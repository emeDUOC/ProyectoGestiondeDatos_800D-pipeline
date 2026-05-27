"""
Orquestador del Pipeline de Operaciones de Taxis.

Ejecuta las tres etapas en orden secuencial:
  1. clean    — CSV original → data/processed/
  2. validate — CSV procesado → data/validated/ + data/reports/
  3. load     — CSV validado → PostgreSQL

Uso:
  uv run python main.py               # Ejecuta todas las etapas consecutivas
  uv run python main.py --stage clean
  uv run python main.py --stage validate
  uv run python main.py --stage load
"""

import argparse
import logging
import sys
import time

# Configuración del sistema de logging profesional (idéntico al del profesor)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


# Importaciones dinámicas (Lazy Imports) adaptadas a los nuevos módulos
def run_clean() -> None:
    from src.clean import clean
    clean()


def run_validate() -> None:
    from src.validate import validate
    validate()


def run_load() -> None:
    from src.load import load
    load()


# Despachador de etapas por diccionario (Patrón Command)
STAGES = {
    "clean": run_clean,
    "validate": run_validate,
    "load": run_load,
}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Pipeline DataOps de Control de Taxis")
    parser.add_argument(
        "--stage",
        choices=list(STAGES),
        default=None,
        help="Ejecuta una sola etapa aislada en vez del pipeline completo",
    )
    args = parser.parse_args(argv)

    # Determinar si corre todo el flujo o una sola sección modular
    stages = [args.stage] if args.stage else list(STAGES)

    t0 = time.perf_counter()
    for stage in stages:
        log.info(f"--- Iniciando etapa: {stage} ---")
        t1 = time.perf_counter()
        try:
            STAGES[stage]()
        except Exception:
            log.exception(f"La etapa '{stage}' falló de manera crítica")
            sys.exit(1)
        log.info(f"--- Etapa '{stage}' completada en {time.perf_counter() - t1:.2f}s ---")

    log.info(f"🎉 Pipeline finalizado con éxito total en {time.perf_counter() - t0:.2f}s")


if __name__ == "__main__":
    main()