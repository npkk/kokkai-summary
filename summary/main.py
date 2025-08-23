import asyncio
import time
from datetime import datetime

from kokkai_db.schema import Meeting, Speech, Summary
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import BATCH_SIZE, PROMPT_VERSION
from app.db.session import SessionLocal
from app.services.summary_service import make_summary


async def run_summary_job():
    print(f"[{datetime.now()}] Starting summary job...")
    db: Session = SessionLocal()
    try:
        # 優先1: 未要約の会議録を取得
        meetings_to_summarize = (
            db.query(Meeting)
            .outerjoin(Summary, Meeting.issue_id == Summary.issue_id)
            .join(Speech, Meeting.issue_id == Speech.issue_id)
            .filter(Summary.issue_id.is_(None))
            .group_by(Meeting.issue_id)
            .order_by(
                Meeting.session.desc(),
                func.sum(func.length(Speech.speech)).desc(),
            )
            .limit(BATCH_SIZE)
            .all()
        )

        # 取得した会議録のissue_idをセットに格納
        summarized_issue_ids = {m.issue_id for m in meetings_to_summarize}

        # 優先2: BATCH_SIZEに満たない場合、古いバージョンの要約を持つ会議録を追加
        remaining_limit = BATCH_SIZE - len(meetings_to_summarize)
        if remaining_limit > 0:
            old_version_meetings = (
                db.query(Meeting)
                .join(Summary, Meeting.issue_id == Summary.issue_id)
                .join(Speech, Meeting.issue_id == Speech.issue_id)
                .filter(
                    Summary.prompt_version < PROMPT_VERSION,
                    Meeting.issue_id.notin_(summarized_issue_ids),
                )
                .group_by(Meeting.issue_id)
                .order_by(
                    Meeting.session.desc(),
                    func.sum(func.length(Speech.speech)).desc(),
                )
                .limit(remaining_limit)
                .all()
            )
            meetings_to_summarize.extend(old_version_meetings)

        if not meetings_to_summarize:
            print("No new meetings to summarize.")
            return

        for meeting in meetings_to_summarize:
            issue_id = meeting.issue_id
            print(f"Summarizing issue_id: {issue_id}")
            await make_summary(issue_id, db)
            db.commit()
            print(f"Successfully summarized issue_id: {issue_id}")
            time.sleep(5)  # API呼び出し間の遅延

    except Exception as e:
        db.rollback()
        print(f"An error occurred during summary job: {e}")
    finally:
        db.close()
    print(f"[{datetime.now()}] Summary job finished.")


if __name__ == "__main__":
    asyncio.run(run_summary_job())
