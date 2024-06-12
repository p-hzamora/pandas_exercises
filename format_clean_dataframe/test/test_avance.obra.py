from datetime import datetime
from typing import Any, Literal
from format_clean_dataframe.src.utils.data_parser.src.data_parser import DataParser
from format_clean_dataframe.src.utils.data_parser.src.spanish_month import (
    INT_MONTHS_DICC,
)
from src.utils.get_df import get_df
import pandas as pd
from decimal import Decimal
from pathlib import Path
import re


class Cols:
    letra = "Letra"
    supercapitulo = "SUPERCAPITULO"
    n = "N"
    capitulo = "CAPITULO"
    cod = "Cod"
    subcapitulo = "SUBCAPITULO"
    tipo_de_trabajo = "TIPO DE TRABAJO"
    ppto_al_ini = "Presupuesto al inicio"
    ppto_1 = "Variante Presupuesto 1"
    ppto_2 = "Variante Presupuesto 2"
    ppto_3 = "Variante Presupuesto 3"
    ppto_actualizado = "Presupuesto Actualizado"
    desviacion = "Desviación"
    certificado = "Certificado"
    pct_certificado = "% Certificado"
    pendiente_de_certificar = "Pendiente de Certificar"
    pct_pendiente = "% Pendiente"
    planificación = "Planificación"
    coste_obra = "Coste de Obra"


def parse_date(
    text: str,
    year_mode: Literal["%y", "%Y"],
    month_mode: Literal["short", "large"],
    day: bool,
) -> datetime | Any:
    if not isinstance(text, str):
        return text
    text = text.replace(" ", "-")
    for key, value in INT_MONTHS_DICC.items():
        text = text.replace(value[month_mode], str(key).zfill(2))
    if day:
        return datetime.strptime(text, f"%d-%m-{year_mode}")
    else:
        return datetime.strptime(text, f"%m-{year_mode}")


def calculate_pct(x: Decimal, y: Decimal):
    if y == Decimal("0"):
        result = Decimal("0")
    else:
        result = x / y
    return round(result, 4)


def format_pct(x: Decimal):
    """
    Given a pct in the range [0-1]
    returns a str like "1,00 %"
    """
    if not isinstance(x, Decimal):
        return x
    x = x * 100
    x = f"{x:,.2f} %".replace(".", ",")
    return x


