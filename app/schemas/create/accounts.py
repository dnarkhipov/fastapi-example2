from typing import Optional

from pydantic import UUID4, BaseModel, Field, root_validator, validator

from app.schemas.accounts import BankAccountInfo
from app.types import AccountType, BankAccountNumber, CurrencyNumericCode


class AccountCreateDTO(BaseModel):
    type: AccountType = Field(description="Account Type")
    currency: CurrencyNumericCode = Field(
        description="Account Currency (ISO 4217 numeric code)"
    )
    account: BankAccountNumber = Field(description="IBAN or Account No.")
    company_id: Optional[UUID4] = Field(None, description="Company ID")
    company_name: Optional[str] = Field(None, description="Company Name")
    additional_info: Optional[BankAccountInfo] = Field(
        default_factory=dict, description="Additional Bank Account info"
    )

    @validator("type")
    def allowed_types(cls, v):
        allowed_t = [
            AccountType.account_type_1,
            AccountType.account_type_2,
            AccountType.account_type_3,
        ]
        if v not in allowed_t:
            raise ValueError(f"Allowed Account Type: {[t.value for t in allowed_t]}")
        return v

    @root_validator
    def root_check(cls, values):
        _type = values.get("type")
        company_id = values.get("company_id")
        company_name = values.get("company_name")
        additional_info = values.get("additional_info")

        check = (
            _type == AccountType.account_type_1
            and company_id
            and company_name
            and additional_info
        ) or (
            _type
            in (
                AccountType.account_type_3,
                AccountType.account_type_3,
                AccountType.account_type_4,
            )
            and company_id
            and company_name
        )
        if not check:
            raise ValueError("Account parameters not fully defined")
        return values
