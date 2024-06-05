from abc import ABC, abstractmethod
from typing import override


class ICleanData(ABC):
    @abstractmethod
    def clean_data(data: str) -> str:
        pass

class ReplaceSIbyFilledCircle(ICleanData):
    @staticmethod
    @override
    def clean_data(data: str) -> str:
        return data.replace("SÍ", "●")

class ReplaceNObyHollowCircle(ICleanData):
    @staticmethod
    @override
    def clean_data(data: str) -> str:
        return data.replace("NO", "○")

class ReplaceHypenbyDoubleAt(ICleanData):
    @staticmethod
    @override
    def clean_data(data: str) -> str:
        return data.replace("-", "@@")
    
class ReplaceNoProcedebyHyphen(ICleanData):
    @staticmethod
    @override
    def clean_data(data: str) -> str:
        return data.replace("No procede", "-")    

class CleanData:
    
    validators: tuple[ICleanData] = (
        ReplaceSIbyFilledCircle,
        ReplaceNObyHollowCircle,
        ReplaceHypenbyDoubleAt, 
        ReplaceNoProcedebyHyphen,
    )

    @classmethod
    def apply(cls, data: str) -> str:
        for validator in cls.validators:
            data = validator.clean_data(data)   
        return data


if __name__ == '__main__':
    data = ['SÍ', 'NO', 'NO', 'No procede', '-', 'SI', 'NO', 'NO', 'SÍ', 'no']

    print(f'Original data: {data}')
    
    for d in data:
        print(CleanData.apply(d))
    
    print(f'Cleaned data: {data}')
