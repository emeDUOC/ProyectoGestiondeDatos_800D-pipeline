CREATE TABLE IF NOT EXISTS viajes_taxis (
    id_registro      SERIAL PRIMARY KEY,
    taxi_id          VARCHAR(150)  NOT NULL,
    trip_start_timestamp TIMESTAMP NOT NULL,
    trip_seconds     NUMERIC(10,2) NOT NULL,
    trip_miles       NUMERIC(10,4) NOT NULL,
    trip_total       NUMERIC(10,2) NOT NULL,
    categoria_viaje  VARCHAR(20)   NOT NULL,
    loaded_at        TIMESTAMP     NOT NULL DEFAULT NOW(),

    -- Restricciones de Calidad de Datos adaptadas a la realidad del CSV
    CONSTRAINT chk_trip_seconds   CHECK (trip_seconds >= 0),
    CONSTRAINT chk_trip_miles     CHECK (trip_miles >= 0),
    CONSTRAINT chk_trip_total     CHECK (trip_total >= 0),
    CONSTRAINT chk_categoria_viaje CHECK (categoria_viaje IN ('CORTO', 'ESTÁNDAR', 'LARGO', 'VIAJE_EXTREMO')),
    CONSTRAINT uq_taxi_timestamp   UNIQUE (taxi_id, trip_start_timestamp)
);