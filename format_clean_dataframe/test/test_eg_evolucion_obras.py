from pathlib import Path
import sys 
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))

from src.exercises.evolucion_obras.dataframe import EvolucionObrasDataFrameCreator  # noqa: E402


ruta= Path(__file__).parent/"datos_planificacion.csv"


print(pd.read_csv(ruta,delimiter=";"))
df = EvolucionObrasDataFrameCreator().create(ruta)
print(df)
df.to_excel("evolucion_obras.xlsx",index=False)
