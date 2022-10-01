import pytest

from app.schemas.auth import ANONYMOUS_COMPANY_ID
from app.services.accounts import get_db_accounts_by_company_id

pytestmark = pytest.mark.asyncio


async def test_factor_accounts(apply_migrations, db_session):
    accounts = await get_db_accounts_by_company_id(
        company_id=ANONYMOUS_COMPANY_ID, _session=db_session
    )
    assert len(accounts) > 0