def create(self):
    cols = [
        Cols.ppto_al_ini,
        Cols.ppto_actualizado,
        Cols.desviacion,
        Cols.certificado,
        Cols.pct_certificado,
        Cols.pendiente_de_certificar,
        Cols.pct_pendiente,
    ]

    t_trabajo_obra_presupcerti_certificacion: Path = Path(r"rutas")
    t_trabajo_facturas_promocion_introduccion: Path = Path(r"rutas")

    # region data initialization
    dopc = get_df(path=t_trabajo_obra_presupcerti_certificacion)
    difp = get_df(path=t_trabajo_facturas_promocion_introduccion)
    df_data = dopc.copy()
    # endregion

    # region data cleaning
    df_data[Cols.letra] = df_data[Cols.letra] + " " + df_data[Cols.supercapitulo]
    df_data[Cols.capitulo] = df_data[Cols.n].astype(str) + " " + df_data[Cols.capitulo]
    # endregion

    total_group:pd.DataFrame = df_data.groupby(Cols.letra)[cols].sum()
    total = total_group.sum()

    # pasamos la Serie a un dataframe con un index concreto, por eso no  uso .to_frame()
    total: pd.DataFrame = pd.DataFrame({"TOTAL": total}).T
    df_to_concat: list[pd.DataFrame] = []
    # bucle a lo largo del numero de letras distintas que haya. Conseguimos una lista agregando el df con la suma de subcapitulos y el los df de subcapitulos
    for letra in df_data[Cols.letra].unique():
        # total df
        df_to_concat.append(total_group.loc[letra, :].to_frame().T)
        # agrupar por capitulo, obtener la posicion de cada fila y ordenarlos
        df_capitulos: pd.DataFrame = (
            df_data[df_data[Cols.letra] == letra].groupby(Cols.capitulo).sum()
        )
        df_capitulos["index"] = [
            int(re.search(r"(\d+)", x.split(" ")[0]).group(1))
            for x in df_capitulos.index.tolist()
        ]
        df_to_concat.append(df_capitulos.sort_values("index")[cols])

    # agregar fila de totales (totales de totales)
    df_to_concat.append(total)

    df_final = pd.concat(axis=0, objs=df_to_concat)

    df_final[Cols.pct_certificado] = df_final.apply(
        lambda x: calculate_pct(x=x[Cols.certificado], y=x[Cols.ppto_actualizado]),
        axis=1,
    )
    df_final[Cols.pct_pendiente] = df_final.apply(
        lambda x: calculate_pct(
            x=x[Cols.pendiente_de_certificar], y=x[Cols.ppto_actualizado]
        ),
        axis=1,
    )

    # agregar titulos de filas
    df_final = df_final.reset_index(names=["Coste de Obra"])
    # agregar titulos de columnas
    df_final.loc[-1] = df_final.columns
    df_final.index = df_final.index + 1
    df_final = df_final.sort_index()

    # region process data for total rows
    contratista_principal_nombre = dopc.loc[dopc.Letra == "A", "SUPERCAPITULO"].values[
        0
    ]
    contratista_principal_presup_inicio_numeric = total_group.loc[
        f"A {contratista_principal_nombre}", "Presupuesto al inicio"
    ]
    contratista_principal_desviacion_numeric = total_group.loc[
        f"A {contratista_principal_nombre}", Cols.desviacion
    ]
    contratista_principal_monetario = DataParser.parse_numeric_to_string(
        contratista_principal_presup_inicio_numeric,
        chr="€",
    )
    descripcion_presup_contrata_inicial = (
        f"Presup. Contrata Inicial firmado: {contratista_principal_monetario}"
        if contratista_principal_nombre == "CONTRATISTA PRINCIPAL"
        else f"Presup. {contratista_principal_nombre} Inicial: {contratista_principal_monetario}"
    )
    current_month: datetime = datetime.now()
    current_month = datetime(current_month.year, current_month.month, 1)
    difp.Mes = difp.Mes.apply(parse_date, year_mode="%y", month_mode="short", day=False)
    previously_certified_value = difp.loc[
        (difp.GRUPO == "OBRA") & (difp.Mes < current_month), "B.I. / CERTIFICACIÓN"
    ].sum()
    total_updated_budget_value = total.loc["TOTAL", "Presupuesto Actualizado"]
    total_certified_value = total.loc["TOTAL", Cols.certificado]
    previously_certified_pct_value = calculate_pct(
        previously_certified_value, total_updated_budget_value
    )
    desviacion_pct_value = calculate_pct(
        contratista_principal_desviacion_numeric,
        contratista_principal_presup_inicio_numeric,
    )
    desviacion_pct = format_pct(desviacion_pct_value)
    descripcion_desviacion = f"% Desviación s/Presup. Inicial: {desviacion_pct}"
    desviacion_s_presup_ini_certified_value = (
        total_certified_value - previously_certified_value
    )
    desviacion_s_presup_ini_pct_certified_value = calculate_pct(
        desviacion_s_presup_ini_certified_value, total_updated_budget_value
    )
    # endregion

    # agregar % Desviación s/ Presup. Inicial
    df_final.loc[df_final.shape[0]] = [
        descripcion_presup_contrata_inicial,
        "Certificado anteriormente",
        "",
        "",
        previously_certified_value,
        previously_certified_pct_value,
        "",
        "",
    ]
    df_final.loc[df_final.shape[0]] = [
        descripcion_desviacion,
        "TOTAL Certificado mes",
        "",
        "",
        desviacion_s_presup_ini_certified_value,
        desviacion_s_presup_ini_pct_certified_value,
        "",
        "",
    ]

    return df_final.fillna("")
