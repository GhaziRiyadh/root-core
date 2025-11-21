"""Log model."""

from typing import Optional

from sqlmodel import Relationship
from sqlmodel import JSON, Field, SQLModel
from sqlmodel import Column, DateTime
from datetime import datetime

from src.core.apps.auth.models.user import User
from src.core.apps.auth.utils.utils import auth
from src.core.config import settings


class Log(SQLModel, table=True):
    """يمثل سجل التغييرات لسجلات قاعدة البيانات."""

    __tablename__ = "base_logs"  # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    table_name: str = Field(index=True, description="اسم الجدول الذي حدث فيه التغيير")
    record_id: int = Field(description="المفتاح الأساسي للسجل المتأثر")

    action: str = Field(description="نوع الإجراء المنفذ (مثل: إضافة، تعديل، delete)")
    old_data: Optional[dict] = Field(
        default=None,
        sa_column=Column(
            "old_data",
            JSON,
            nullable=True,
        ),
        description="الحالة السابقة للسجل بصيغة JSON",
    )
    new_data: Optional[dict] = Field(
        default=None,
        sa_column=Column(
            "new_data",
            JSON,
            nullable=True,
        ),
        description="الحالة الجديدة للسجل بصيغة JSON",
    )

    user_id: Optional[int] = Field(
        default_factory=lambda: auth().user.get("id", None) if auth().user else None,
        foreign_key="auth_users.id",
        nullable=True,
        ondelete="SET NULL",
        description=" المستخدم الذي نفذ الإجراء",
        index=True,
    )

    created_at: datetime = Field(
        default_factory=settings.get_now,
        sa_column=Column(DateTime(timezone=True)),
        description="الوقت الذي تم فيه إنشاء سجل التغيير",
    )
    ip_address: Optional[str] = Field(
        default=None,
        description="عنوان IP للمستخدم الذي نفذ الإجراء",
    )

    user_agent: Optional[str] = Field(
        default=None,
        description="وكيل المستخدم (User Agent) للمستخدم الذي نفذ الإجراء",
    )

    user: Optional[User] = Relationship()
