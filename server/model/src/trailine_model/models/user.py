from datetime import datetime

from sqlalchemy import Integer, String, Boolean, text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from trailine_model.base import Base, TIME_ZONE_QUERY


class User(Base):
    __tablename__ = "user"
    __table_args__ = {
        "comment": "사용자"
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    nickname: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    can_access_admin: Mapped[bool] = mapped_column(Boolean, nullable=False,
                                                   server_default=text("false"), comment="어드민 접속 가능 여부")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                 server_default=text(f"({TIME_ZONE_QUERY})"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                 server_default=text(f"({TIME_ZONE_QUERY})"),
                                                 onupdate=text(f"({TIME_ZONE_QUERY})"))
    last_login_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, comment="최근 로그인 날짜")
