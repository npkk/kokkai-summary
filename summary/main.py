import argparse
import asyncio

from kokkai_db.database import SessionLocal, create_tables
from kokkai_db.schema import Meeting
from sqlalchemy import select

from src.summary import get_summaries, make_summary


async def main():
    """
    コマンドライン引数で指定された国会回次の会議録の要約を作成し、
    データベースに保存するメイン処理。
    """
    parser = argparse.ArgumentParser(
        description="指定された回次の会議録の要約を作成し、DBに保存します。"
    )
    parser.add_argument(
        "--session", type=int, required=True, help="要約を作成する国会の回次"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="既存の要約をスキップする",
    )
    args = parser.parse_args()

    print(f"--- Start: Summarize session {args.session} ---")
    create_tables()
    db = SessionLocal()
    try:
        # 指定された回次に該当する会議のIssueIDを取得
        stmt = (
            select(Meeting.issue_id)
            .where(Meeting.session == args.session)
            .where(Meeting.image_kind == "会議録")
        )
        issue_ids = db.execute(stmt).scalars().all()

        if not issue_ids:
            print(f"No meetings found for session {args.session}.")
            return

        print(f"Found {len(issue_ids)} meetings for session {args.session}.")

        # 各会議録について要約を作成
        for issue_id in issue_ids:
            print(f"Processing: {issue_id}")
            try:
                summaries = get_summaries(issue_id, db)
                if summaries and args.skip_existing:
                    print(f"  - Skip: Summary already exists for {issue_id}.")
                    continue
                await make_summary(issue_id, db)
                db.commit()
                print(f"  - Success: Saved summary for {issue_id}.")

            except Exception as e:
                print(f"  - Error processing {issue_id}: {e}")
                db.rollback()
                break

    finally:
        db.close()

    print(f"--- Finish: Summarize session {args.session} ---")


if __name__ == "__main__":
    asyncio.run(main())
