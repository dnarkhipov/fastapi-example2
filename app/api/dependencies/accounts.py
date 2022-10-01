from fastapi import HTTPException, Path, status
from pydantic.types import UUID4

from app.database.errors import EntityDoesNotExist
from app.models.accounts import AccountDB
from app.services.accounts import get_db_account_by_id


async def get_db_account_by_id_from_path(account_id: UUID4 = Path(...)) -> AccountDB:
    try:
        return await get_db_account_by_id(account_id)
    except EntityDoesNotExist as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
