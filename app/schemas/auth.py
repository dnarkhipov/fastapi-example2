from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

ANONYMOUS_USER_ID = UUID("1a00212b-0151-4aae-9ffd-daf367461d08")
ANONYMOUS_USER_NAME = "anonymous"
ANONYMOUS_USER_EMAIL = "anonymous@company.com"
ANONYMOUS_COMPANY_ID = UUID("a422fb8c-046e-4786-a076-93039cc9aab5")
ANONYMOUS_COMPANY_NAME = UUID("755b596b-2492-4a85-b292-ee6c0bea1170")


class User(BaseModel):
    id: UUID = Field(description="User ID (SCA)")
    name: str = Field(description="User Name")
    email: str = Field(description="User email")
    company_id: UUID = Field(description="Company ID")
    company_name: str = Field(description="Company Name")

    @classmethod
    def anonymous(cls) -> User:
        return User(
            id=ANONYMOUS_USER_ID,
            name=ANONYMOUS_USER_NAME,
            email=ANONYMOUS_USER_EMAIL,
            company_id=ANONYMOUS_COMPANY_ID,
            company_name=ANONYMOUS_COMPANY_NAME,
        )
