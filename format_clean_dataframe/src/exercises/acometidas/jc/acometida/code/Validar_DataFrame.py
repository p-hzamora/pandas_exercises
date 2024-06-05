import pandas as pd
import numpy as np
import re
import time
from functools import wraps
from enum import Enum

class eCols(Enum):
    COLUMNA = 'Columna'
    CONDICION = 'Condicion'
    TIPO_DE_ERROR = 'Tipo_de_Error'
    INDICES = 'Indices'
    EXPRESION = 'Expresion'
    NUM_ERRORES = 'Num_errores'
    TIEMPO = 'Tiempo'
    PCT_TIEMPO = 'Pct_tiempo'

class eMsg(Enum):
    NO_NULO = 'no_nulo'
    RANGO = 'rango'
    ERROR_DE_TIPO = 'Error de tipo'
    VALORES_PERMITIDOS = 'valores_permitidos'
    REGEX = 'regex'
    FORMATO_FECHA = 'formato_fecha'
    RANGO_FECHA = 'rango_fecha'
    TIENE_VALORES_NULOS = 'Tiene valores nulos'
    FUERA_DEL_RANGO = 'Fuera del rango'
    ERROR_DE_TIPO_MSG = 'Error de tipo'
    VALORES_NO_PERMITIDOS = 'Contiene valores no permitidos'
    NO_CUMPLE_PATRON = 'No cumple patrón'
    NO_CUMPLE_FORMATO = 'No cumple formato'
    NO_CUMPLE_RANGO = 'No cumple rango'

