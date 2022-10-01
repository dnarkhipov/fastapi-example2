from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, String, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CompanyDB(Base):
    __tablename__ = "companies"

    id: UUID = Column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        autoincrement=False,
    )
    name: str = Column(
        String,
        nullable=False,
    )
    created: Optional[datetime] = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    modified: Optional[datetime] = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
