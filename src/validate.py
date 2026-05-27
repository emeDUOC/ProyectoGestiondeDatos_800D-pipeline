import os
import logging
import pandas as pd

log = logging.getLogger(__name__)

def validate() -> None:
    processed_path = "data/processed/chicago_taxi_clean.csv"
    validated_path = "data/validated/taxi_validated.csv"
    rejected_path = "data/validated/taxi_rejected.csv"
    report_path = "data/reports/validation_report.txt"
    
    if not os.path.exists(processed_path):
        raise FileNotFoundError("No existen datos limpios procesados para validar.")
        
    df = pd.read_csv(processed_path)
    registros_validos = []
    registros_rechazados = []
    
    log.info(f"Iniciando validación semántica de {len(df)} registros...")
    
    for idx, row in df.iterrows():
        reglas_fallidas = []
        
        # Validaciones de Integridad y Reglas de Negocio
        if pd.isna(row['id_taxi']) or row['id_taxi'] == "NAN":
            reglas_fallidas.append("not_null:id_taxi")
        if row['duracion_segundos'] < 0:
            reglas_fallidas.append("range:duracion_negativa")
        if row['distancia_millas'] < 0:
            reglas_fallidas.append("range:distancia_negativa")
        if row['total_pago'] < 0 or row['total_pago'] > 1000:
            reglas_fallidas.append("range:pago_invalido_o_extremo")

        row_dict = row.to_dict()
        if len(reglas_fallidas) == 0:
            registros_validos.append(row_dict)
        else:
            row_dict['failed_rules'] = "|".join(reglas_fallidas)
            registros_rechazados.append(row_dict)
            
    df_val = pd.DataFrame(registros_validos)
    df_rej = pd.DataFrame(registros_rechazados)
    
    os.makedirs(os.path.dirname(validated_path), exist_ok=True)
    df_val.to_csv(validated_path, index=False)
    df_rej.to_csv(rejected_path, index=False)
    
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        f.write(f"Registros analizados: {df.shape[0]}\nRegistros aprobados: {df_val.shape[0]}\nRegistros rechazados: {df_rej.shape[0]}\n")
            
    log.info(f"Validación finalizada. Aprobados: {len(df_val)} | Rechazados: {len(df_rej)}")