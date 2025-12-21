import bcrypt
from datetime import datetime

from sqlalchemy import Integer, String, Boolean, text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, validates

from trailine_model.base import Base, TimeStampModel


class User(Base, TimeStampModel):
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
    last_login_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, comment="최근 로그인 날짜")

    @validates("password")
    def validate_password(self, key, password: str) -> str:
        """
        비밀번호를 bcrypt로 해싱한다.
        """
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed_password.decode('utf-8')

    def check_password(self, password: str) -> bool:
        """
        입력된 비밀번호와 저장된 해시 비밀번호를 비교한다.
        :param password: 사용자가 입력한 비밀번호 (일반 텍스트)
        :return: 비밀번호 일치 여부 (True/False)
        """
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
