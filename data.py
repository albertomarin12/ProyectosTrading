import pandas as pd

def load_data():
    # sep=None con engine='python' detecta automáticamente si es , o ;
    # encoding='latin-1' maneja caracteres especiales de Excel en español
    # on_bad_lines='warn' evita que el programa truene si hay filas con errores
    try:
        data_train = pd.read_csv("C:\\Users\\Alberto\\OneDrive - ITESO\\9no Semestre\\Microestructuras de Trading\\Proyecto_1\\data\\btc_project_train.csv", sep=None, engine='python', encoding='latin-1', on_bad_lines='warn').dropna()
        data_test = pd.read_csv("C:\\Users\\Alberto\\OneDrive - ITESO\\9no Semestre\\Microestructuras de Trading\\Proyecto_1\\data\\btc_project_test.csv", sep=None, engine='python', encoding='latin-1', on_bad_lines='warn').dropna()
    except Exception as e:
        print(f"Error al cargar archivos: {e}")
        raise e
        
    return data_train, data_test

def preprocess_data(raw_data: pd.DataFrame) -> pd.DataFrame: 
    data = pd.DataFrame()
    
    # Buscamos explícitamente la columna llamada "Datetime" (ignoramos "Timestamp")
    time_col = next((c for c in raw_data.columns if c.lower() == "datetime"), None)
    
    if time_col:
        # El archivo train tiene "2022-06-01", el test tiene "02/05/2024"
        # format='mixed' le dice a pandas que averigüe el formato línea por línea
        data["Datetime"] = pd.to_datetime(raw_data[time_col], dayfirst=True, format='mixed', errors='coerce')
    else:
        raise KeyError(f"No se encontró la columna 'Datetime'. Columnas disponibles: {list(raw_data.columns)}")

    data["Open"] = pd.to_numeric(raw_data.Open, errors='coerce')
    data["High"] = pd.to_numeric(raw_data.High, errors='coerce')
    data["Low"] = pd.to_numeric(raw_data.Low, errors='coerce')
    data["Close"] = pd.to_numeric(raw_data.Close, errors='coerce')
    
    data = data.dropna().set_index("Datetime").sort_index()
    return data