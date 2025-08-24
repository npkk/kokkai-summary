import os

import strawberry
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware # 追加
from strawberry.fastapi import GraphQLRouter
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.graphql.resolvers import Query
from app.graphql.dataloaders import DataLoaders

def get_secret(secret_name: str) -> str | None:
    secret_path = f"/run/secrets/{secret_name}"
    if os.path.exists(secret_path):
        with open(secret_path, "r") as f:
            return f.read().strip()
    return os.environ.get(secret_name.upper())

DATABASE_URL = get_secret("database_url")

if DATABASE_URL is None:
    raise Exception("DATABASE_URL secret or environment variable not set.")

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
graphql_app = GraphQLRouter(schema, context_getter=get_context, graphql_ide=None)

app = FastAPI()

allow_origins = [
    "https://kokkai-summary.sigsegvvv.xyz",
    "http://localhost:3002"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(graphql_app, prefix="/graphql")


@app.on_event("shutdown")
async def shutdown():
    await async_engine.dispose()