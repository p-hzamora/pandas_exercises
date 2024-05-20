import calendar
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Literal, Union

from .spanish_month import SpanishMonth

NumericType = Union[float, int, Decimal]
DatetimeType = Literal["short", "long"]
DatetimeTypeNoDay = Literal["short", "long", "short_no_day"]


class DataParseError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    def __str__(self) -> str:
        return f"The specified condition was not met for '{self.args[0]}' value with '{type(self.args[0])}' as data type"


class DataParser(object):
    spanish_numeric_data = r"(-?\d{1,3}(?:\.?\d{3})*(?:,\d+)?)"
    raise_error: bool = False

    def __new__(cls, raise_error) -> "DataParser":
        cls.raise_error = raise_error
        return object.__new__(cls)

    @classmethod
    def raise_error_or_return_value(cls, error: Exception, value: Any):
        if cls.raise_error:
            raise error(value)
        return value

    @classmethod
    def parse_string_to_decimal(cls, val: str) -> Decimal:
        """
        Tries to return a Decimal.
        Returns the same value if failed and cls.raise_error is False
        """
        if not isinstance(val, str):
            return cls.raise_error_or_return_value(DataParseError, val)

        try:
            return Decimal(val)
        except InvalidOperation:
            return cls.parse_spanish_numeric_notation_to_decimal(val)

    @classmethod
    def parse_spanish_numeric_notation_to_decimal(cls, currency: str) -> str:
        pattern = re.compile(rf"^{cls.spanish_numeric_data}(?:\s?€)*$")

        if new_val := pattern.match(currency):
            val = new_val.group(1).replace(".", "").replace(",", ".")
            return cls.parse_string_to_decimal(val)

        return cls.raise_error_or_return_value(DataParseError, currency)

    @classmethod
    def parse_string_to_datetime(cls, string: str) -> datetime:
        """
        Turns "dd/mm/yy" or "dd/mm/yyyy" string into datetime object
        Returns the same value if failed and cls.raise_error is False

        """
        if not isinstance(string, str):
            return cls.raise_error_or_return_value(DataParseError, string)

        try:
            return cls.__if_datetime_is_dd_mm_yy(string)
        except DataParseError:
            return cls.__if_datetime_is_month_text_with_or_without_day(string)

    @classmethod
    def __if_datetime_is_dd_mm_yy(cls, val: str) -> datetime:
        # Expresion utilizada para encontrar fechas en (d|dd)/mm/(yy|yyyy)
        pattern = re.compile(r"^(?:\d{1,2}/){2}(\d{2}|\d{4})$")
        if pattern.match(val):
            len_year = len(pattern.match(val).group(1))
            if len_year == 2:
                # %y para años en centenas 00,01,..., 99
                return datetime.strptime(val, "%d/%m/%y")
            elif len_year == 4:
                # %Y para años en miles 2000,2001,...
                return datetime.strptime(val, "%d/%m/%Y")
            else:
                raise Exception(f"La fecha no se puede parsear por tener un numero de año inesperado.\nSe esperaba 2 o 4 caracteres y se introdujo {len_year}")

        raise DataParseError(val)

    @classmethod
    def __if_datetime_is_dd_mm_yy(cls, val: str) -> datetime:
        # Expresion utilizada para encontrar fechas en (d|dd)/mm/(yy|yyyy)
        pattern = re.compile(r"^(?:\d{1,2}/){2}(\d{2}|\d{4})$")
        if pattern.match(val):
            len_year = len(pattern.match(val).group(1))
            if len_year == 2:
                # %y para años en centenas 00,01,..., 99
                return datetime.strptime(val, "%d/%m/%y")
            elif len_year == 4:
                # %Y para años en miles 2000,2001,...
                return datetime.strptime(val, "%d/%m/%Y")
            else:
                raise Exception(f"La fecha no se puede parsear por tener un numero de año inesperado.\nSe esperaba 2 o 4 caracteres y se introdujo {len_year}")
        raise DataParseError(val)

    @classmethod
    def __if_datetime_is_month_text_with_or_without_day(
        cls,
        value: str,
    ) -> datetime:
        pattern = re.compile(r"(\d{1,2})?\s?([a-zA-Z]+)\s(\d{2}|\d{4})$")
        if not pattern.match(value):
            return cls.raise_error_or_return_value(DataParseError, value)

        try:
            day, month, year = pattern.search(value).groups()

            year = cls.convert_4_digits_year_into_integer(year)
            month = SpanishMonth[int](month.lower()).number
            day = cls.__get_last_day_month_integer(month, year) if day is None else int(day)

            return datetime(year, month, day)
        except KeyError:
            return cls.raise_error_or_return_value(DataParseError, value)
        except Exception as err:
            raise err

    @staticmethod
    def __get_last_day_month_integer(month: int, year: int) -> int:
        return calendar.monthrange(year, month)[1]

    @staticmethod
    def convert_4_digits_year_into_integer(year: str) -> int:
        n = len(year)
        if n == 4:
            return int(year)
        elif n == 2:
            return int(year) + 2000
        else:
            raise ValueError(year)

    @classmethod
    def parse_numeric_to_string(cls, num: NumericType, chr: str = "") -> str:
        """
        Parsea una variable de tipo float para agregarle:
            ',' como separador decimal
            ',' como separador de miles
            {<chr>} como cualquier caracter extra Eg, "€", "%", "$" ,etc...
        Returns the same value if failed and cls.raise_error is False

        """
        if not isinstance(num, NumericType):
            return cls.raise_error_or_return_value(DataParseError, num)

        data = f"{num:,.2f} {chr}" if chr else f"{num:,.2f}"
        return data.replace(",", ";").replace(".", ",").replace(";", ".")

    @classmethod
    def format_percentage(cls, value: NumericType) -> str:
        """
        Returns the same value if failed and cls.raise_error is False

        """
        if not isinstance(value, NumericType):
            return cls.raise_error_or_return_value(DataParseError, value)

        _value = Decimal(str(value))
        if not Decimal("0.00") <= abs(_value) <= Decimal("1.00"):
            return cls.raise_error_or_return_value(IndexError, value)

        return cls.parse_numeric_to_string(value * 100, chr="%")

    @classmethod
    def format_num_ppto(cls, num: NumericType) -> str:
        """
        Returns the same value if failed and cls.raise_error is False

        """
        if not isinstance(num, NumericType):
            return cls.raise_error_or_return_value(DataParseError, num)

        return cls.parse_numeric_to_string(num, chr="€")

    @classmethod
    def format_datetime(cls, date: datetime, size: DatetimeType = "short") -> str:
        """
        Returns the same value if failed and cls.raise_error is False

        """
        size_selector: dict[str, str] = {"short": "y", "long": "Y"}
        if not isinstance(date, datetime):
            return cls.raise_error_or_return_value(DataParseError, date)

        return date.strftime(f"%d/%m/%{size_selector[size]}")

    @classmethod
    def format_spanish_text_datetime(cls, date: datetime, size: DatetimeTypeNoDay = "short") -> str:
        """
        Returns the same value if failed and cls.raise_error is False

        """
        size_selector: dict[str, str] = {
            "short": lambda date: f"{date.day} {SpanishMonth[int](date.month).short} {date.year}",
            "long": lambda date: f"{SpanishMonth[int](date.month).large.capitalize()} {date.year}",
            "short_no_day": lambda date: f"{SpanishMonth[int](date.month).short} {date.year-2000}",
        }
        if not isinstance(date, datetime):
            return cls.raise_error_or_return_value(DataParseError, date)
        return size_selector[size](date)
