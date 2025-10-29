from contextlib import asynccontextmanager
from typing import Optional

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import Field, SQLModel, Session, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from root_core.config import settings

engine = create_async_engine(settings.ASYCNC_DATABASE_URL, echo=False)

local_engine = create_engine(settings.DATABASE_URI, echo=False)


@asynccontextmanager
async def get_session():
    async with AsyncSession(engine) as session:
        yield session


def get_local_session():
    with Session(local_engine) as session:
        yield session


class BaseModel(SQLModel):
    """Base model with common fields."""

    id: Optional[int] = Field(default=None, primary_key=True)
    is_deleted: bool = Field(default=False)
