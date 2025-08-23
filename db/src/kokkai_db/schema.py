from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Meeting(Base):
    """
    会議
    """

    __tablename__ = "meetings"

    issue_id: Mapped[str] = mapped_column(
        String, primary_key=True, unique=True, nullable=False
    )
    image_kind: Mapped[str] = mapped_column(String, nullable=False)
    search_object: Mapped[int] = mapped_column(Integer, nullable=False)
    session: Mapped[int] = mapped_column(Integer, nullable=False)
    name_of_house: Mapped[str] = mapped_column(String, nullable=False)
    name_of_meeting: Mapped[str | None] = mapped_column(String, nullable=True)
    issue: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[date | None] = mapped_column(Date, nullable=True)
    closing: Mapped[str | None] = mapped_column(String, nullable=True)
    meeting_url: Mapped[str] = mapped_column(String, nullable=False)
    pdf_url: Mapped[str | None] = mapped_column(String, nullable=True)

    speeches: Mapped[list[Speech]] = relationship("Speech", back_populates="meeting")


class Speech(Base):
    """
    発言
    """

    __tablename__ = "speeches"

    issue_id: Mapped[str] = mapped_column(
        String, ForeignKey("meetings.issue_id"), nullable=False
    )
    speech_id: Mapped[str] = mapped_column(
        String, primary_key=True, unique=True, nullable=False
    )
    speech_order: Mapped[int] = mapped_column(Integer, nullable=False)
    speaker: Mapped[str | None] = mapped_column(String)
    speaker_yomi: Mapped[str | None] = mapped_column(String)
    speaker_group: Mapped[str | None] = mapped_column(String)
    speaker_position: Mapped[str | None] = mapped_column(String)
    speaker_role: Mapped[str | None] = mapped_column(String)
    speech: Mapped[str | None] = mapped_column(Text)
    start_page: Mapped[int | None] = mapped_column(Integer)
    create_time: Mapped[datetime | None] = mapped_column(DateTime)
    update_time: Mapped[datetime | None] = mapped_column(DateTime)
    speech_url: Mapped[str] = mapped_column(String, nullable=False)

    meeting: Mapped[Meeting] = relationship("Meeting", back_populates="speeches")


class Summary(Base):
    """
    会議ごとの要約
    """

    __tablename__ = "summaries"

    issue_id: Mapped[str] = mapped_column(
        String, ForeignKey("meetings.issue_id"), primary_key=True, nullable=False
    )
    summary: Mapped[str | None] = mapped_column(Text)
    model: Mapped[str | None] = mapped_column(String, primary_key=True)
    prompt_version: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    create_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    update_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class Session(Base):
    """
    国会回次のマスタ
    """

    __tablename__ = "sessions"

    session: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
