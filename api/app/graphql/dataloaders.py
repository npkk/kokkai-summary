from typing import List, Optional
from collections import defaultdict

from strawberry.dataloader import DataLoader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from kokkai_db.schema import Meeting, Speech, Summary, Session


async def load_meetings_by_issue_ids(
    session: AsyncSession, issue_ids: List[str]
) -> List[List[Optional[Meeting]]]:
    meetings = await session.execute(
        select(Meeting).where(Meeting.issue_id.in_(issue_ids))
    )
    meetings_by_id = {meeting.issue_id: meeting for meeting in meetings.scalars().all()}
    return [[meetings_by_id.get(issue_id)] for issue_id in issue_ids]


async def load_speeches_by_issue_ids(
    session: AsyncSession, issue_ids: List[str]
) -> List[List[Speech]]:
    speeches = await session.execute(
        select(Speech).where(Speech.issue_id.in_(issue_ids))
    )
    speeches_by_issue_id = defaultdict(list)
    for speech in speeches.scalars().all():
        speeches_by_issue_id[speech.issue_id].append(speech)
    return [speeches_by_issue_id[issue_id] for issue_id in issue_ids]


async def load_latest_summaries_by_issue_ids(
    session: AsyncSession, issue_ids: List[str]
) -> List[Optional[Summary]]:
    stmt = (
        select(
            Summary,
            func.row_number()
            .over(
                partition_by=Summary.issue_id,
                order_by=(Summary.update_time.desc(), Summary.prompt_version.desc()),
            )
            .label("rn"),
        )
        .where(Summary.issue_id.in_(issue_ids))
        .subquery()
    )

    summaries = await session.execute(select(Summary).where(stmt.c.rn == 1))

    summaries_by_issue_id = {
        summary.issue_id: summary for summary in summaries.scalars().all()
    }
    return [summaries_by_issue_id.get(issue_id) for issue_id in issue_ids]


async def load_sessions_by_session_numbers(
    session: AsyncSession, session_numbers: List[int]
) -> List[Optional[Session]]:
    sessions = await session.execute(
        select(Session)
        .where(Session.session.in_(session_numbers))
        .order_by(Session.session)
    )
    sessions_by_number = {s.session: s for s in sessions.scalars().all()}
    return [
        sessions_by_number.get(session_number) for session_number in session_numbers
    ]


class DataLoaders:
    def __init__(self, session: AsyncSession):
        async def _load_meetings(keys: List[str]):
            return await load_meetings_by_issue_ids(session, keys)

        async def _load_speeches(keys: List[str]):
            return await load_speeches_by_issue_ids(session, keys)

        async def _load_summaries(keys: List[str]):
            return await load_latest_summaries_by_issue_ids(session, keys)

        async def _load_sessions(keys: List[int]):
            return await load_sessions_by_session_numbers(session, keys)

        self.meetings_by_issue_id = DataLoader(_load_meetings)
        self.speeches_by_issue_id = DataLoader(_load_speeches)
        self.latest_summaries_by_issue_id = DataLoader(_load_summaries)
        self.sessions_by_session_number = DataLoader(_load_sessions)
