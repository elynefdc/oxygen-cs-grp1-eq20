import datetime
from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.dialects import postgresql
from sqlalchemy import types
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import BIGINT, Integer, NVARCHAR, String, TIMESTAMP


class Base(DeclarativeBase):
    pass


class UserEvent(Base):
    __tablename__ = "user_event"

    id: Mapped[int] = mapped_column(primary_key=True)
    temperature: Mapped[float] = mapped_column(types.Float)
    timestamp: Mapped[datetime.datetime] = mapped_column(TIMESTAMP)


class SystemEvent(Base):
    __tablename__ = "system_event"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    timestamp: Mapped[datetime.datetime] = mapped_column(TIMESTAMP)
