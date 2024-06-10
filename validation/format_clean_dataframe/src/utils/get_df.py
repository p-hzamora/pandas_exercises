import pandas as pd
from pathlib import Path
import re
import numpy as np
from src.utils.data_parser import DataClean




def get_df(path: str | Path = None, delimiter=";", *args, **kwargs) -> pd.DataFrame:
    df: pd.DataFrame = pd.read_csv(
        path, encoding="utf-8", delimiter=delimiter, dtype="str", *args, **kwargs
    )

    # limpiar nombres de columnas en caso de que estos sean str
    if df.columns.dtype == np.dtype("O"):
        df.columns = [re.sub(r"[\n]", " ", x.strip()) for x in df.columns]
    # limpiar datos
    df = df.map(DataClean.apply)

    return df
