import pandas as pd
import pyarrow as pa

def format_bytes(size):
    # Formatear tamaño en bytes con separador de miles europeo
    return f"{size:,}".replace(",", ".").replace(".", " ", 1).replace(" ", ".")

def format_mb(size):
    # Convertir bytes a MB y formatear con 2 decimales
    size_mb = size / (1024 ** 2)
    return f"{size_mb:,.2f} MB".replace(",", " ")

def importar_csv_optimo(ruta_csv, separador=',', columnas_datetime=None, formato_fecha=None, columnas_booleanas=None):
    # Leer el archivo CSV en un DataFrame de pandas
    df = pd.read_csv(ruta_csv, sep=separador)
    
    # Convertir las columnas especificadas a datetime
    if columnas_datetime is not None:
        for columna in columnas_datetime:
            df[columna] = pd.to_datetime(df[columna], format=formato_fecha, errors='coerce')
    
    # Convertir las columnas especificadas a booleanas
    if columnas_booleanas is not None:
        for columna in columnas_booleanas:
            df[columna] = df[columna].astype('bool')
    
    # Calcular el uso de memoria antes de la optimización
    memoria_inicial = df.memory_usage(deep=True).sum()
    
    # Definir los tipos de datos de referencia
    string_pa = pd.ArrowDtype(pa.string())
    cat = pd.CategoricalDtype()
    u8 = pd.UInt8Dtype()
    u16 = pd.UInt16Dtype()
    u32 = pd.UInt32Dtype()
    u64 = pd.UInt64Dtype()
    i8 = pd.Int8Dtype()
    i16 = pd.Int16Dtype()
    i32 = pd.Int32Dtype()
    i64 = pd.Int64Dtype()
    f32 = pd.Float32Dtype()
    f64 = pd.Float64Dtype()
    bl = pd.BooleanDtype()
    
    # Diccionario para almacenar los tipos de datos óptimos
    tipo_optimo = {}

    # Evaluar cada columna del DataFrame
    for columna in df.columns:

        # Verificar si la columna es de tipo cadena
        if df[columna].dtype == 'object':
            valores_unicos = df[columna].nunique()
            if valores_unicos <= 1000:
                tipo_optimo[columna] = cat
            else:
                tipo_optimo[columna] = string_pa

        # Verificar si la columna es numérica
        elif pd.api.types.is_numeric_dtype(df[columna]):
            min_val = df[columna].min()
            max_val = df[columna].max()
            if pd.api.types.is_integer_dtype(df[columna]):

                # Asignar el tipo de entero adecuado
                if min_val >= 0:
                    if max_val <= 255:
                        tipo_optimo[columna] = u8
                    elif max_val <= 65535:
                        tipo_optimo[columna] = u16
                    elif max_val <= 4294967295:
                        tipo_optimo[columna] = u32
                    else:
                        tipo_optimo[columna] = u64
                else:
                    if min_val >= -128 and max_val <= 127:
                        tipo_optimo[columna] = i8
                    elif min_val >= -32768 and max_val <= 32767:
                        tipo_optimo[columna] = i16
                    elif min_val >= -2147483648 and max_val <= 2147483647:
                        tipo_optimo[columna] = i32
                    else:
                        tipo_optimo[columna] = i64
            else:
                # Asignar el tipo de flotante adecuado
                if df[columna].dtype == 'float32':
                    tipo_optimo[columna] = f32
                else:
                    tipo_optimo[columna] = f64

        # Verificar si la columna es booleana
        elif pd.api.types.is_bool_dtype(df[columna]):
            tipo_optimo[columna] = bl
            
        # Verificar si la columna es de tipo datetime
        elif pd.api.types.is_datetime64_any_dtype(df[columna]):
            tipo_optimo[columna] = 'datetime64[ns]'
    
    # Convertir las columnas del DataFrame al tipo de dato óptimo
    for columna, tipo in tipo_optimo.items():
        df[columna] = df[columna].astype(tipo)
    
    # Calcular el uso de memoria después de la optimización
    memoria_final = df.memory_usage(deep=True).sum()
    
    # Calcular el ahorro de memoria en bytes y MB
    ahorro_memoria = memoria_inicial - memoria_final
    ahorro_memoria_mb = ahorro_memoria / (1024 ** 2)
    
    # Calcular el porcentaje de mejora
    mejora_porcentaje = (ahorro_memoria / memoria_inicial) * 100
    
    return df, memoria_inicial, memoria_final, ahorro_memoria, ahorro_memoria_mb, mejora_porcentaje

# Ejemplo de uso
ruta_csv = r'C:\Users\Juan\Desktop\Next State\Python\81_Python_Pablo\pandas_exercises\format_clean_dataframe\test\data_sales_records.csv'
columnas_datetime = ['Order Date', 'Ship Date']  # Reemplazar con nombres de columnas reales
formato_fecha = '%m/%d/%Y'  # Formato de fecha, ajustar según sea necesario
columnas_booleanas = []  # Reemplazar con nombres de columnas reales

df_optimo, memoria_inicial, memoria_final, ahorro_memoria, ahorro_memoria_mb, mejora_porcentaje = importar_csv_optimo(
    ruta_csv, separador=',', columnas_datetime=columnas_datetime, formato_fecha=formato_fecha, columnas_booleanas=columnas_booleanas
)

print(f"Memoria usada antes de optimizar: {format_bytes(memoria_inicial)} bytes ({format_mb(memoria_inicial)})")
print(f"Memoria usada después de optimizar: {format_bytes(memoria_final)} bytes ({format_mb(memoria_final)})")
print(f"Ahorro de memoria: {format_bytes(ahorro_memoria)} bytes ({ahorro_memoria_mb:.2f} MB)")
print(f"Mejora en el uso de memoria: {mejora_porcentaje:.2f}%")


print(df_optimo.info(verbose=True, memory_usage='deep'))
print(df_optimo.head())
