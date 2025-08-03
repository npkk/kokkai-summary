from datetime import datetime
from sqlalchemy.orm import Session

from .db_schema import Meeting, Speech
from .response_schema import NdlApiResponse


def save_response_to_db(db: Session, response: NdlApiResponse):
    """
    APIレスポンスをデータベースに保存します。
    セッションのコミット、ロールバック、クローズは呼び出し元で行う必要があります。

    Args:
        db (Session): SQLAlchemyのセッションオブジェクト。
        response (NdlApiResponse): APIから取得したレスポンスデータ。
    """
    try:
        for meeting_record in response.meetingRecord:
            # 既に同じ会議録IDが存在するかチェック
            existing_meeting = (
                db.query(Meeting)
                .filter(Meeting.issue_id == meeting_record.issueID)
                .first()
            )
            if existing_meeting:
                print(
                    f"Skipping: Meeting with issueID {meeting_record.issueID} already exists."
                )
                continue

            # Meetingオブジェクトを作成
            new_meeting = Meeting(
                issue_id=meeting_record.issueID,
                image_kind=meeting_record.imageKind,
                search_object=meeting_record.searchObject,
                session=meeting_record.session,
                name_of_house=meeting_record.nameOfHouse,
                name_of_meeting=meeting_record.nameOfMeeting,
                issue=meeting_record.issue,
                date=datetime.strptime(meeting_record.date, "%Y-%m-%d").date(),
                closing=meeting_record.closing,
                meeting_url=meeting_record.meetingURL,
                pdf_url=meeting_record.pdfURL,
            )

            # 関連するSpeechオブジェクトを作成し、Meetingに追加
            for speech_record in meeting_record.speechRecord:
                new_speech = Speech(
                    speech_id=speech_record.speechID,
                    speech_order=speech_record.speechOrder,
                    speaker=speech_record.speaker,
                    speaker_yomi=speech_record.speakerYomi,
                    speaker_group=speech_record.speakerGroup,
                    speaker_position=speech_record.speakerPosition,
                    speaker_role=speech_record.speakerRole,
                    speech=speech_record.speech,
                    start_page=speech_record.startPage,
                    create_time=speech_record.createTime,
                    update_time=speech_record.updateTime,
                    speech_url=speech_record.speechURL,
                )
                new_meeting.speeches.append(new_speech)

            # セッションに新しいMeeting（と関連するSpeech）を追加
            db.add(new_meeting)
            print(f"Staged for commit: Meeting with issueID {meeting_record.issueID}")

    except Exception as e:
        print(f"An error occurred during DB operation: {e}")
        raise  # 呼び出し元でロールバックできるように例外を再送出