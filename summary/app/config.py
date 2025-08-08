import os

from dotenv import load_dotenv

load_dotenv()

_gemini_api_key = os.environ.get("GEMINI_API_KEY")
if _gemini_api_key is None:
    raise ValueError("GEMINI_API_KEY environment variable not set.")
GEMINI_API_KEY: str = _gemini_api_key

MODEL: str = "gemini-2.5-flash"

PROMPT: str = """
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

_database_url = os.environ.get("DATABASE_URL")
if _database_url is None:
    raise ValueError("DATABASE_URL environment variable not set.")
DATABASE_URL: str = _database_url

# API呼び出し制限関連の定数
BATCH_SIZE: int = 1