from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Meeting(Base):
    __tablename__ = "meetings"

    issue_id = Column(String, primary_key=True, unique=True, nullable=False)
    image_kind = Column(String, nullable=False)
    search_object = Column(Integer, nullable=False)
    session = Column(Integer, nullable=False)
    name_of_house = Column(String, nullable=False)
    name_of_meeting = Column(String, nullable=True)
    issue = Column(String, nullable=False)
    date = Column(Date, nullable=True)
    closing = Column(String, nullable=True)
    meeting_url = Column(String, nullable=False)
    pdf_url = Column(String, nullable=True)

    speeches = relationship("Speech", back_populates="meeting")


class Speech(Base):
    __tablename__ = "speeches"

    issue_id = Column(String, ForeignKey("meetings.issue_id"), nullable=False)
    speech_id = Column(String, primary_key=True, unique=True, nullable=False)
    speech_order = Column(Integer, nullable=False)
    speaker = Column(String)
    speaker_yomi = Column(String)
    speaker_group = Column(String)
    speaker_position = Column(String)
    speaker_role = Column(String)
    speech = Column(Text)
    start_page = Column(Integer)
    create_time = Column(String)
    update_time = Column(String)
    speech_url = Column(String, nullable=False)

    meeting = relationship("Meeting", back_populates="speeches")
