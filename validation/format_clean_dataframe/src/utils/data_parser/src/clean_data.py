"""
Parser each data cell in DataFrame

"""

from decimal import Decimal
import re
from abc import ABC, abstractmethod
from typing import override
from .data_parser import DataParser


class IValidator(ABC):
    @abstractmethod
    def convert_str(line: str) -> str: ...


class ParseValueToDecimal(IValidator):
    @staticmethod
    @override
    def convert_str(val: str) -> str | Decimal:
        """
        Tries to return a Decimal
        """
        return DataParser.parse_string_to_decimal(val)


class DeleteUnicodeXA0(IValidator):
    @staticmethod
    @override
    def convert_str(val: str | int | Decimal) -> str | Decimal:
        """
        Limpia los datos con caracteres "[€\xa0]"
        """
        if not isinstance(val, str):
            return val

        return re.sub(r"\xa0", "", val)


class ParseDatetime(IValidator):
    """
    "dd/mm/yy" or "dd/mm/yyyy" string into datetime object
    """

    @staticmethod
    @override
    def convert_str(val: str | int | Decimal) -> str:
        return DataParser.parse_string_to_datetime(val)


class ParsePercentageToDecimal(IValidator):
    @staticmethod
    @override
    def convert_str(line: str) -> str:
        if not isinstance(line, str):
            return line

        pattern: re.Pattern = re.compile(rf"^{DataParser.spanish_numeric_data}\s*%$")
        if num := pattern.match(line):
            return DataParser.parse_string_to_decimal(num.group(1)) / 100
        return line


class DeleteSIAccents(IValidator):
    """
    Deleted accents if
    """

    @staticmethod
    @override
    def convert_str(line: str) -> str:
        if line == "SÍ":
            return line.replace("SÍ", "SI")
        return line


class DataClean:
    VALIDATORS: tuple[IValidator,...] = (
        DeleteUnicodeXA0,
        ParseDatetime,
        ParseValueToDecimal,
        ParsePercentageToDecimal,
        DeleteSIAccents,
    )

    @classmethod
    def apply(cls, value: str) -> str:
        for func in cls.VALIDATORS:
            value = func.convert_str(value)
        return value
