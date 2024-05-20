from collections import defaultdict
from datetime import datetime

import pandas as pd
from pathlib import Path
from src.utils.data_parser import SpanishMonth

from .col_planificacion import Cols
from src.utils.get_df import get_df

class EvolucionObrasDataFrameCreator():
    @staticmethod
    def create(path:Path|str) -> pd.DataFrame:
        df_orig = get_df(path=path)

        cols = [Cols.mes, Cols.fecha_visita]

        months: dict[str, int] = {
            "ene": 0,
            "feb": 1,
            "mar": 2,
            "abr": 3,
            "may": 4,
            "jun": 5,
            "jul": 6,
            "ago": 7,
            "sept": 8,
            "oct": 9,
            "nov": 10,
            "dic": 11,
        }

        condition = df_orig[Cols.n].notna()
        df_orig = df_orig.loc[condition, cols].dropna().reset_index(drop=True)

        if df_orig.empty:
            return df_orig

        last_visit_date: datetime = df_orig[Cols.fecha_visita].iat[-1].to_pydatetime()
        # TODOL to implement spanish date class
        format_last_visit_date: str = f"{last_visit_date.day} de {SpanishMonth[str](last_visit_date.month).large} de {last_visit_date.year}"

        # If there's only one year in ColName.mes add next year to better visualitation
        df_orig["year"] = df_orig[Cols.mes].apply(lambda x: x.year).astype(int)
        df_orig["month"] = df_orig[Cols.mes].apply(lambda x: SpanishMonth(x.month).short).astype(str)
        df_orig[Cols.fecha_visita] = df_orig[Cols.fecha_visita].apply(lambda x: x.strftime("%d/%m")).astype(str)
        df_orig["informe"] = "PCex"

        list_year: list[int] = list(set(df_orig.year))
        if len(list_year) == 1:
            list_year.append(list_year[-1] + 1)

        dict_year = defaultdict(list)
        for y in list_year:
            if y not in df_orig.year.values:
                dict_year[y] = []
                continue
            for _, row in df_orig.iterrows():
                year = row.year
                month = row.month
                dict_year[year].append(month)

        list_dataframe: list[pd.DataFrame] = []
        column_names = ["year", "month", "informe", Cols.fecha_visita]

        for year, list_months in dict_year.items():
            new_df = pd.DataFrame(columns=column_names)
            for month in months:
                if month not in list_months:
                    new_df.loc[len(new_df)] = [year, month, "", ""]
                else:
                    temp_df: pd.DataFrame = df_orig[(df_orig.year == year) & (df_orig.month == month)][column_names]
                    if (n := len(temp_df)) != 1:
                        raise Exception(f"Solo debe haber un mes por año.Se obtuvieron {n}")
                    # accedo por posicion en vez de por Index porque cada iteracion eligira una fila diferente
                    new_df.loc[len(new_df)] = temp_df.iloc[0]

            new_df["month_num"] = new_df.month.map(months)

            df_sorted = new_df.sort_values(by=["year", "month_num"]).set_index("month")[["informe", Cols.fecha_visita]].T
            df_sorted.insert(0, "", ["", year])
            list_dataframe.append(df_sorted)

        lista = ["Ultima visita realizada", "", format_last_visit_date]
        lista.extend([""] * (list_dataframe[0].columns.size - len(lista)))
        last_row = pd.Series(lista, index=list_dataframe[0].columns).to_frame().T
        empty_row = pd.Series([""] * len(lista), index=list_dataframe[0].columns).to_frame().T
        final_df = pd.concat([x for x in list_dataframe])
        final_df = pd.concat([final_df, empty_row, last_row], axis=0).reset_index(drop=True)

        final_df.loc[-1] = final_df.columns
        final_df.index += 1
        final_df.sort_index(inplace=True)

        return final_df.map(lambda x: str(x))
