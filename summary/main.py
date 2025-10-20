import asyncio
import time
from datetime import datetime

from kokkai_db.schema import Meeting, Speech, Summary
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import BATCH_SIZE, PROMPT_VERSION
from app.db.session import SessionLocal
from app.services.summary_service import make_summary


async def run_summary_job():
    print(f"[{datetime.now()}] Starting summary job...")
    db: AsyncSession = SessionLocal()
    try:
        db.begin()
        # 未要約または古いバージョンの要約を持つ会議録を取得
        stmt = (
            select(Meeting, func.max(Summary.prompt_version).label("max_version"))
            .join(Speech, Meeting.issue_id == Speech.issue_id)
            .outerjoin(Summary, Meeting.issue_id == Summary.issue_id)
            .where(Meeting.image_kind == "会議録")
            .group_by(Meeting.issue_id)
            .having(func.coalesce(func.max(Summary.prompt_version), 0) < PROMPT_VERSION)
            .order_by(
                func.coalesce(func.max(Summary.prompt_version), 0).asc(),
                Meeting.session.desc(),
                func.sum(func.length(Speech.speech)).desc(),
            )
            .limit(BATCH_SIZE)
        )
        meetings_to_summarize = (await db.execute(stmt)).all()

        if not meetings_to_summarize:
            print("No new meetings to summarize.")
            return

        for meeting in meetings_to_summarize:
            issue_id = meeting.issue_id
            print(f"Summarizing issue_id: {issue_id}")
            await make_summary(issue_id, db)
            await db.commit()
            print(f"Successfully summarized issue_id: {issue_id}")
            time.sleep(60)  # API呼び出し間の遅延

    except Exception as e:
        await db.rollback()
        print(f"An error occurred during summary job: {e}")
    finally:
        await db.close()
    print(f"[{datetime.now()}] Summary job finished.")


if __name__ == "__main__":
    asyncio.run(run_summary_job())
