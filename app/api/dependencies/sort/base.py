import json
from abc import abstractmethod
from itertools import chain
from typing import Optional
from urllib import parse

from fastapi import Query
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, ValidationError
from pydantic.error_wrappers import ErrorWrapper

from app.types import CaseInsensitiveEnum


class PropertyNameBase(str, CaseInsensitiveEnum):
    ...


class SortDirection(str, CaseInsensitiveEnum):
    asc = "asc"
    desc = "desc"


class SortExpressionBase(BaseModel):
    property: PropertyNameBase
    direction: SortDirection = Field(SortDirection.desc)

    @abstractmethod
    def get_model_by_property(self):
        ...

    def build_sqlalchemy_sort(self):
        model_field = self.get_model_by_property()

        if self.direction == SortDirection.asc:
            sqlalchemy_sort = model_field.asc()
        else:
            sqlalchemy_sort = model_field.desc()

        return sqlalchemy_sort

    def __str__(self):
        return f"{self.property.value} {self.direction.value}"


class SortBase:
    @abstractmethod
    def get_expression_class(self):
        ...

    def __init__(
        self,
        sort: Optional[str] = Query(None, description="Sort parameters (url encoded)"),
    ):
        self.criteria = [self.get_expression_class()()]
        if sort:
            try:
                self.criteria = self._build_criteria(json.loads(parse.unquote(sort)))
            except (json.JSONDecodeError, ValidationError, ValueError) as error:
                raise RequestValidationError([ErrorWrapper(error, ("query", "sort"))])

    def _build_criteria(self, sort_spec):
        if isinstance(sort_spec, list):
            return list(chain.from_iterable(self._build_criteria(f) for f in sort_spec))

        return [self.get_expression_class()(**sort_spec)]

    def _build_sqlalchemy_sort(self):
        return [c.build_sqlalchemy_sort() for c in self.criteria]

    def apply(self, query):
        sqlalchemy_sort = self._build_sqlalchemy_sort()
        if sqlalchemy_sort:
            return query.order_by(*sqlalchemy_sort)
        return query

    def __str__(self):
        expr = ", ".join([str(c) for c in self.criteria])
        return expr
