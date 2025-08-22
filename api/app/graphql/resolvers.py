from typing import List, Optional
from datetime import date

import strawberry
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, distinct

from kokkai_db.schema import Meeting as DBMeeting, Speech as DBSpeech, Session as DBSession, Summary as DBSummary
from .dataloaders import DataLoaders


@strawberry.type
class Session:
    session: int
    name: str
    start_date: date
    end_date: date

@strawberry.type
class Speech:
    speech_id: str
    speech_order: int
    speaker: Optional[str]
    speaker_yomi: Optional[str]
    speaker_group: Optional[str]
    speaker_position: Optional[str]
    speaker_role: Optional[str]
    speech: Optional[str]
    start_page: Optional[int]
    create_time: Optional[str]
    update_time: Optional[str]
    speech_url: str

@strawberry.type
class Summary:
    summary: Optional[str]
    model: Optional[str]
    create_time: Optional[str]
    update_time: Optional[str]

@strawberry.type
class Meeting:
    issue_id: str
    image_kind: str
    search_object: int
    session: int
    name_of_house: str
    name_of_meeting: Optional[str]
    issue: str
    date: Optional[date]
    closing: Optional[str]
    meeting_url: str
    pdf_url: Optional[str]

    @strawberry.field
    async def speeches(self, info, speech_id: Optional[str] = None) -> List[Speech]:
        dataloaders: DataLoaders = info.context["dataloaders"]
        speeches = await dataloaders.speeches_by_issue_id.load(self.issue_id)
        if speech_id:
            return [Speech(**s.__dict__) for s in speeches if s.speech_id == speech_id]
        return [
            Speech(
                speech_id=s.speech_id,
                speech_order=s.speech_order,
                speaker=s.speaker,
                speaker_yomi=s.speaker_yomi,
                speaker_group=s.speaker_group,
                speaker_position=s.speaker_position,
                speaker_role=s.speaker_role,
                speech=s.speech,
                start_page=s.start_page,
                create_time=s.create_time.isoformat() if s.create_time else None,
                update_time=s.update_time.isoformat() if s.update_time else None,
                speech_url=s.speech_url,
            )
            for s in speeches
        ]

    @strawberry.field
    async def summary(self, info) -> Optional[Summary]:
        dataloaders: DataLoaders = info.context["dataloaders"]
        summary: Optional[DBSummary] = await dataloaders.latest_summaries_by_issue_id.load(self.issue_id)
        if summary:
            return Summary(
                summary=summary.summary,
                model=summary.model,
                create_time=summary.create_time.isoformat() if summary.create_time else None,
                update_time=summary.update_time.isoformat() if summary.update_time else None,
            )
        return None

    @strawberry.field
    async def session_info(self, info) -> Optional[Session]:
        dataloaders: DataLoaders = info.context["dataloaders"]
        session_info: Optional[DBSession] = await dataloaders.sessions_by_session_number.load(self.session)
        if session_info:
            return Session(
                session=session_info.session,
                name=session_info.name,
                start_date=session_info.start_date,
                end_date=session_info.end_date,
            )
        return None


@strawberry.type
class Query:
    @strawberry.field
    async def meetings(
        self,
        info,
        session: Optional[int] = None,
        issue_id: Optional[str] = None,
        name_of_house: Optional[str] = None,
        name_of_meeting: Optional[str] = None,
        has_summary: Optional[bool] = False,
    ) -> List[Meeting]:
        db_session: AsyncSession = info.context["session"]

        if not session and not issue_id:
            raise ValueError("Either 'session' or 'issue_id' must be provided.")

        conditions = []
        if session:
            conditions.append(DBMeeting.session == session)
        if issue_id:
            conditions.append(DBMeeting.issue_id == issue_id)
        if name_of_house:
            conditions.append(DBMeeting.name_of_house == name_of_house)
        if name_of_meeting:
            conditions.append(DBMeeting.name_of_meeting == name_of_meeting)

        query = select(DBMeeting)
        if has_summary:
            query = query.join(DBSummary, DBMeeting.issue_id == DBSummary.issue_id)

        db_meetings = (
            (await db_session.execute(query.where(and_(*conditions)))).scalars().all()
        )
        return [
            Meeting(
                issue_id=m.issue_id,
                image_kind=m.image_kind,
                search_object=m.search_object,
                session=m.session,
                name_of_house=m.name_of_house,
                name_of_meeting=m.name_of_meeting,
                issue=m.issue,
                date=m.date,
                closing=m.closing,
                meeting_url=m.meeting_url,
                pdf_url=m.pdf_url,
            )
            for m in db_meetings
        ]

    @strawberry.field
    async def speeches(self, info, speech_id: Optional[str] = None) -> List[Speech]:
        session: AsyncSession = info.context["session"]
        if speech_id:
            db_speeches = (
                (
                    await session.execute(
                        select(DBSpeech).where(DBSpeech.speech_id == speech_id)
                    )
                )
                .scalars()
                .all()
            )
        else:
            db_speeches = (await session.execute(select(DBSpeech))).scalars().all()
        return [
            Speech(
                speech_id=s.speech_id,
                speech_order=s.speech_order,
                speaker=s.speaker,
                speaker_yomi=s.speaker_yomi,
                speaker_group=s.speaker_group,
                speaker_position=s.speaker_position,
                speaker_role=s.speaker_role,
                speech=s.speech,
                start_page=s.start_page,
                create_time=s.create_time.isoformat() if s.create_time else None,
                update_time=s.update_time.isoformat() if s.update_time else None,
                speech_url=s.speech_url,
            )
            for s in db_speeches
        ]

    @strawberry.field
    async def sessions(self, info) -> List[Session]:
        db_session: AsyncSession = info.context["session"]
        db_sessions = (await db_session.execute(select(DBSession))).scalars().all()
        return [
            Session(
                session=s.session,
                name=s.name,
                start_date=s.start_date,
                end_date=s.end_date,
            )
            for s in db_sessions
        ]

    @strawberry.field
    async def meeting_names(self, info, session: int) -> List[str]:
        db_session: AsyncSession = info.context["session"]
        db_meeting_names = (
            (
                await db_session.execute(
                    select(distinct(DBMeeting.name_of_meeting)).where(
                        DBMeeting.session == session
                    )
                )
            )
            .scalars()
            .all()
        )
        return [name for name in db_meeting_names if name]
