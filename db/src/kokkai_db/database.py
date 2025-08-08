from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from kokkai_db.schema import Base


def create_engine_and_session(database_url: str):
    """データベースURLからengineとSessionLocalを作成して返します。"""
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal


def create_tables(db_engine: Engine):
    """データベースにテーブルを作成します。"""
    Base.metadata.create_all(bind=db_engine)
    print("Tables created if they did not exist.")