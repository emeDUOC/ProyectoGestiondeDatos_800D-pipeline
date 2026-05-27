import os
import logging
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger(__name__)

def load() -> None:
    validated_path = "data/validated/taxi_validated.csv"
    inserted_path = "data/validated/taxi_inserted.csv"
    db_rejected_path = "data/validated/taxi_db_rejected.csv"
    sql_script_path = "sql/create_table.sql"
    
    if not os.path.exists(validated_path):
        raise FileNotFoundError("No existen datos validados preparados para la carga.")
        
    df = pd.read_csv(validated_path)
    
    try:
        db_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST', '127.0.0.1')}:{os.getenv('POSTGRES_PORT', 5432)}/{os.getenv('POSTGRES_DB')}"
        engine = create_engine(db_url)
        
        # Ejecutar plano DDL inicial si existe
        if os.path.exists(sql_script_path):
            log.info("Verificando existencia de la estructura de tablas SQL...")
            with open(sql_script_path, "r", encoding="utf-8") as f:
                with engine.connect() as connection:
                    connection.execute(text(f.read()))
                    connection.commit()
    except Exception as e:
        log.error(f"Error crítico en la conexión a la base de datos: {e}")
        raise e

    list_inserted = []
    list_rejected = []
    
    log.info("Iniciando inserción controlada de registros en PostgreSQL...")
    with engine.connect() as connection:
        for _, row in df.iterrows():
            try:
                query = text("""
                    INSERT INTO viajes_taxis (id_taxi, fecha_viaje, duracion_segundos, distancia_millas, total_pago, categoria_viaje)
                    VALUES (:id_taxi, :fecha_viaje, :duracion_segundos, :distancia_millas, :total_pago, :categoria_viaje);
                """)
                connection.execute(query, {
                    'id_taxi': row['id_taxi'],
                    'fecha_viaje': row['fecha_viaje'],
                    'duracion_segundos': row['duracion_segundos'],
                    'distancia_millas': row['distancia_millas'],
                    'total_pago': row['total_pago'],
                    'categoria_viaje': row['categoria_viaje']
                })
                connection.commit()
                list_inserted.append(row.to_dict())
            except Exception:
                connection.rollback()
                row_dict = row.to_dict()
                row_dict['rejection_reason'] = "Duplicado_Detectado"
                list_rejected.append(row_dict)

    if list_inserted:
        pd.DataFrame(list_inserted).to_csv(inserted_path, index=False)
    if list_rejected:
        pd.DataFrame(list_rejected).to_csv(db_rejected_path, index=False)
        log.warning(f"Se omitieron {len(list_rejected)} viajes por estar duplicados en la base de datos.")
        
    log.info(f"Carga finalizada con éxito. {len(list_inserted)} filas impactadas en Postgres.")