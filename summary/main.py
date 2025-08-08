import asyncio
import time
from datetime import datetime

from kokkai_db.schema import Meeting, Speech, Summary
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import BATCH_SIZE
from app.db.session import SessionLocal  # get_db_sessionではなくSessionLocalを直接使用
from app.services.summary_service import make_summary  # make_summaryをインポート


async def run_summary_job():
    print(f"[{datetime.now()}] Starting summary job...")
    db: Session = SessionLocal() # SessionLocalを直接呼び出す
    try:
        # 既に要約済みのissue_idを取得
        summarized_issue_ids = {
            s.issue_id for s in db.query(Summary.issue_id).distinct().all()
        }

        # 未要約の会議録を回次最新順、文字数が多い順に取得
        meetings_to_summarize = (
            db.query(Meeting)
            .join(Speech, Meeting.issue_id == Speech.issue_id)
            .filter(Meeting.issue_id.notin_(summarized_issue_ids))
            .group_by(Meeting.issue_id)
            .order_by(
                Meeting.session.desc(),
                func.sum(func.length(Speech.speech)).desc()
            )
            .limit(BATCH_SIZE)
            .all()
        )

        if not meetings_to_summarize:
            print("No new meetings to summarize.")
            return

        for meeting in meetings_to_summarize:
            issue_id = meeting.issue_id
            print(f"Summarizing issue_id: {issue_id}")
            await make_summary(issue_id, db)
            db.commit()
            print(f"Successfully summarized issue_id: {issue_id}")
            time.sleep(5) # API呼び出し間の遅延

    except Exception as e:
        db.rollback()
        print(f"An error occurred during summary job: {e}")
    finally:
        db.close()
    print(f"[{datetime.now()}] Summary job finished.")

if __name__ == "__main__":
    asyncio.run(run_summary_job())