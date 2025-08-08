import os

import strawberry
from fastapi import FastAPI, Request
from strawberry.fastapi import GraphQLRouter
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from dotenv import load_dotenv

from app.graphql.resolvers import Query
from app.graphql.dataloaders import DataLoaders

# .envファイルから環境変数を読み込む
load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL is None:
    raise Exception("DATABASE_URL environment variable not set.")

# 非同期エンジンを作成
async_engine = create_async_engine(DATABASE_URL, echo=True)

# 非同期セッションを作成
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_context(request: Request) -> dict:
    session = AsyncSessionLocal()
    try:
        return {"session": session, "dataloaders": DataLoaders(session)}
    finally:
        await session.close()


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema, context_getter=get_context)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(graphql_app, prefix="/graphql")
