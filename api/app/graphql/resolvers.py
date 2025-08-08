from typing import List, Optional
from datetime import date

import strawberry
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from kokkai_db.schema import Meeting as DBMeeting, Speech as DBSpeech
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
                create_time=s.create_time,
                update_time=s.update_time,
                speech_url=s.speech_url,
            )
            for s in speeches
        ]

    @strawberry.field
    async def summary(self, info) -> Optional[Summary]:
        dataloaders: DataLoaders = info.context["dataloaders"]
        summary = await dataloaders.latest_summaries_by_issue_id.load(self.issue_id)
        return Summary(**summary.__dict__) if summary else None

    @strawberry.field
    async def session_info(self, info) -> Optional[Session]:
        dataloaders: DataLoaders = info.context["dataloaders"]
        session_info = await dataloaders.sessions_by_session_number.load(self.session)
        return Session(**session_info.__dict__) if session_info else None


@strawberry.type
class Query:
    @strawberry.field
    async def meetings(self, info, issue_id: Optional[str] = None) -> List[Meeting]:
        session: AsyncSession = info.context["session"]
        if issue_id:
            db_meetings = (await session.execute(select(DBMeeting).where(DBMeeting.issue_id == issue_id))).scalars().all()
        else:
            db_meetings = (await session.execute(select(DBMeeting))).scalars().all()
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
            db_speeches = (await session.execute(select(DBSpeech).where(DBSpeech.speech_id == speech_id))).scalars().all()
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
                create_time=s.create_time,
                update_time=s.update_time,
                speech_url=s.speech_url,
            )
            for s in db_speeches
        ]
