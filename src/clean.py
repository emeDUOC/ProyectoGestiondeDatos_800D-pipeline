import os
import logging
import pandas as pd

log = logging.getLogger(__name__)

def clean() -> None:
    raw_path = "data/raw/chicago_taxi_raw.csv"
    processed_path = "data/processed/chicago_taxi_clean.csv"
    
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"No se encontró el archivo inicial en {raw_path}")
        
    log.info("Leyendo el dataset crudo de taxis...")
    df = pd.read_csv(raw_path)
    
    # Eliminar columnas basura (como las que contienen 'zero')
    columnas_basura = [col for col in df.columns if 'zero' in col.lower()]
    if columnas_basura:
        log.info(f"Eliminando columnas irrelevantes: {columnas_basura}")
        df = df.drop(columns=columnas_basura)

    # Homologar nombres de columnas al esquema operativo en español
    log.info("Homologando nombres de columnas para la base de datos...")
    df = df.rename(columns={
        'taxi_id': 'id_taxi',
        'trip_start_timestamp': 'fecha_viaje',
        'trip_seconds': 'duracion_segundos',
        'trip_miles': 'distancia_millas',
        'trip_total': 'total_pago'
    })
    
    # Quitar duplicados operativos primarios
    df = df.drop_duplicates(subset=['id_taxi', 'fecha_viaje'])
    
    # Imputación inteligente por la mediana ante nulos en indicadores clave
    for col in ['duracion_segundos', 'distancia_millas', 'total_pago']:
        if col in df.columns and df[col].isnull().sum() > 0:
            mediana = df[col].median()
            log.warning(f"Campos nulos detectados en '{col}'. Imputando con la mediana: {mediana}")
            df[col] = df[col].fillna(mediana)

    df['id_taxi'] = df['id_taxi'].astype(str).str.upper()
    df['fecha_viaje'] = pd.to_datetime(df['fecha_viaje']).dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Feature Engineering: Clasificación de viajes por distancia
    def clasificar_viaje(row):
        dist = row['distancia_millas']
        if dist < 2: return 'CORTO'
        elif dist < 10: return 'ESTÁNDAR'
        elif dist < 30: return 'LARGO'
        else: return 'VIAJE_EXTREMO'
        
    df['categoria_viaje'] = df.apply(clasificar_viaje, axis=1)
    
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    df.to_csv(processed_path, index=False)
    log.info(f"Datos limpios guardados exitosamente en: {processed_path}")