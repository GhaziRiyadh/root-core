import json
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    Type,
    TypeVar,
    Union,
)
from datetime import date, datetime, time
from sqlmodel import SQLModel, func, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pydantic import BaseModel

from core.helpers.commit_action import CommitAction
from core.response import schemas
from core.config import settings
from core.security_manager import auth


from core.logger import get_logger
from typing import Callable, Dict, Any, List, Optional

from core.utils.query_utils import add_include_deleted

logger = get_logger(__name__)

T = TypeVar("T", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


def json_safe(o):
    try:
        if isinstance(o, (datetime, date, time)):
            return o.isoformat()
    except Exception as e:
        print(e)
        raise e


class RepositoryError(Exception):
    """Custom exception for repository errors."""

    pass


class BaseRepository(Generic[T], CommitAction[T]):
    """
    Generic repository for SQLModel models with common CRUD, bulk and logging support.
    Improvements:
    - Consistent error handling via RepositoryError
    - No prints, uses logger
    - Safer count/total extraction using scalar APIs
    - Better typing for casts
    - Reduced repeated dynamic imports inside helper where possible
    """

    model: Type[T]
    _options: List[Any] = []
    get_session: Callable[..., AsyncSession]
    _search_fields: List[str] = []
    _permission_name: str

    casts: Dict[str, Callable[[Any], Any]] = {"id": int}

    def __init__(self, get_session: Callable[..., AsyncSession]):
        self.get_session = get_session

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_options(self) -> List[Any]:
        return list(self._options or [])

    def __get_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        # apply casts in-place but return a new dict for safety
        processed = dict(filters)
        for k, v in list(processed.items()):
            if k in self.casts and v is not None:
                try:
                    if isinstance(v, list):
                        processed[k] = [self.casts[k](item) for item in v]
                    else:
                        processed[k] = self.casts[k](v)
                except Exception as exc:
                    logger.debug("Failed casting filter %s=%r: %s", k, v, exc)
                    raise RepositoryError(f"Invalid filter value for {k}: {v}") from exc
        return processed

    def _handle_db_error(self, error: SQLAlchemyError, operation: str) -> None:
        print(error)
        if isinstance(error, IntegrityError):
            logger.exception("Integrity error during %s", operation)
            raise RepositoryError(
                f"Database integrity error during {operation}: {error}"
            ) from error
        logger.exception("Database error during %s", operation)
        raise RepositoryError(f"Database error during {operation}: {error}") from error

    def _build_select_stmt(self, include_deleted: bool = False, **filters) -> Any:
        stmt = select(self.model).options(*self.get_options())

        # soft-delete handling
        add_include_deleted(stmt, include_deleted)

        filters = self.__get_filter(filters)

        for field, value in filters.items():
            if field == "query" and value:
                search_conditions = [
                    getattr(self.model, s).ilike(f"%{value}%")
                    for s in self._search_fields
                    if hasattr(self.model, s)
                ]
                if search_conditions:
                    stmt = stmt.where(or_(*search_conditions))  # type: ignore
            elif hasattr(self.model, field):
                custom_filter = getattr(self, f"filter_{field}", None)
                if callable(custom_filter):
                    stmt = custom_filter(stmt, value)
                else:
                    model_field = getattr(self.model, field)
                    if isinstance(value, list):
                        stmt = stmt.where(model_field.in_(value))  # type: ignore
                    elif value is None:
                        stmt = stmt.where(model_field.is_(None))  # type: ignore
                    else:
                        stmt = stmt.where(model_field == value)  # type: ignore

        return stmt

    # ----------------- CRUD ----------------- #
    async def get(
        self, item_id: int, include_deleted: bool = False, **filters
    ) -> Optional[T]:
        async with self.get_session() as db:
            try:
                stmt = self._build_select_stmt(
                    include_deleted=include_deleted, **filters
                )
                stmt = stmt.where(self.model.id == item_id)  # type: ignore
                result = await db.exec(stmt)
                return result.first()
            except SQLAlchemyError as e:
                self._handle_db_error(e, "GET")

    async def get_all(
        self, include_deleted: bool = False, **filters
    ) -> List[T]:  # type:ignore
        async with self.get_session() as db:
            try:
                stmt = self._build_select_stmt(
                    include_deleted=include_deleted, **filters
                )
                result = await db.exec(stmt)
                return result.all()
            except SQLAlchemyError as e:
                self._handle_db_error(e, "get_all")

    async def get_one(self, **filters) -> Optional[T]:
        async with self.get_session() as db:
            try:
                stmt = self._build_select_stmt(**filters)
                result = await db.exec(stmt)
                return result.first()
            except SQLAlchemyError as e:
                self._handle_db_error(e, "get_one")

    async def get_many(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
        **filters,
    ) -> List[T]:  # type:ignore
        """Get multiple items with filtering and pagination."""
        async with self.get_session() as db:
            try:
                stmt = self._build_select_stmt(
                    include_deleted=include_deleted, **filters
                )
                stmt = stmt.offset(skip).limit(limit)
                result = await db.exec(stmt)
                return result.all()
            except SQLAlchemyError as e:
                self._handle_db_error(e, "get_many")

    async def list(
        self,
        page: int = 1,
        per_page: int = 10,
        include_deleted: bool = False,
        sort_by: str = "id",
        sort_order: str = "desc",
        **filters,
    ) -> schemas.PaginatedResponse:  # type:ignore
        """Get paginated list of items."""
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10

        async with self.get_session() as db:
            try:
                offset = (page - 1) * per_page
                base_stmt = self._build_select_stmt(
                    include_deleted=include_deleted, **filters
                )
                # total count
                count_stmt = select(func.count()).select_from(base_stmt.subquery())
                total_result = await db.exec(count_stmt)
                total = int(total_result.one())

                # sorting
                if hasattr(self.model, sort_by):
                    sort_col = getattr(self.model, sort_by)
                    base_stmt = base_stmt.order_by(
                        sort_col.desc()
                        if sort_order.lower() == "desc"
                        else sort_col.asc()
                    )

                # pagination and fetch
                result = await db.exec(base_stmt.offset(offset).limit(per_page))
                items = result.all()
                pages = (total + per_page - 1) // per_page

                return schemas.PaginatedResponse(
                    success=True,
                    data=items,
                    total=total,
                    page=page,
                    per_page=per_page,
                    pages=pages,
                    message="Items retrieved successfully",
                )
            except SQLAlchemyError as e:
                self._handle_db_error(e, "list")

    async def create(
        self, obj_in: Union[Dict[str, Any], CreateSchemaType]
    ) -> T:  # type:ignore
        if isinstance(obj_in, BaseModel):
            obj_in = obj_in.model_dump(exclude_unset=True)

        async with self.get_session() as db:
            try:
                obj = self.model(**obj_in)  # type: ignore
                db.add(obj)
                await db.flush()  # ensure id and defaults are present

                await self._add_log(
                    action="انشاء",
                    record_id=obj.id,  # type:ignore
                    new_data=json.loads(
                        json.dumps(
                            obj.model_dump(exclude={"is_deleted", "id"}),
                            default=json_safe,
                        )
                    ),
                    db=db,
                )

                await self.commit(db, obj, "CREATE")
                return obj
            except SQLAlchemyError as e:
                await db.rollback()
                self._handle_db_error(e, "create")

    async def create_many(
        self, objects_in: List[Union[Dict[str, Any], BaseModel]]
    ) -> List[T]:  # type:ignore
        """Create multiple items at once."""
        objects_data = [
            obj.model_dump(exclude_unset=True) if isinstance(obj, BaseModel) else obj
            for obj in objects_in
        ]

        async with self.get_session() as db:
            try:
                objects = [self.model(**data) for data in objects_data]  # type: ignore
                db.add_all(objects)
                await db.flush()

                for item in objects:
                    await self._add_log(
                        action="انشاء",
                        record_id=item.id,  # type:ignore
                        new_data=json.loads(
                            json.dumps(
                                item.model_dump(exclude={"is_deleted", "id"}),
                                default=json_safe,
                            )
                        ),
                        db=db,
                    )

                await self.commit(db=db, obj=objects, action="CREATE")
                return objects
            except SQLAlchemyError as e:
                await db.rollback()
                self._handle_db_error(e, "create_many")

    async def update(
        self,
        item_id: Any,
        obj_in: Union[Dict[str, Any], BaseModel],
        exclude_unset: bool = True,
    ) -> Optional[T]:
        update_data = (
            obj_in.model_dump(exclude_unset=exclude_unset)
            if isinstance(obj_in, BaseModel)
            else dict(obj_in)
        )
        update_data.pop("id", None)

        if not update_data:
            raise RepositoryError("No data provided for update")

        async with self.get_session() as db:
            try:
                db_obj = await db.get(self.model, item_id, options=self.get_options())
                if not db_obj:
                    return None

                await self._add_log(
                    action="تعديل",
                    record_id=db_obj.id,  # type:ignore
                    new_data=json.loads(
                        json.dumps(
                            {
                                **db_obj.model_dump(exclude={"is_deleted", "id"}),
                                **update_data,
                            },
                            default=json_safe,
                        )
                    ),
                    old_data=json.loads(
                        json.dumps(
                            db_obj.model_dump(exclude={"is_deleted", "id"}),
                            default=json_safe,
                        )
                    ),
                    db=db,
                )

                for key, value in update_data.items():
                    if value is not None:
                        update_method = getattr(self, f"update_{key}", None)
                        if callable(update_method):
                            await update_method(db, db_obj, value)  # type: ignore
                        elif hasattr(db_obj, key) and key != "id":
                            setattr(db_obj, key, value)

                await self.commit(db, db_obj, "UPDATE")
                return db_obj
            except SQLAlchemyError as e:
                await db.rollback()
                self._handle_db_error(e, "update")

    async def exists(
        self, item_id: Any, include_deleted: bool = False
    ) -> bool:  # type:ignore
        async with self.get_session() as db:
            try:
                stmt = select(self.model.id).where(self.model.id == item_id).options(*self.get_options())  # type: ignore
                add_include_deleted(stmt, include_deleted)
                result = await db.exec(stmt)
                return result.first() is not None
            except SQLAlchemyError as e:
                self._handle_db_error(e, "exists")

    async def count(
        self, include_deleted: bool = False, **filters
    ) -> int:  # type:ignore
        async with self.get_session() as db:
            try:
                stmt = self._build_select_stmt(
                    include_deleted=include_deleted, **filters
                )
                count_stmt = select(func.count()).select_from(stmt.subquery())
                result = await db.exec(count_stmt)
                return int(result.one())
            except SQLAlchemyError as e:
                self._handle_db_error(e, "count")

    # ----------------- DELETE / RESTORE ----------------- #
    async def soft_delete(self, item_id: Any) -> bool:  # type:ignore
        if not hasattr(self.model, "is_deleted"):
            raise AttributeError("Model must have 'is_deleted' field for soft delete")

        async with self.get_session() as db:
            try:
                db_obj = await db.get(self.model, item_id)
                if not db_obj:
                    return False
                setattr(db_obj, "is_deleted", True)
                await self._add_log(
                    action="حدف",
                    record_id=db_obj.id,  # type:ignore
                    new_data={"is_deleted": True},
                    old_data={"is_deleted": False},
                    db=db,
                )
                await self.commit(db, db_obj, "DELETE")
                return True
            except SQLAlchemyError as e:
                await db.rollback()
                self._handle_db_error(e, "soft_delete")

    async def restore(self, item_id: Any) -> bool:  # type:ignore
        if not hasattr(self.model, "is_deleted"):
            raise AttributeError("Model must have 'is_deleted' field for restore")

        async with self.get_session() as db:
            try:
                db_obj = await db.get(self.model, item_id)
                if not db_obj:
                    return False
                await self._add_log(
                    action="استعاده",
                    record_id=db_obj.id,  # type:ignore
                    new_data={"is_deleted": False},
                    old_data={"is_deleted": True},
                    db=db,
                )
                setattr(db_obj, "is_deleted", False)
                await self.commit(db, db_obj, "RESTORE")
                return True
            except SQLAlchemyError as e:
                await db.rollback()
                self._handle_db_error(e, "restore")

    async def force_delete(self, item_id: Any) -> bool:  # type:ignore
        async with self.get_session() as db:
            try:
                db_obj = await db.get(self.model, item_id)
                if not db_obj:
                    return False
                await self._add_log(
                    action="حدف نهائي",
                    record_id=db_obj.id,  # type:ignore
                    old_data=json.loads(
                        json.dumps(db_obj.model_dump(), default=json_safe)
                    ),
                    db=db,
                )
                await db.delete(db_obj)
                await self.commit(db=db, obj=db_obj, action="DELETE")
                return True
            except SQLAlchemyError as e:
                await db.rollback()
                self._handle_db_error(e, "force_delete")

    async def force_delete_many(self, item_ids: List[Any]) -> bool:  # type:ignore
        async with self.get_session() as db:
            try:
                result = await db.exec(
                    select(self.model)
                    .where(self.model.id.in_(item_ids))  # type: ignore
                    .options(*self.get_options())
                )
                objects = result.all()
                for obj in objects:
                    await db.delete(obj)
                    await self._add_log(
                        action="حدف نهائي",
                        record_id=obj.id,  # type:ignore
                        old_data=json.loads(
                            json.dumps(obj.model_dump(), default=json_safe)
                        ),
                        db=db,
                    )
                await self.commit(db=db, obj=objects, action="DELETE")
                return True
            except SQLAlchemyError as e:
                await db.rollback()
                self._handle_db_error(e, "force_delete_many")

    async def bulk_create(self, items: List[T]) -> List[T]:  # type:ignore
        async with self.get_session() as db:
            try:
                db.add_all(items)
                await db.flush()
                for item in items:
                    await self._add_log(
                        action="انشاء",
                        record_id=item.id,  # type:ignore
                        new_data=json.loads(
                            json.dumps(
                                item.model_dump(exclude={"is_deleted", "id"}),
                                default=json_safe,
                            )
                        ),
                        db=db,
                    )
                await db.commit()
                for item in items:
                    await db.refresh(item)
                return items
            except SQLAlchemyError as e:
                await db.rollback()
                self._handle_db_error(e, "bulk_create")

    async def bulk_update(self, items: List[T]) -> List[T]:  # type:ignore
        async with self.get_session() as db:
            try:
                for item in items:
                    await db.merge(item)
                    await self._add_log(
                        action="تعديل",
                        record_id=item.id,  # type:ignore
                        new_data=json.loads(
                            json.dumps(
                                item.model_dump(exclude={"is_deleted", "id"}),
                                default=json_safe,
                            )
                        ),
                        db=db,
                    )
                await db.commit()
                for item in items:
                    await db.refresh(item)
                return items
            except SQLAlchemyError as e:
                await db.rollback()
                self._handle_db_error(e, "bulk_update")

    async def search(
        self, query: str, search_fields: List[str] = [], include_deleted: bool = False
    ) -> schemas.PaginatedResponse:  # type:ignore
        if not search_fields:
            search_fields = self._search_fields

        async with self.get_session() as db:
            try:
                stmt = select(self.model).options(*self.get_options())
                add_include_deleted(stmt, include_deleted)
                if hasattr(self.model, "is_deleted"):
                    stmt = stmt.where(self.model.is_deleted == False)  # type: ignore

                search_conditions = [
                    getattr(self.model, field).ilike(f"%{query}%")
                    for field in search_fields
                    if hasattr(self.model, field)
                ]
                if search_conditions:
                    stmt = stmt.where(or_(*search_conditions))

                result = await db.exec(stmt)
                items = result.all()
                total = len(items)
                return schemas.PaginatedResponse(
                    success=True,
                    data=list(items),
                    total=total,
                    page=1,
                    per_page=total,
                    pages=1,
                    message="Search completed successfully",
                )
            except SQLAlchemyError as e:
                self._handle_db_error(e, "search")

    async def bulk_delete(self, ids: List[int]):
        if not hasattr(self.model, "is_deleted"):
            raise AttributeError("Model must have 'is_deleted' field for bulk delete")

        async with self.get_session() as db:
            try:
                result = await db.exec(select(self.model).where(self.model.id.in_(ids)))  # type: ignore
                objects = result.all()
                for obj in objects:
                    new_deleted = not getattr(obj, "is_deleted", True)
                    old_deleted = not new_deleted
                    setattr(obj, "is_deleted", new_deleted)
                    await self._add_log(
                        action=("حدف" if new_deleted else "استعاده"),
                        record_id=obj.id,  # type:ignore
                        new_data={"is_deleted": new_deleted},
                        old_data={"is_deleted": old_deleted},
                        db=db,
                    )
                await db.commit()
                for obj in objects:
                    await db.refresh(obj)
                return True
            except SQLAlchemyError as e:
                await db.rollback()
                self._handle_db_error(e, "bulk_delete")

    async def get_logs(
        self,
        page: int = 1,
        per_page: int = 10,
        include_deleted: bool = False,
        sort_by: str = "id",
        sort_order: str = "desc",
        **filters,
    ) -> schemas.PaginatedResponse:  # type:ignore
        try:
            log_module = __import__(settings.LOG_MODEL, fromlist=["Log"])
            Log = getattr(log_module, "Log")

            stmt = select(Log).where(
                Log.table_name
                == getattr(self.model, "__tablename__", self.model.__name__)
            )
            add_include_deleted(stmt, include_deleted)

            for field, value in filters.items():
                if hasattr(Log, field):
                    model_field = getattr(Log, field)
                    if isinstance(value, list):
                        stmt = stmt.where(model_field.in_(value))  # type: ignore
                    elif value is None:
                        stmt = stmt.where(model_field.is_(None))  # type: ignore
                    else:
                        stmt = stmt.where(model_field == value)  # type: ignore

            async with self.get_session() as db:
                count_stmt = select(func.count()).select_from(stmt.subquery())
                total_result = await db.exec(count_stmt)
                total = int(total_result.one())

                if hasattr(Log, sort_by):
                    sort_col = getattr(Log, sort_by)
                    stmt = stmt.order_by(
                        sort_col.desc()
                        if sort_order.lower() == "desc"
                        else sort_col.asc()
                    )

                if page < 1:
                    page = 1
                if per_page < 1 or per_page > 100:
                    per_page = 10
                offset = (page - 1) * per_page

                result = await db.exec(stmt.offset(offset).limit(per_page))
                items = result.all()
                pages = (total + per_page - 1) // per_page

                return schemas.PaginatedResponse(
                    success=True,
                    data=items,  # type:ignore
                    total=total,
                    page=page,
                    per_page=per_page,
                    pages=pages,
                    message="Logs retrieved successfully",
                )
        except SQLAlchemyError as e:
            self._handle_db_error(e, "get_logs")
        except Exception as e:
            logger.exception("Unexpected error in get_logs: %s", e)
            raise RepositoryError(f"Error retrieving logs: {e}") from e

    async def _add_log(
        self,
        action: Literal["انشاء", "تعديل", "حدف", "استعاده", "حدف نهائي"],
        old_data: Optional[Any] = None,
        new_data: Optional[Any] = None,
        record_id: int = 0,
        user_id: Optional[int] = None,
        db: Optional[AsyncSession] = None,
    ):
        try:
            user = auth().user
            if user and hasattr(user, "id"):
                user_id = user.id  # type: ignore
            ip = auth().ip_address
            ua = auth().user_agent

            def _serialize(data: Any) -> Any:
                if data is None:
                    return None
                try:
                    return json.loads(json.dumps(data, default=json_safe))
                except Exception:
                    return str(data)

            async def save_log(session: AsyncSession):
                log_module = __import__(settings.LOG_MODEL, fromlist=["Log"])
                Log = getattr(log_module, "Log")
                entry = Log(
                    table_name=getattr(
                        self.model, "__tablename__", self.model.__name__
                    ),
                    record_id=record_id,
                    action=action,
                    old_data=_serialize(old_data),
                    new_data=_serialize(new_data),
                    user_id=user_id,
                    ip_address=ip,
                    user_agent=ua,
                )
                session.add(entry)

            if db:
                await save_log(db)
            else:
                async with self.get_session() as session:
                    await save_log(session)
        except SQLAlchemyError as e:
            logger.exception("Failed to add log entry: %s", e)
            # Do not raise to avoid breaking primary operation; log only
        except Exception as e:
            logger.exception("Unexpected error in _add_log: %s", e)
