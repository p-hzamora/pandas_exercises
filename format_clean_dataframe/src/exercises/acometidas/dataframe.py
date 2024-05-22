import pandas as pd
from .columns import Cols
from src.utils.get_df import get_df
from pathlib import Path
class AcometidasDataFrameCreator():
    def __init__(self) -> None:
        ...

    @classmethod
    def create(cls,ruta:Path|str) -> pd.DataFrame:
        df = get_df(path=ruta)
        cls.add_title_rows(df)
        cls.translate(df)
        df = df.fillna("").reset_index(drop=True)

        # Agregar espacio para separar de observaciones
        df.loc[df.shape[0]] = ""
        df.loc[df.shape[0]] = ""
        df.iloc[-1, 0] = r"Observaciones adicionales de la tabla" 

        return df

    @staticmethod
    def add_title_rows(df: pd.DataFrame):
        df.loc[-1] = Cols.get_all_cols()
        df.index += 1
        df.sort_index(inplace=True)
        df.iat[0, 0] = "Acometidas"

    @staticmethod
    def translate(df: pd.DataFrame) -> None:
        dicc: dict[str, str] = {
            "SI": "●",
            "NO": "○",
            "-": "@@",
            "No procede": "-",
        }

        cols_to_translate:list[str] = [Cols.solicitud, Cols.ejecutado,Cols.registro] 
        for cols in cols_to_translate:
            df[cols] = df[cols].apply(lambda x: dicc.get(x,x))
