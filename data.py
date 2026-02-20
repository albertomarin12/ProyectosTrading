import pandas as pd

def load_data():
    # sep=None con engine='python' detecta automáticamente si es , o ;
    # encoding='latin-1' maneja caracteres especiales de Excel en español
    # on_bad_lines='warn' evita que el programa truene si hay filas con errores
    try:
        data_train = pd.read_csv("data/btc_project_train.csv", sep=None, engine='python', encoding='latin-1', on_bad_lines='warn').dropna()
        data_test = pd.read_csv("data/btc_project_test.csv", sep=None, engine='python', encoding='latin-1', on_bad_lines='warn').dropna()
    except Exception as e:
        print(f"Error al cargar archivos: {e}")
        raise e
        
    return data_train, data_test

def preprocess_data(raw_data: pd.DataFrame) -> pd.DataFrame: 
    data = pd.DataFrame()
    
    # Buscamos la columna de tiempo sin importar si es 'timestamp' o 'Datetime'
    time_col = next((c for c in raw_data.columns if c.lower() in ["timestamp", "datetime"]), None)
    
    if time_col:
        data["Datetime"] = pd.to_datetime(raw_data[time_col])
    else:
        raise KeyError(f"No se encontró columna de tiempo. Columnas disponibles: {list(raw_data.columns)}")

    # Aseguramos que los precios sean flotantes
    data["Open"] = raw_data.Open.astype(float)
    data["High"] = raw_data.High.astype(float)
    data["Low"] = raw_data.Low.astype(float)
    data["Close"] = raw_data.Close.astype(float)
    
    # Establecer el índice para series de tiempo
    data = data.set_index("Datetime")
    return data