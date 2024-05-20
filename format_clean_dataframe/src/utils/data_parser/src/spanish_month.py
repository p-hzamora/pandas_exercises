from typing import overload

LONG_MONTHS_DICC: dict[str, int] = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}

SHORT_MONTHS_DICC: dict[str, int] = {
    "ene": 1,
    "feb": 2,
    "mar": 3,
    "abr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "ago": 8,
    "sept": 9,
    "oct": 10,
    "nov": 11,
    "dic": 12,
}

INT_MONTHS_DICC: dict[int, str] = {
    1: {"large": "enero", "short": "ene"},
    2: {"large": "febrero", "short": "feb"},
    3: {"large": "marzo", "short": "mar"},
    4: {"large": "abril", "short": "abr"},
    5: {"large": "mayo", "short": "may"},
    6: {"large": "junio", "short": "jun"},
    7: {"large": "julio", "short": "jul"},
    8: {"large": "agosto", "short": "ago"},
    9: {"large": "septiembre", "short": "sept"},
    10: {"large": "octubre", "short": "oct"},
    11: {"large": "noviembre", "short": "nov"},
    12: {"large": "diciembre", "short": "dic"},
}

large_str = str
short_str = str


class SpanishMonth[T]:
    # region Private method
    @overload
    def __init__(self, month: int) -> None: ...

    @overload
    def __init__(self, month: large_str) -> None: ...

    @overload
    def __init__(self, month: short_str) -> None: ...

    def __init__(self, month: T) -> None:
        self.__valid_and_set_number(month)

    def __valid_and_set_number(self, _number: T) -> bool:
        if self.__valid_number(_number):
            self._number: T = _number
        elif self.__valid_long(_number):
            self._number: T = LONG_MONTHS_DICC[_number]
        else:
            self._number: T = SHORT_MONTHS_DICC[_number]

    def __valid_number(self, value: int) -> bool:
        if isinstance(value, int):
            if value not in range(1, 13):
                raise IndentationError(f"Number month '{value}' is not valid. It must be between 1 and 12")
            return True
        return False

    def __valid_long(self, value: str) -> bool:
        if isinstance(value, str) and value in LONG_MONTHS_DICC:
            return True
        return False

    def __get_month(self, key: int):
        return INT_MONTHS_DICC[key]

    # endregion

    # region Properties
    @property
    def number(self):
        return self._number

    @property
    def short(self) -> str:
        return self.__get_month(self.number)["short"]

    @property
    def large(self) -> str:
        return self.__get_month(self.number)["large"]

    # endregion
