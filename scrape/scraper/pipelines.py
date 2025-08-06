from datetime import datetime

from itemadapter import ItemAdapter
from kokkai_db.database import SessionLocal
from kokkai_db.schema import Meeting, Session, Speech
from sqlalchemy.orm import Session as DbSession


class DatabasePipeline:
    def open_spider(self, spider):
        self.session: DbSession = SessionLocal()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if spider.name == 'meetings_spider':
            self._process_meeting_item(adapter, spider)
        elif spider.name == 'sessions_spider':
            self._process_session_item(adapter, spider)
        
        return item

    def _process_meeting_item(self, adapter, spider):
        # 既に同じ会議録IDが存在するかチェック
        existing_meeting = (
            self.session.query(Meeting)
            .filter(Meeting.issue_id == adapter["issueID"])
            .first()
        )
        if existing_meeting:
            spider.logger.info(f"Skipping: Meeting with issueID {adapter['issueID']} already exists.")
            return

        # Meetingオブジェクトを作成
        _date = (
            datetime.strptime(adapter["date"], "%Y-%m-%d").date()
            if adapter.get("date")
            else None
        )

        new_meeting = Meeting(
            issue_id=adapter.get("issueID"),
            image_kind=adapter.get("imageKind"),
            search_object=adapter.get("searchObject"),
            session=adapter.get("session"),
            name_of_house=adapter.get("nameOfHouse"),
            name_of_meeting=adapter.get("nameOfMeeting"),
            issue=adapter.get("issue"),
            date=_date,
            closing=adapter.get("closing"),
            meeting_url=adapter.get("meetingURL"),
            pdf_url=adapter.get("pdfURL"),
        )

        # 関連するSpeechオブジェクトを作成し、Meetingに追加
        for speech_item in adapter.get("speechRecord", []):
            speech_adapter = ItemAdapter(speech_item)
            new_speech = Speech(
                speech_id=speech_adapter.get("speechID"),
                speech_order=speech_adapter.get("speechOrder"),
                speaker=speech_adapter.get("speaker"),
                speaker_yomi=speech_adapter.get("speakerYomi"),
                speaker_group=speech_adapter.get("speakerGroup"),
                speaker_position=speech_adapter.get("speakerPosition"),
                speaker_role=speech_adapter.get("speakerRole"),
                speech=speech_adapter.get("speech"),
                start_page=speech_adapter.get("startPage"),
                create_time=speech_adapter.get("createTime"),
                update_time=speech_adapter.get("updateTime"),
                speech_url=speech_adapter.get("speechURL"),
            )
            new_meeting.speeches.append(new_speech)

        try:
            self.session.add(new_meeting)
            self.session.commit()
            spider.logger.info(f"Committed: Meeting with issueID {adapter['issueID']}")
        except Exception as e:
            spider.logger.error(f"Database commit failed for issueID {adapter['issueID']}: {e}")
            self.session.rollback()
            raise

    def _process_session_item(self, adapter, spider):
        # 既存のセッションを検索
        existing_session = (
            self.session.query(Session)
            .filter(Session.session == adapter["session"])
            .first()
        )

        if existing_session:
            # レコードが存在する場合は更新
            existing_session.name = adapter.get("name")
            existing_session.start_date = adapter.get("start_date")
            existing_session.end_date = adapter.get("end_date")
            spider.logger.info(f"Updated: Session {adapter['session']}")
        else:
            # レコードが存在しない場合は新規作成
            new_session = Session(
                session=adapter.get("session"),
                name=adapter.get("name"),
                start_date=adapter.get("start_date"),
                end_date=adapter.get("end_date"),
            )
            self.session.add(new_session)
            spider.logger.info(f"Staged for commit: Session {adapter['session']}")

        try:
            self.session.commit()
        except Exception as e:
            spider.logger.error(f"Database commit failed for session {adapter['session']}: {e}")
            self.session.rollback()
            raise