def medir_tiempo(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        result = func(self, *args, **kwargs)
        end_time = time.time()
        tiempo = end_time - start_time
        # Obtener información para agregar a resultados
        columna, condicion, tipo_de_error, indices, expresion = result
        self.agregar_resultado(columna, condicion, tipo_de_error, indices, expresion, tiempo)
        return self
    return wrapper

class ValidadorDataFrame:
    def __init__(self, df):
        self.df = df
        self.resultados = pd.DataFrame(columns=[
            eCols.COLUMNA.value, eCols.CONDICION.value, eCols.TIPO_DE_ERROR.value,
            eCols.INDICES.value, eCols.EXPRESION.value, eCols.NUM_ERRORES.value,
            eCols.TIEMPO.value, eCols.PCT_TIEMPO.value
        ])
    
    def agregar_resultado(self, columna, condicion, tipo_de_error, indices, expresion, tiempo):
        if len(indices) > 5:
            indices_str = indices[:5] + ['...']
        else:
            indices_str = indices
        nuevo_resultado = pd.DataFrame({
            eCols.COLUMNA.value: [columna],
            eCols.CONDICION.value: [condicion],
            eCols.TIPO_DE_ERROR.value: [tipo_de_error],
            eCols.INDICES.value: [indices_str],
            eCols.EXPRESION.value: [expresion],
            eCols.NUM_ERRORES.value: [len(indices)],
            eCols.TIEMPO.value: [round(tiempo * 1000, 0)],  # Convertir a milisegundos sin decimales
            eCols.PCT_TIEMPO.value: [0.0]  # Esto se actualizará después
        })
        self.resultados = pd.concat([self.resultados, nuevo_resultado], ignore_index=True)
    
    @medir_tiempo
    def validar_no_nulo(self, columna):
        indices = self.df.index[self.df[columna].isnull()].tolist()
        tipo_de_error = eMsg.TIENE_VALORES_NULOS.value if indices else ''
        return columna, eMsg.NO_NULO.value, tipo_de_error, indices, ''
    
    @medir_tiempo
    def validar_rango(self, columna, min_val, max_val):
        indices = self.df.index[~self.df[columna].between(min_val, max_val)].tolist()
        expresion = f'{min_val}-{max_val}'
        tipo_de_error = eMsg.FUERA_DEL_RANGO.value if indices else ''
        return columna, eMsg.RANGO.value, tipo_de_error, indices, expresion
    
    @medir_tiempo
    def validar_tipo(self, columna, tipo):
        indices = self.df.index[~self.df[columna].apply(lambda x: isinstance(x, tipo))].tolist()
        expresion = f'{tipo}'
        tipo_de_error = eMsg.ERROR_DE_TIPO_MSG.value if indices else ''
        return columna, eMsg.ERROR_DE_TIPO.value, tipo_de_error, indices, expresion
    
    @medir_tiempo
    def validar_valores_permitidos(self, columna, valores_permitidos):
        indices = self.df.index[~self.df[columna].isin(valores_permitidos)].tolist()
        expresion = f'{valores_permitidos}'
        tipo_de_error = eMsg.VALORES_NO_PERMITIDOS.value if indices else ''
        return columna, eMsg.VALORES_PERMITIDOS.value, tipo_de_error, indices, expresion
    
    @medir_tiempo
    def validar_regex(self, columna, patron):
        regex = re.compile(patron)
        indices = self.df.index[~self.df[columna].apply(lambda x: regex.match(str(x)) is not None)].tolist()
        expresion = f'{patron}'
        tipo_de_error = eMsg.NO_CUMPLE_PATRON.value if indices else ''
        return columna, eMsg.REGEX.value, tipo_de_error, indices, expresion
    

    @medir_tiempo
    def validar_formato_fecha(self, columna, formato):

        self.df[columna] = pd.to_datetime(self.df[columna], format=formato, errors='coerce')
        fecha_validas = self.df[columna].notna()

        indices = self.df[~(fecha_validas)].index.tolist()

        expresion = f'{formato}'
        tipo_de_error = eMsg.NO_CUMPLE_FORMATO.value if len(indices) else ''
        return columna, eMsg.FORMATO_FECHA.value, tipo_de_error, indices, expresion



    @medir_tiempo
    def validar_rango_fecha(self, columna, formato, min_fecha=None, max_fecha=None):
        
        min_fecha_dt = pd.to_datetime(min_fecha) if min_fecha else None
        max_fecha_dt = pd.to_datetime(max_fecha) if max_fecha else None

        self.df[columna] = pd.to_datetime(self.df[columna], format=formato, errors='coerce')
        fecha_validas = self.df[columna].notna()
        fecha_en_rango = (self.df[columna] >= min_fecha_dt) & (self.df[columna] <= max_fecha_dt)
        

        indices = self.df[~(fecha_validas & fecha_en_rango)].index.tolist()

        expresion = f'{min_fecha} - {max_fecha}'
        tipo_de_error = eMsg.NO_CUMPLE_RANGO.value if len(indices) else ''
        return columna, eMsg.RANGO_FECHA.value, tipo_de_error, indices, expresion
    
   
    def obtener_resultados(self):
        tiempo_total = self.resultados[eCols.TIEMPO.value].sum()
        self.resultados[eCols.PCT_TIEMPO.value] = (self.resultados[eCols.TIEMPO.value] / tiempo_total * 100).round(2)
        fila_total = pd.DataFrame({
            eCols.COLUMNA.value: [''],
            eCols.CONDICION.value: [''],
            eCols.TIPO_DE_ERROR.value: [''],
            eCols.INDICES.value: [''],
            eCols.EXPRESION.value: [''],
            eCols.NUM_ERRORES.value: [''],
            eCols.TIEMPO.value: [round(tiempo_total, 0)],
            eCols.PCT_TIEMPO.value: [100.00]
        })
        self.resultados = pd.concat([self.resultados, fila_total], ignore_index=True)
        return self.resultados

# Ejemplo de uso:




# Suponemos que ValidadorDataFrame está definida y disponible aquí.

def test_validador_dataframe():
    # Crear un DataFrame con 10,000,000 de registros
    num_registros = 1_000_000
    data = {
        'edad': np.random.randint(10, 70, size=num_registros).astype(float),  # Algunas edades fuera de rango
        'salario': np.random.randint(30000, 90000, size=num_registros),
        'nombre': np.random.choice(['Ana', 'Juan', 'Pedro', 'Luis', 'María'], size=num_registros),
        'email': np.random.choice(['ana@example.com', 'juan@example.com', 'pedro@sample.com', 'invalid-email', 'maria@example.com'], size=num_registros),
        'fecha_ingreso': np.random.choice(['01/01/2020', '29/03/2021', '20/07/2022', '30/12/2023'], size=num_registros)
    }

    df = pd.DataFrame(data)
    
    # Introducir algunos valores nulos
    df.loc[np.random.choice(df.index, size=1000, replace=False), 'edad'] = np.nan

    # Introducir algunos valores fuera del rango de fechas
    df.loc[np.random.choice(df.index, size=1000, replace=False), 'fecha_ingreso'] = '32/13/2020'

    # Iniciar el temporizador
    start_time = time.time()

    # Validar el DataFrame
    validador = ValidadorDataFrame(df)
    validador.validar_no_nulo('edad') \
             .validar_rango('edad', 20, 60) \
             .validar_tipo('edad', int) \
             .validar_rango('salario', 40000, 80000) \
             .validar_tipo('salario', int) \
             .validar_no_nulo('nombre') \
             .validar_tipo('nombre', str) \
             .validar_valores_permitidos('nombre', ['Ana', 'Juan', 'Pedro', 'Luis', 'María']) \
             .validar_formato_fecha('fecha_ingreso', '%d/%m/%Y') \
             .validar_rango_fecha('fecha_ingreso', '%d/%m/%Y', '01/01/2020', '31/12/2023') \
             .validar_regex('email', r'^\S+@\S+\.\S+$')

    resultados = validador.obtener_resultados()

    # Detener el temporizador
    end_time = time.time()
    elapsed_time = end_time - start_time

    # Mostrar los resultados de las validaciones
    print(resultados)


    print(f"Tiempo de ejecución para validar {num_registros} registros: {elapsed_time:.2f} segundos")

# Ejecutar el test
test_validador_dataframe()
