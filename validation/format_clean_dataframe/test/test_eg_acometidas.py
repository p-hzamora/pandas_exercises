from pathlib import Path
import sys 
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))

from src.exercises.acometidas.dataframe import AcometidasDataFrameCreator  # noqa: E402

ruta= Path(__file__).parent/"data.csv"

print(pd.read_csv(ruta,delimiter=";"))
df = AcometidasDataFrameCreator().create(ruta)
print(df)
df.to_excel("evolucion_obras.xlsx",index=False)
