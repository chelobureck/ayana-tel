import os
import ssl
import urllib.parse
from typing import AsyncGenerator, Dict, Any

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config.settings import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    pass


def _build_database_url() -> str:
    if getattr(settings, "USE_POSTGRES", "false").lower() in ("1", "true", "yes"):
        if getattr(settings, "DATABASE_URL", None):
            return settings.DATABASE_URL
        user = settings.POSTGRES_USER
        password = urllib.parse.quote_plus(settings.POSTGRES_PASSWORD or "")
        server = settings.POSTGRES_SERVER
        port = settings.POSTGRES_PORT
        db = settings.POSTGRES_DB
        return f"postgresql+asyncpg://{user}:{password}@{server}:{port}/{db}"
    # default local sqlite
    return "sqlite+aiosqlite:///./local.db"


DATABASE_URL = _build_database_url()

# engine & connect_args
connect_args: Dict[str, Any] = {}
engine_kwargs: Dict[str, Any] = {"echo": False, "pool_pre_ping": True}

if "sqlite" in DATABASE_URL:
    # aiosqlite specific tweaks if needed
    engine = create_async_engine(DATABASE_URL, **engine_kwargs)
else:
    # try to decide about SSL for asyncpg
    env_value = (os.getenv("ENVIRONMENT") or getattr(settings, "ENVIRONMENT", "")).lower()
    must_use_ssl = (
        env_value in ("production", "prod")
        or "aws" in env_value
        or "render" in env_value
        or ("rds.amazonaws.com" in DATABASE_URL)
    )
    if must_use_ssl:
        ssl_verify = (os.getenv("POSTGRES_SSL_VERIFY") or "true").lower() == "true"
        ssl_ctx = ssl.create_default_context()
        if not ssl_verify:
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = ssl_ctx  # type: ignore
    else:
        connect_args["ssl"] = None

    engine = create_async_engine(DATABASE_URL, connect_args=connect_args, **engine_kwargs)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session