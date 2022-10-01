from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from app.types import AccountType, BankAccountNumber, CurrencyNumericCode

from .companies import CompanyDB

Base = declarative_base()


class AccountDB(Base):
    __tablename__ = "accounts"
    id: Optional[UUID] = Column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        server_default=text("uuid_generate_v4()"),
    )
    type: AccountType = Column(Enum(AccountType, name="account_type"), nullable=False)
    currency: CurrencyNumericCode = Column(String(3), nullable=False)
    account: BankAccountNumber = Column(String, unique=True, nullable=False)

    company_id: UUID = Column(
        postgresql.UUID(as_uuid=True),
        ForeignKey(CompanyDB.id),
        nullable=False,
    )
    company = relationship(CompanyDB, uselist=False, lazy="joined", innerjoin=True)
    company_name = association_proxy("company", "name")

    additional_info = Column(postgresql.JSONB, server_default="{}", nullable=False)
    archived: bool = Column(Boolean, server_default="false", nullable=False)
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

    def __str__(self):
        return (
            f"Account(id='{str(self.id)}';"
            f" type='{self.type.value}';"
            f" currency='{self.currency}';"
            f" account='{self.account}';"
            f" company_id='{str(self.company_id)}';"
            f" company_name='{self.company_name}';"
        )
