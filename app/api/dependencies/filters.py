import json
from collections import namedtuple
from datetime import datetime
from inspect import signature
from itertools import chain
from typing import Any, Optional
from urllib import parse

from fastapi import Query
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ValidationError, validator
from pydantic.error_wrappers import ErrorWrapper
from sqlalchemy import and_, not_, or_
from sqlalchemy.ext.associationproxy import ObjectAssociationProxyInstance

from app.models.accounts import AccountDB
from app.types import AccountType, CaseInsensitiveEnum, CurrencyNumericCode


def like_patch(attr, *args, **kwargs):
    # https://github.com/sqlalchemy/sqlalchemy/issues/4351
    filter_attr = attr
    if isinstance(
        filter_attr, ObjectAssociationProxyInstance
    ):  # If assoc_proxy get remote_attr as like() doesnt work
        filter_attr = filter_attr.remote_attr
    return filter_attr.like(*args, **kwargs)


def ilike_patch(attr, *args, **kwargs):
    filter_attr = attr
    if isinstance(
        filter_attr, ObjectAssociationProxyInstance
    ):  # If assoc_proxy get remote_attr as ilike() doesnt work
        filter_attr = filter_attr.remote_attr
    return filter_attr.ilike(*args, **kwargs)


class PropertyName(str, CaseInsensitiveEnum):
    type = "type"
    client = "client"
    client_id = "client_id"
    currency = "currency"
    modified = "modified"


PROPERTY_TO_MODEL_MAP = {
    PropertyName.type: AccountDB.type,
    PropertyName.client_id: AccountDB.factoring_company_id,
    PropertyName.client: AccountDB.factoring_company_name,
    PropertyName.currency: AccountDB.currency,
    PropertyName.modified: AccountDB.modified,
}


BooleanExpression = namedtuple(
    "BooleanExpression", ("exp", "sqlalchemy_exp", "single_arg")
)
BOOLEAN_EXPRESSIONS = (
    BooleanExpression("or", or_, False),
    BooleanExpression("and", and_, False),
    BooleanExpression("not", not_, True),
)
"""
Sqlalchemy boolean expressions that can be parsed from the filter definition.
"""


class Operator:

    OPERATORS = {
        "is_null": lambda p: p.is_(None),
        "is_not_null": lambda p: p.isnot(None),
        "=": lambda p, v: p == v,
        "!=": lambda p, v: p != v,
        ">": lambda p, v: p > v,
        "<": lambda p, v: p < v,
        ">=": lambda p, v: p >= v,
        "<=": lambda p, v: p <= v,
        "like": lambda p, v: like_patch(p, v),
        "ilike": lambda p, v: ilike_patch(p, v),
        "not_ilike": lambda p, v: ~ilike_patch(p, v),
        "in": lambda p, v: p.in_(v),
        "not_in": lambda p, v: ~p.in_(v),
        # "any": lambda p, v: p.any(v),
        # "not_any": lambda p, v: func.not_(p.any(v)),
    }

    def __init__(self, operator):
        if operator not in self.OPERATORS:
            raise ValueError(f"Operator `{operator}` not valid.")

        self.operator = operator
        self.function = self.OPERATORS[operator]
        self.arity = len(signature(self.function).parameters)

    def __str__(self):
        return self.operator


class FilterExpression(BaseModel):
    property: PropertyName
    operator: Operator
    value: Optional[Any]

    class Config:
        arbitrary_types_allowed = True

    @validator("value")
    def type_of_value(cls, v, values, **kwargs):
        if "property" in values:
            if values["property"] == PropertyName.type:
                [AccountType(t) for t in v] if isinstance(v, list) else AccountType(v)
            elif values["property"] in (PropertyName.modified,):
                [datetime.fromisoformat(t) for t in v] if isinstance(
                    v, list
                ) else datetime.fromisoformat(v)
            elif values["property"] == PropertyName.currency:
                [CurrencyNumericCode.validate(t) for t in v] if isinstance(
                    v, list
                ) else CurrencyNumericCode.validate(v)

        return v

    def _cast_sql_value(self):
        if self.property in (PropertyName.modified,):
            v = datetime.fromisoformat(self.value)
        else:
            v = self.value
        return v

    def build_sqlalchemy_filter(self):
        model_field = PROPERTY_TO_MODEL_MAP[self.property]

        function = self.operator.function
        arity = self.operator.arity
        sql_value = self._cast_sql_value()

        if isinstance(model_field, (tuple, list)):
            if arity == 2:
                sqlalchemy_filter = or_(*[function(f, sql_value) for f in model_field])
            else:
                sqlalchemy_filter = or_(*[function(f) for f in model_field])
        else:
            if arity == 2:
                sqlalchemy_filter = function(model_field, sql_value)
            else:
                sqlalchemy_filter = function(model_field)

        return sqlalchemy_filter

    def __str__(self):
        return f"{self.property.value} {str(self.operator)} '{str(self.value)}'"


class BooleanGroup:
    def __init__(self, expression, *filters):
        self.expression = expression
        self.filters = filters

    def build_sqlalchemy_filter(self):
        return self.expression.sqlalchemy_exp(
            *[f.build_sqlalchemy_filter() for f in self.filters]
        )

    def __str__(self):
        exp = f" {self.expression.exp} ".upper()
        return exp.join(str(f) for f in self.filters)


class Filters:

    criteria = []

    def __init__(
        self,
        filters: Optional[str] = Query(
            None, alias="filter", description="Filter settings (url encoded)"
        ),
    ):
        if filters:
            try:
                self.criteria = self._build_criteria(json.loads(parse.unquote(filters)))
            except (json.JSONDecodeError, ValidationError, ValueError) as error:
                raise RequestValidationError(
                    [ErrorWrapper(error, ("query", "filters"))]
                )

    def _build_criteria(self, filters_spec):
        if isinstance(filters_spec, list):
            return list(
                chain.from_iterable(self._build_criteria(f) for f in filters_spec)
            )

        if isinstance(filters_spec, dict):
            criteria = []
            for expression in BOOLEAN_EXPRESSIONS:
                if expression.exp in filters_spec.keys():
                    exp_args = filters_spec[expression.exp]
                    criteria.append(
                        BooleanGroup(
                            expression,
                            *self._build_criteria(exp_args),
                        )
                    )
                    return criteria

        return [
            FilterExpression(
                property=filters_spec["property"].lower(),
                operator=Operator(filters_spec["operator"].lower()),
                value=filters_spec.get("value"),
            )
        ]

    def _build_sqlalchemy_filters(self):
        return [c.build_sqlalchemy_filter() for c in self.criteria]

    def apply(self, query):
        sqlalchemy_filters = self._build_sqlalchemy_filters()
        if sqlalchemy_filters:
            return query.filter(*sqlalchemy_filters)
        return query

    def __str__(self):
        expr = " AND ".join([str(c) for c in self.criteria])
        return expr
