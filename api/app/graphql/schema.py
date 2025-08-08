import strawberry
from typing import List, Optional
from datetime import date

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

    speeches: List[Speech]
    summary: Optional[Summary]
    session_info: Optional[Session]

@strawberry.type
class Query:
    meetings: List[Meeting]
    speeches: List[Speech]