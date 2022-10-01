import logging
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from app.api.dependencies.sort import AccountsSort
    from app.api.dependencies import Filters

from fastapi_async_sqlalchemy import db
from sqlalchemy import not_, select
from sqlalchemy.exc import IntegrityError

from app.database.errors import ConflictWhenInsert, EntityDoesNotExist
from app.models.accounts import AccountDB
from app.models.companies import CompanyDB
from app.paginate_patch import ParamsEx, paginate
from app.schemas.create.accounts import AccountCreateDTO
from app.schemas.response.accounts import AccountResponse, get_response_model_by_type
from app.types import AccountType, BankAccountNumber

logger = logging.getLogger("app")


def map_raw_account(account) -> AccountResponse:
    model = get_response_model_by_type(account[0].type)
    result = model.from_orm(account[0])
    result.balance = account["balance"]
    result.balance_date = account["balance_date"]
    return result


async def get_accounts_page(
    *,
    page: int = 1,
    size: int = 50,
    filters: "Filters",
    sort: "AccountsSort",
):
    stmt = select(AccountDB).filter(not_(AccountDB.archived))
    stmt = filters.apply(stmt)
    stmt = sort.apply(stmt)

    accounts_page = await paginate(
        db.session,
        stmt,
        ParamsEx(page=page, size=size),
        mapping_func=map_raw_account,
    )
    return accounts_page


async def get_db_account_by_id(account_id: UUID, archived: bool = False) -> AccountDB:
    stmt = select(AccountDB).filter(AccountDB.id == account_id)
    if not archived:
        stmt = stmt.filter(not_(AccountDB.archived))
    result = await db.session.execute(stmt)
    account = result.scalar()
    if not account:
        raise EntityDoesNotExist(f"Account with id '{account_id}' does not exists")
    return account


async def get_db_account_by_number(number: BankAccountNumber) -> AccountResponse:
    stmt = select(AccountDB).filter(
        AccountDB.account == number, not_(AccountDB.archived)
    )
    result = await db.session.execute(stmt)
    account = result.scalars().first()
    if not account:
        raise EntityDoesNotExist(f"Account with number '{number}' does not exists")
    return map_raw_account(account)


async def get_db_accounts_by_company_id(
    *, company_id: UUID, _session=None
) -> list[AccountResponse]:
    if not _session:
        _session = db.session

    stmt = select(AccountDB).filter(
        AccountDB.company_id == company_id, not_(AccountDB.archived)
    )
    result = await _session.execute(stmt)
    accounts = [map_raw_account(a) for a in result.all()]
    return accounts


async def create_account(account_dto: AccountCreateDTO) -> AccountDB:
    if account_dto.type == AccountType.account_type_1:
        _accounts = await get_db_accounts_by_company_id(
            company_id=account_dto.company_id
        )
    else:
        _accounts = []

    account = next(
        (
            a
            for a in _accounts
            if a.currency == account_dto.currency and a.type == account_dto.type
        ),
        None,
    )

    # only one account per company in a given currency
    if not account:
        try:
            model_kwargs = account_dto.dict(exclude={"company_name"})

            if account_dto.company_id is not None:
                await db.session.merge(
                    CompanyDB(
                        id=account_dto.company_id,
                        name=account_dto.company_name,
                    )
                )

            account = AccountDB(**model_kwargs)

            db.session.add(account)
            await db.session.commit()
            await db.session.refresh(account)
        except IntegrityError as error:
            logger.error(str(error))
            raise ConflictWhenInsert(
                f"Insert new entity in database raising a unique violation or exclusion constraint violation error: {error}"  # noqa
            )
        logger.debug(f"Create new Account: {str(account)}")

    return map_raw_account(account)
