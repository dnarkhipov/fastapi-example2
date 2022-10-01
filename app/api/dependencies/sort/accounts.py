from pydantic import Field

from app.models.accounts import AccountDB

from .base import PropertyNameBase, SortBase, SortExpressionBase


class PropertyName(PropertyNameBase):
    created = "created"
    modified = "modified"


PROPERTY_TO_MODEL_MAP = {
    PropertyName.created: AccountDB.created,
    PropertyName.modified: AccountDB.modified,
}


class AccountsSortExpression(SortExpressionBase):
    property: PropertyName = Field(PropertyName.modified)

    def get_model_by_property(self):
        return PROPERTY_TO_MODEL_MAP[self.property]


class AccountsSort(SortBase):
    def get_expression_class(self):
        return AccountsSortExpression
