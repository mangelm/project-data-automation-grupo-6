import os
import pandas as pd
from sqlalchemy import create_engine, text
from src.config import *

def get_engine():
    # Construye la URL de conexión y devuelve un engine de SQLAlchemy
    url_db = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    return create_engine(url_db)

def generar_reporte_csv(query_sql, nombre_archivo):
    """
    Ejecuta una query y genera UN archivo CSV específico.
    """
    engine = get_engine()
    try:
        # Ejecuta la consulta y obtiene un DataFrame
        with engine.begin() as connection:
            df = pd.read_sql(text(query_sql), connection)
        # Asegura que el directorio de salida exista
        if not os.path.exists('outputs'):
            os.makedirs('output')

        ruta = f"outputs/{nombre_archivo}.csv"
        df.to_csv(ruta, index=False, encoding='utf-8')
        print(f"✅ Generado: {ruta}")
        return True
    except Exception as e:
        print(f"❌ Error en {nombre_archivo}: {e}")
        return False

    