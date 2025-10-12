from typing import List, Optional
from datetime import date

import strawberry
from strawberry.types import Info
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, distinct, func
from sqlalchemy.orm import aliased

from kokkai_db.schema import (
    Meeting as DBMeeting,
    Speech as DBSpeech,
    Session as DBSession,
    Summary as DBSummary,
)
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
    prompt_version: Optional[int]
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
        """
        Meetingに紐づくSpeechを取得する
        現在呼び出していない
        """
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

    summary: Optional[Summary]

    @strawberry.field
    async def session_info(self, info) -> Optional[Session]:
        """
        Meetingに紐づくSessionを取得する
        現在呼び出していない
        """
        dataloaders: DataLoaders = info.context["dataloaders"]
        session_info: Optional[
            DBSession
        ] = await dataloaders.sessions_by_session_number.load(self.session)
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
        info: Info,
        session: Optional[int] = None,
        issue_id: Optional[str] = None,
        name_of_house: Optional[str] = None,
        name_of_meeting: Optional[str] = None,
        has_summary: Optional[bool] = False,
    ) -> List[Meeting]:
        db_session: AsyncSession = info.context["session"]

        if not session and not issue_id:
            raise ValueError("Either 'session' or 'issue_id' must be provided.")

        try:
            conditions = []
            if session:
                conditions.append(DBMeeting.session == session)
            if issue_id:
                conditions.append(DBMeeting.issue_id == issue_id)
            if name_of_house:
                conditions.append(DBMeeting.name_of_house == name_of_house)
            if name_of_meeting:
                conditions.append(DBMeeting.name_of_meeting == name_of_meeting)
            if has_summary:
                conditions.append(DBSummary.issue_id is not None)

            subquery = (
                select(
                    DBMeeting,
                    DBSummary,
                    func.row_number()
                    .over(
                        partition_by=DBMeeting.issue_id,
                        order_by=(
                            DBSummary.prompt_version.desc(),
                            DBSummary.update_time.desc(),
                        ),
                    )
                    .label("rn"),
                )
                .select_from(DBMeeting)
                .outerjoin(DBSummary, DBMeeting.issue_id == DBSummary.issue_id)
                .where(and_(*conditions))
                .subquery()
            )

            MeetingAlias = aliased(DBMeeting, subquery)
            SummaryAlias = aliased(DBSummary, subquery)

            query = (
                select(MeetingAlias, SummaryAlias)
                .where(subquery.c.rn == 1)
                .order_by(subquery.c.issue_id)
            )

            results = (await db_session.execute(query)).all()

            meetings = []
            for meeting_obj, summary_obj in results:
                summary_dto = None
                if summary_obj and summary_obj.issue_id:
                    summary_dto = Summary(
                        summary=summary_obj.summary,
                        model=summary_obj.model,
                        prompt_version=summary_obj.prompt_version,
                        create_time=summary_obj.create_time.isoformat()
                        if summary_obj.create_time
                        else None,
                        update_time=summary_obj.update_time.isoformat()
                        if summary_obj.update_time
                        else None,
                    )

                meetings.append(
                    Meeting(
                        issue_id=meeting_obj.issue_id,
                        image_kind=meeting_obj.image_kind,
                        search_object=meeting_obj.search_object,
                        session=meeting_obj.session,
                        name_of_house=meeting_obj.name_of_house,
                        name_of_meeting=meeting_obj.name_of_meeting,
                        issue=meeting_obj.issue,
                        date=meeting_obj.date,
                        closing=meeting_obj.closing,
                        meeting_url=meeting_obj.meeting_url,
                        pdf_url=meeting_obj.pdf_url,
                        summary=summary_dto,
                    )
                )
            return meetings
        except Exception as e:
            await db_session.rollback()
            print(e)
            raise

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
