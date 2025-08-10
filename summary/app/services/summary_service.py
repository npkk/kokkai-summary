import os
from datetime import datetime
from typing import List

from google.genai.types import GenerateContentResponse
from kokkai_db.schema import Meeting, Speech, Summary
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import MODEL
from app.services.gemini_api import GeminiAPIClient
from app.utils.text_processing import clean_summary_text


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
        print(f"An error occurred during DB operation in make_text: {e}")
        raise

async def make_summary(issue_id: str, db: Session):
    """
    要約を作成し、DBに保存する
    """
    try:
        text = make_text(issue_id, db)
        # textを一時ファイルに保存する
        # tmpディレクトリが存在しない場合は作成
        os.makedirs("tmp", exist_ok=True)
        temp_file_path = "tmp/temp.txt"
        with open(temp_file_path, "w") as f:
            f.write(text)

        gemini_client = GeminiAPIClient()
        response = await gemini_client.generate_content_from_file(temp_file_path)

        create_summary_record(issue_id, db, response)
    except Exception as e:
        print(f"An error occurred during summary creation: {e}")
        raise

def create_summary_record(issue_id: str, db: Session, response: GenerateContentResponse):
    """
    生成された要約をDBに保存する
    """
    # response.textがNoneの場合を考慮
    summary_text_from_response = response.text if response.text is not None else ""
    cleaned_summary = clean_summary_text(summary_text_from_response)
    
    now = datetime.now() # 現在のタイムスタンプを取得

    new_summary = Summary(
        issue_id=issue_id,
        summary=cleaned_summary,
        model=MODEL, # app.configからインポートしたMODELを使用
        create_time=now, # datetimeオブジェクトを渡す
        update_time=now, # datetimeオブジェクトを渡す
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
        print(f"An error occurred during DB operation in get_summaries: {e}")
        raise
