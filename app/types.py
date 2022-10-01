import re
from enum import Enum

from pydantic import ConstrainedStr


class CaseInsensitiveEnum(Enum):
    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if member.value == value.lower():
                return member
        return None


class CurrencyNumericCode(ConstrainedStr):
    """Currency three-digit numeric code (ISO 4217)"""

    regex = re.compile(r"^\d{3}$")


class BankAccountNumber(ConstrainedStr):
    """Bank account number (IBAN or other): 8..34 символов"""

    min_length = 8
    max_length = 34


class AccountType(str, Enum):
    account_type_1 = "account-type-1"
    account_type_2 = "account-type-2"
    account_type_3 = "account-type-3"
    account_type_4 = "account-type-4"
