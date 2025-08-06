import os
from typing import List

from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError
from google.genai.types import GenerateContentResponse
from kokkai_db.schema import Meeting, Speech, Summary
from pytimeparse import parse
from sqlalchemy import select
from sqlalchemy.orm import Session
from tenacity import (
    RetryCallState,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_combine,
    wait_exponential,
)
from tenacity.wait import wait_base

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

MODEL = "gemini-2.5-flash"

PROMPT = """
下記要約テンプレートに従って要約してください。

## 要約テンプレート

```markdown
# 国会会議録要約

## 会議名

（ここに会議名を記述）

## 決議された事項

* （決議事項1）
* （決議事項2）
* ...

## 議論となった事項

（ここから下に、全ての質疑応答の要約を繰り返す）

---

### 【質疑のテーマ】（ここにテーマを記述）

**質疑者:** （氏名） 分科員（所属）
**答弁者:** （氏名） 政府参考人（役職など）

**【質疑の要点】**

*   （質疑のポイント1）
*   （質疑のポイント2）
*   ...

**【答弁の要点】**

*   （答弁のポイント1）
*   （答弁のポイント2）
*   ...

**【議論の結論】**

（議論が平行線で終わったのか、何らかの合意や進展があったのかなど、議論の結果を簡潔に記述）

---

### 【質疑のテーマ】（次のテーマ）

...（同様の構造を繰り返す）...
```
"""


def make_text(issue_id: str, db: Session) -> str:
    """
    会議内の全発言からspeechを取得し発言順に連結する
    """
    try:
        stmt_meeting = select(Meeting).where(Meeting.issue_id == issue_id)
        meeting = db.execute(stmt_meeting).scalar_one_or_none()

        if not meeting:
            print(f"Meeting with issue_id {issue_id} not found.")
            raise Exception

        stmt_speeches = (
            select(Speech.speech)
            .where(Speech.issue_id == issue_id)
            .order_by(Speech.speech_order)
        )
        speeches = db.execute(stmt_speeches).scalars().all()
        return "\n".join([s for s in speeches if s is not None])

    except Exception as e:
        print(f"An error occurred during DB operation: {e}")
        raise


def _is_retriable(e: BaseException) -> bool:
    return isinstance(e, APIError) and e.code in [503, 429]


def _calc_retry_delay(exception: BaseException | None) -> float:
    if exception is None:
        return 60
    if isinstance(exception, APIError) and exception.code == 503:
        return 60
    if isinstance(exception, APIError) and exception.code == 429:
        try:
            retry_delay = parse(
                [
                    rd
                    for d in exception.details["error"]["details"]
                    if (rd := d.get("retryDelay"))
                ][0]
            )
            if retry_delay:
                return retry_delay + 5
        except (IndexError, KeyError):
            # retryDelayが取得できない場合はデフォルト値にフォールバック
            return 60
    return 60


class wait_from_exception(wait_base):
    def __init__(self):
        pass

    def __call__(self, retry_state: "RetryCallState") -> float:
        if retry_state.outcome is None:
            return 0
        exception = retry_state.outcome.exception()
        return _calc_retry_delay(exception)


@retry(
    wait=wait_combine(
        wait_from_exception(), wait_exponential(multiplier=2, min=10, max=300)
    ),
    retry=retry_if_exception(_is_retriable),
    stop=stop_after_attempt(10),
)
async def make_summary(issue_id: str, db: Session):
    """
    要約を作成し、DBに保存する
    """
    try:
        text = make_text(issue_id, db)
        # textを一時ファイルに保存する
        with open("tmp/temp.txt", "w") as f:
            f.write(text)

        client = genai.Client(api_key=GEMINI_API_KEY)

        file = await client.aio.files.upload(file="tmp/temp.txt")
        response = await client.aio.models.generate_content(
            model=MODEL, contents=[PROMPT, file]
        )

        create_summary(issue_id, db, response)
    except APIError as e:
        if _is_retriable(e):
            print(f"APIError occurred: {e.code}, retrying...")
        raise
    except Exception as e:
        print(f"An error occurred during DB operation: {e}")
        raise


def create_summary(issue_id: str, db: Session, response: GenerateContentResponse):
    new_summary = Summary(
        issue_id=issue_id,
        summary=response.text,
        model=MODEL,
        create_time=response.create_time,
        update_time=response.create_time,
    )

    db.add(new_summary)
    print(f"Staged for commit: Summary with issueID {issue_id}")


def get_summaries(issue_id: str, db: Session) -> List[Summary]:
    """
    要約を取得する
    """

    try:
        summaries = (
            db.query(Summary)
            .filter(Summary.issue_id == issue_id)
            .order_by(Summary.create_time.desc())
            .all()
        )
        return summaries

    except Exception as e:
        print(f"An error occurred during DB operation: {e}")
        raise
