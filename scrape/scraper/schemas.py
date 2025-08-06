import re
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

# --- Request Schemas ---


class NameOfHouse(str, Enum):
    """院名"""

    SHUGIIN = "衆議院"
    SANGIIN = "参議院"
    RYOIN = "両院"


class RecordPacking(str, Enum):
    """応答形式"""

    XML = "xml"
    JSON = "json"


class SearchRange(str, Enum):
    """検索範囲"""

    HEADER = "冒頭"
    BODY = "本文"
    ALL = "冒頭・本文"


class SpeechRequestParams(BaseModel):
    """
    国会会議録検索APIへのリクエストパラメータを定義するスキーマ。
    https://kokkai.ndl.go.jp/api.html
    """

    startRecord: Optional[int] = Field(1, ge=1, description="取得開始位置 (1以上)")
    maximumRecords: Optional[int] = Field(
        10, ge=1, le=100, description="最大取得件数 (1-100)"
    )
    nameOfHouse: Optional[NameOfHouse] = Field(None, description="院名")
    nameOfMeeting: Optional[str] = Field(None, description="会議名")
    any: Optional[str] = Field(None, description="任意のキーワード")
    speaker: Optional[str] = Field(None, description="発言者名")
    from_: Optional[str] = Field(
        None, alias="from", description="発言日付（開始） YYYY-MM-DD形式"
    )
    until: Optional[str] = Field(None, description="発言日付（終了） YYYY-MM-DD形式")
    supplementAndAppendix: Optional[bool] = Field(
        None, description="検索対象を追録・附録に限定するか"
    )
    contentsAndIndex: Optional[bool] = Field(
        None, description="検索対象を本文・索引に限定するか"
    )
    searchRange: Optional[SearchRange] = Field(None, description="議事冒頭・本文指定")
    closing: Optional[bool] = Field(None, description="閉会中指定")
    speechNumber: Optional[int] = Field(None, description="発言番号")
    speakerPosition: Optional[str] = Field(None, description="発言者肩書き")
    speakerGroup: Optional[str] = Field(None, description="発言者所属会派")
    speakerRole: Optional[str] = Field(None, description="発言者役割")
    speechID: Optional[str] = Field(None, description="発言ID")
    issueID: Optional[str] = Field(None, description="会議録ID")
    issueFrom: Optional[int] = Field(None, ge=0, le=999, description="号数From")
    issueTo: Optional[int] = Field(None, ge=0, le=999, description="号数To")
    sessionFrom: Optional[int] = Field(None, ge=1, description="国会回次From")
    sessionTo: Optional[int] = Field(None, ge=1, description="国会回次From")
    recordPacking: RecordPacking = Field(RecordPacking.JSON, description="応答形式")

    @field_validator("from_", "until")
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("日付はYYYY-MM-DD形式で指定してください")
        return v

    model_config = ConfigDict(use_enum_values=True)


# --- Response Schemas ---


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
