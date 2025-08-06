from typing import List, Optional

from pydantic import BaseModel, Field


class SpeechRecord(BaseModel):
    speechID: str = Field(..., description="発言ID")
    speechOrder: int = Field(..., description="発言番号")
    speaker: Optional[str] = Field(None, description="発言者名")
    speakerYomi: Optional[str] = Field(None, description="発言者よみ")
    speakerGroup: Optional[str] = Field(None, description="発言者所属会派")
    speakerPosition: Optional[str] = Field(None, description="発言者肩書き")
    speakerRole: Optional[str] = Field(None, description="発言者役割")
    speech: Optional[str] = Field(None, description="発言")
    startPage: Optional[int] = Field(None, description="発言が掲載されている開始ページ")
    createTime: Optional[str] = Field(None, description="レコード登録日時")
    updateTime: Optional[str] = Field(None, description="レコード更新日時")
    speechURL: str = Field(..., description="発言URL")


class MeetingRecord(BaseModel):
    issueID: str = Field(..., description="会議録ID")
    imageKind: str = Field(..., description="イメージ種別")
    searchObject: int = Field(..., description="検索対象箇所")
    session: int = Field(..., description="国会回次")
    nameOfHouse: str = Field(..., description="院名")
    nameOfMeeting: Optional[str] = Field(..., description="会議名")
    issue: str = Field(..., description="号数")
    date: Optional[str] = Field(..., description="開催日付")
    closing: Optional[str] = Field(..., description="閉会中フラグ")
    speechRecord: List[SpeechRecord] = Field(..., description="発言リスト")
    meetingURL: str = Field(..., description="会議録テキスト表示画面のURL")
    pdfURL: Optional[str] = Field(None, description="会議録PDF表示画面のURL")


class NdlApiResponse(BaseModel):
    numberOfRecords: int = Field(..., description="総結果件数")
    numberOfReturn: int = Field(..., description="返戻件数")
    startRecord: int = Field(..., description="開始位置")
    nextRecordPosition: Optional[int] = Field(None, description="次開始位置")
    meetingRecord: List[MeetingRecord] = Field(..., description="会議録リスト")
