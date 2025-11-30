from contextlib import asynccontextmanager, contextmanager
from typing import Any, AsyncGenerator, Generator, Optional

from sqlalchemy import event
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import Field, SQLModel, create_engine, Session
from sqlmodel.ext.asyncio.session import AsyncSession

from core.config import settings
from core.logger import get_logger

# Import app-specific database functions
from core.database_registry import (
    get_app_session,
    discover_app_database,
    discover_all_app_databases,
    get_async_engine,
    get_sync_engine,
)

logger = get_logger(__name__)

engine = create_async_engine(settings.ASYNC_DATABASE_URI, echo=False, future=True)
local_engine = create_engine(settings.DATABASE_URI, echo=False, future=True)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Async context manager that yields an AsyncSession."""
    async with AsyncSession(engine) as session:
        yield session


@contextmanager
def get_local_session() -> Generator[Session, None, None]:
    """Sync context manager that yields a sync Session."""
    with Session(local_engine) as session:
        yield session


class BaseModel(SQLModel):
    """Base model with common fields for soft-delete support."""

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        title="المعرف",
        description="المعرف الفريد للسجل",
    )
    is_deleted: bool = Field(
        default=False, title="محذوف", description="يشير إلى ما إذا تم حذف السجل منطقياً"
    )

    # created_at: datetime = Field(
    #     default_factory=settings.get_now,
    #     sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    #     title="تاريخ الإنشاء",
    #     description="وقت إنشاء السجل",
    # )

    # updated_at: Optional[datetime] = Field(
    #     default=None,
    #     sa_column=Column(DateTime(timezone=True), onupdate=func.now()),
    #     title="تاريخ التحديث",
    #     description="وقت آخر تحديث للسجل",
    # )


# Soft-delete global query filter registration.
# The filter is applied automatically to all SELECT queries unless the
# execution option "include_deleted=True" is provided.
@event.listens_for(AsyncSession.sync_session_class, "do_orm_execute")
@event.listens_for(Session, "do_orm_execute")
def _apply_soft_delete_filter(execute_state):
    if execute_state.is_select and not execute_state.execution_options.get(
        "include_deleted", False
    ):
        logger.debug("Applying soft delete filter")
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                BaseModel,
                exclude_deleted_records,
                include_aliases=True,
            )
        )


def exclude_deleted_records(cls) -> Any:
    if hasattr(cls, "is_deleted"):
        return cls.is_deleted == False
    return True
