import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi_pagination import Page
from pydantic import UUID4

from app.api.dependencies import Filters, optional_sso_auth
from app.api.dependencies.sort.accounts import AccountsSort
from app.database.errors import EntityDoesNotExist
from app.schemas import AccountResponse
from app.schemas.auth import User
from app.services.accounts import (
    get_accounts_page,
    get_db_account_by_id,
    get_db_account_by_number,
    get_db_accounts_by_company_id,
)
from app.types import BankAccountNumber

logger = logging.getLogger("app")

router = APIRouter(tags=["accounts"])


@router.get("/", summary="Get accounts list by page", response_model=Page[Any])
@router.get(
    "",
    summary="Get accounts list by page",
    response_model=Page[Any],
    include_in_schema=False,
)
async def get_accounts(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=1000, description="Page size"),
    filters: Filters = Depends(),
    sort: AccountsSort = Depends(),
    auth_user: User = Depends(optional_sso_auth),
) -> Page[AccountResponse]:
    result_page = await get_accounts_page(
        page=page,
        size=size,
        filters=filters,
        sort=sort,
    )
    return result_page


@router.get(
    "/account-number/{number}",
    summary="Get account by number",
    response_model=Any,
)
async def get_account_by_number(
    number: BankAccountNumber = Query(..., description="Account number"),
    auth_user: User = Depends(optional_sso_auth),
) -> AccountResponse:
    try:
        account = await get_db_account_by_number(number)
    except EntityDoesNotExist as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    return account


@router.get(
    "/company-id/{company_id}",
    summary="Get accounts list by company ID",
    response_model=list[Any],
)
async def get_accounts_by_company_id(
    company_id: UUID4 = Query(..., description="Company ID"),
    auth_user: User = Depends(optional_sso_auth),
) -> list[AccountResponse]:
    accounts = await get_db_accounts_by_company_id(company_id=company_id)
    return accounts


@router.get(
    "/{account_id}",
    summary="Get account by id",
    response_model=Any,
)
async def get_account(
    account_id: UUID4 = Path(...),
    auth_user: User = Depends(optional_sso_auth),
) -> AccountResponse:
    try:
        account = await get_db_account_by_id(account_id=account_id)
    except EntityDoesNotExist as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    return account
