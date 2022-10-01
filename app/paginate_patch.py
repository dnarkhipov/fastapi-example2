from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

from fastapi import Query
from fastapi_pagination import Params, create_page, resolve_params
from fastapi_pagination.bases import AbstractPage, AbstractParams
from fastapi_pagination.ext.sqlalchemy import paginate_query
from sqlalchemy import func, select

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.sql import Select


class ParamsEx(Params):
    size: int = Query(50, ge=1, description="Page size")


async def paginate(
    session: AsyncSession,
    query: Select,
    params: Optional[AbstractParams] = None,
    mapping_func: Callable = None,
) -> AbstractPage:
    params = resolve_params(params)

    total = await session.scalar(select(func.count()).select_from(query.subquery()))  # type: ignore
    results = await session.execute(paginate_query(query, params))

    if mapping_func:
        items = [mapping_func(i) for i in results.unique().all()]
    else:
        items = results.scalars().unique().all()

    return create_page(items, total, params)
