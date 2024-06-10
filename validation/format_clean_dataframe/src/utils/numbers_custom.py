import re
from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import unidecode

from utils.data_parser import DataClean


class ILoadPaths(ABC):
    @abstractmethod
    def load(path: Path): ...

    @staticmethod
    def _parse_name(_name: str):
        # modificar name con lo que necesitemos
        name = unidecode.unidecode(_name)
        return name


class LoadCSVPaths(ILoadPaths):
    @classmethod
    def load(cls, path: Path) -> defaultdict[list]:
        """
        Funcion utilizada para mapear todos los .csv de la carpeta especificada y acceder a sus correspondientes rutas
        """
        table_dicc = defaultdict(dict)
        numbers_path: Path = path

        for paths in numbers_path.rglob(r"[^~].+\.csv$"):
            first, second = paths.stem.split("-", maxsplit=1)
            first = cls._parse_name(first)
            second = cls._parse_name(second)
            table_dicc[first][second] = paths

        return table_dicc


class LoadPaths(object):
    @staticmethod
    def load(path: Path) -> defaultdict[list]:
        return LoadCSVPaths.load(path)


class Numbers(object):
    NUMBERS_TABLES = None
    CSV_PATH = None

    def __new__(cls, path: Path):
        cls.CSV_PATH: Path = path
        return object.__new__(cls)

    @classmethod
    def get_dict(cls, path: str = None, *args, **kwargs) -> dict:
        """
        Funcion enfocada a la creacion de diccionarios pasando por argumento tanto el nombre de la pestaña como el nombre de la tabla.

        Ambos datos los buscara en la variable que almacena todas las tablas que hay en numbers "NUMBERS_TABLE"

        Obtiene el dataframe de la tabla y busca las columnas  "ETIQUETA DATO REQUERIDO" "DATO PROMOCION"

        args.
                to_dict: dict = None
                path:str|Path= None
                sheet_name:str= None
                table_name:str= None
        """

        df = cls.get_df(path=path, *args, **kwargs).fillna("")
        df_filter = df[
            (df["ETIQUETA DATO REQUERIDO"].str.contains(r"^\{.+\}$", regex=True))
            & (df["ETIQUETA DATO REQUERIDO"].notna())
        ]

        # quitamos '{' y '}' del nombre de la funcion
        df_filter.index = df_filter["ETIQUETA DATO REQUERIDO"].apply(
            lambda x: re.sub(r"[\{\}]", "", x)
        )

        # Eliminar caracteres extraños que se hayan podido obtener al leer el .numbers
        dicc = df_filter["DATO PROMOCION"].to_dict()
        new_dicc = {}
        not_valid = ".,"
        for key, val in dicc.items():
            if re.search(not_valid, key):
                key = re.sub(not_valid, "", key)
            # NOTE: 2024-02-27 commented code because it was deleting \n and we want them in the key value dict
            # if isinstance(val, str):
            #     val = " ".join(val.split())
            new_dicc[key] = val
        return new_dicc

    @classmethod
    def get_df(
        cls,
        to_dict: dict = None,
        path: str | Path = None,
        sheet_name: str = None,
        table_name: str = None,
        delimiter=";",
        *args,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Funcion que retorna un dataframe del csv que se desee. Para ello se le puede pasar una ruta directamente o el nombre de la pestaña y el nombre de la tabla por parametro

        args.
            path. Ruta del csv directamente, sirve para los casos que queramos obtener el df de self._dg_path o self._ce_paht
        """
        if path is None and isinstance(to_dict, dict):
            sheet_name, table_name = tuple(to_dict.items())[
                0
            ]  # COMENT: Must be one unique value in "to_dict" val

            try:
                if not cls.NUMBERS_TABLES:
                    cls.NUMBERS_TABLES = LoadPaths.load(cls.CSV_PATH)
                path = cls.NUMBERS_TABLES[sheet_name][table_name]
            except KeyError as e:
                raise Exception(f"Clave {e} no existente en el diccionario de .csv")

        if isinstance(path, str):
            path = cls.CSV_PATH / path
        df: pd.DataFrame = pd.read_csv(
            path, encoding="utf-8", delimiter=delimiter, dtype="str", *args, **kwargs
        )

        # limpiar nombres de columnas en caso de que estos sean str
        if df.columns.dtype == np.dtype("O"):
            df.columns = [re.sub(r"[\n]", " ", x.strip()) for x in df.columns]
        # limpiar signo "\ax0€"
        df = df.map(DataClean.apply)

        return df


class CSVMapped:
    @staticmethod
    def create_map(ini_path: Path):
        def clean_data(val: str) -> str:
            pattern = re.compile(r"^(\d+_?\d*_?)")  # 00_1_REPORTE o 05_reporte

            data = re.sub(r"[\s\.\-/\\]", "_", val.strip())

            if coin := pattern.search(data):
                preffix = coin.group(1)
                data = data.removeprefix(preffix) + "_" + preffix.removesuffix("_")

            return data

        dicc: dict[str, dict[str, Path]] = LoadCSVPaths.load(ini_path)
        # create .py
        path = Path(__file__).parent / "number_mapped.py"
        if not path.exists():
            path.touch()

        # create class per existing sheet
        with open(str(path), "w", encoding="utf-8") as o_file:
            # add var inside class per existing table
            for sheet_name, tables in dicc.items():
                class_name = f"\n\n\nclass {clean_data(sheet_name.upper())}:"
                o_file.write(class_name)

                for table_name, path in tables.items():
                    line = f'\n\t{clean_data(table_name.lower())} = "{path.name}"'
                    o_file.write(line)
