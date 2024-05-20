from pathlib import Path
import sys 
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))

from src.exercises.acometidas.dataframe import AcometidasDataFrameCreator  # noqa: E402

ruta= r"C:\Users\phzam\pandas_exercises\format_clean_dataframe\src\exercises\acometidas\data.csv"

print(pd.read_csv(ruta,delimiter=";"))
df = AcometidasDataFrameCreator().create(ruta)
df.to_excel("evolucion_obras.xlsx",index=False)
