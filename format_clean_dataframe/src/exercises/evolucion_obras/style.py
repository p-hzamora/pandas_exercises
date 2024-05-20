from typing import override

import numpy as np
from pandas.core.api import DataFrame as DataFrame
from scripts.extensions.api_word.src.word_styles import _Border as Border
from scripts.extensions.api_word.src.word_styles import WordStyles
from scripts.extensions.api_word import WordDocument
from scripts.styles.read_table import ReadTable

from ...styles.read_table import TableType
from ...styles.add_table import StyleCreator


class EvolucionObrasStyleCreator(StyleCreator):
    def __init__(
        self,
        docx_tpl: WordDocument,
        dataframe: DataFrame,
        style: ReadTable = TableType.common_stc,
    ) -> None:
        super().__init__(docx_tpl, dataframe, style)

    @override
    def apply(self) -> None:
        if self.df.empty:
            self._docx.add_table(self.df, "EVOLUCION_OBRA")
            return None
        all_cols = np.array(range(self.df.columns.size))
        last_row = self.df.shape[0] - 1
        year_row = self.df[~self.df[""].str.contains(r"^$", regex=True)].index.to_numpy()
        informe_row = year_row - 1
        self._docx.add_table(self.df, "EVOLUCION_OBRA")
        eo = self._docx.EVOLUCION_OBRA

        # estilo para filas de anno y primer fila desde col 1 hasta adelante
        s_grey_4 = WordStyles.to_base({"size": 7})
        s_grey_4.text.font = "MuseoSans-300"
        s_grey_4.text.color.key = "GREY_4"
        s_grey_4.text.position.horizontal = "right"
        s_grey_4.text.position.vertical = "center"
        eo.style_table_range([0] + year_row.tolist(), all_cols[1:], s_grey_4)

        # estilo para filas del nombre del informe
        s = WordStyles.to_base({"size": 7})
        s.text.font = "Museo 500"
        s.text.color.key = "BLUE_2"
        s.text.position.horizontal = "right"
        Border.add(s.border, "bottom", attrib={"grosor": 2, "tipo": "-", "color": "GREY_4"})
        eo.style_table_range(informe_row[:-1], all_cols[1:], s)

        # estilo para filas de anno y ultima visita y col 0
        s = WordStyles.to_base({"size": 7})
        s.text.color.key = "BLUE_2"
        s.text.font = "Museo 700"
        s.text.position.horizontal = "left"
        eo.style_table_range(year_row, 0, s)

        # estilo para evitar colorear las fechas de la columna 1 con el estio de la ultima linea
        eo.style_table_range(last_row, 1, s)
        # estilo para fecha ultima visita realizada
        s_grey_4.text.position.horizontal = "left"
        eo.style_table_range(last_row, [2, 5], s_grey_4)

        # region apply width
        widths = {
            18: all_cols,
        }
        for value, cols in widths.items():
            eo.style_table_range(list(range(last_row + 1)), cols, {"width": value})
        # endregion

        eo.merge_cells((last_row, 0), (last_row, 1))
        eo.merge_cells((last_row, 1), (last_row, 4))
        eo.apply_style()
