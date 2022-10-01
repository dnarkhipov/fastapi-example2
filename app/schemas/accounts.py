from typing import Optional

from pydantic import BaseModel, Field


class BankAccountInfo(BaseModel):
    bank_name: str = Field(description="Bank Name")
    beneficiary_name: Optional[str] = Field(None, description="Beneficiary Name")
    beneficiary_address: Optional[str] = Field(None, description="Beneficiary Address")

    class Config:
        orm_mode = True
