from datetime import datetime
from typing import TypeVar

from pydantic import UUID4, BaseModel, Field

from app.schemas.accounts import BankAccountInfo
from app.types import AccountType, CurrencyNumericCode


class AccountResponseMixin(BaseModel):
    company_id: UUID4 = Field(description="Company ID")
    company_name: str = Field(description="Company Name")


class AccountBaseResponse(BaseModel):
    id: UUID4 = Field(description="Account unique ID")
    type: AccountType = Field(description="Account type")
    currency: CurrencyNumericCode = Field(
        description="Account Currency (ISO 4217 numeric code)"
    )
    created: datetime = Field(description="Date and time the entry was created")
    modified: datetime = Field(description="Date and time the entry was changed")

    class Config:
        orm_mode = True


class AccountType1Response(
    AccountResponseMixin,
    AccountBaseResponse,
):
    additional_info: BankAccountInfo = Field(description="Additional Info")


class AccountType2Response(
    AccountBaseResponse,
):
    pass


class AccountType3Response(
    AccountResponseMixin,
    AccountBaseResponse,
):
    pass


class AccountType4Response(
    AccountResponseMixin,
    AccountBaseResponse,
):
    pass


AccountResponse = TypeVar(
    "AccountResponse",
    AccountType1Response,
    AccountType2Response,
    AccountType3Response,
    AccountType4Response,
)


def get_response_model_by_type(
    account_type: AccountType,
) -> type(AccountResponse):
    if account_type == AccountType.account_type_1:
        model = AccountType1Response
    elif account_type == AccountType.account_type_2:
        model = AccountType2Response
    elif account_type == AccountType.account_type_3:
        model = AccountType3Response
    elif account_type == AccountType.account_type_4:
        model = AccountType4Response
    else:
        model = None
    if model is None:
        raise ValueError(f"Unsupported Account Type: {account_type}")
    return model


def build_account_response_by_type(account) -> AccountResponse:
    model = get_response_model_by_type(account.type)
    return model.from_orm(account)
