import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from kokkai_db.schema import Base

# .envファイルから環境変数を読み込む
load_dotenv()

# --- データベース設定 ---
# 環境変数からデータベースURLを取得。なければSQLiteファイルを使用。
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL is None:
    raise Exception()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables(db_engine: Engine = engine):
    """データベースにテーブルを作成します。"""
    Base.metadata.create_all(bind=db_engine)
    print("Tables created if they did not exist.")
