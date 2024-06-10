import pandas as pd
import numpy as np
from pathlib import Path
from typing import Self
from .enum_cols import FileCols, NewCols
from .logger_decorator import logger 

class Tasks:

    def __init__(self, path: Path):
        self.df: pd.DataFrame
        self.path: Path = path


    @logger
    def load_data(self) -> "Tasks":
        """
        Load data from a CSV file and return it as a pandas DataFrame.

        Returns:
            df (pandas.DataFrame): The loaded data as a DataFrame.
        """

        self.df = pd.read_csv(self.path, sep=";", dtype=str)
        return self


    @logger
    def replace_values(self) -> Self:
        """
        Replaces specific values in the given DataFrame with predefined replacements.

        Args:
            df (pd.DataFrame): The DataFrame to be modified.

        Returns:
            None
        """

        cols: list[str] = [
            FileCols.SOLICITUD_DE_PAGO.value,
            FileCols.EJECUTADO.value,
            FileCols.REGISTRO_CONFORME.value,
        ]

        replacements: dict[str, str] = {
            "SÍ": "●",
            "NO": "○",
            "-": "@@",
            "No procede": "-",
        }

        func = np.vectorize(lambda x: replacements.get(x, x))
        self.df[cols] = func(self.df[cols])

        # for col in cols:
        #     df[col] = df[col].replace(replacements)

        return self


    @logger
    def replace_headers(self) -> Self:
        """
        Replaces columns headers in the given DataFrame with predefined replacements.

        Args:
            df (pd.DataFrame): The DataFrame to be modified.

        Returns:
            None
        """

        replacements: dict[str, str] = {
            FileCols.SOLICITUD_DE_PAGO.value: NewCols.SOLICITUD_DE_PAGO.value,
            FileCols.EJECUTADO.value: NewCols.EJECUTADO.value,
            FileCols.REGISTRO_CONFORME.value: NewCols.REGISTRO_CONFORME.value,
            FileCols.FECHA_ULTIMO_DOC.value: NewCols.FECHA_ULTIMO_DOC.value,
            FileCols.EMPRESA.value: NewCols.EMPRESA.value,
            FileCols.OBSERVACIONES.value: NewCols.OBSERVACIONES.value,
        }

        self.df.rename(columns=replacements, inplace=True)
        return self


    @logger
    def add_blank_rows(self, ntimes: int) -> Self:
        """
        Adds n blank rows to the given DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame to be modified.

        Returns:
            None
        """

        for _ in range(ntimes):
            self.df.loc[len(self.df)] = ""

        return self


    @logger
    def add_observation_row(self) -> Self:
        """
        Adds observation rows to the given DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame to be modified.

        Returns:
            None
        """

        self.df.iloc[-1, 0] = FileCols.OBSERVACIONES.value + ":"
        return self

