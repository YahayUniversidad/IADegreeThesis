##
## @file __init__.py
##
## Contiene constantes y funciones principales del paquete sql.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

from .csv import capturar_datos_csv, crear_tablas_estructura
from .queries import (
    SCRIPT_CREATE_TABLE_TEMPORAL_CSV,
    SQL_CREA_DIM_RIESGO,
    SQL_CREA_DIM_SECTOR,
    SQL_CREA_DIM_SUCURSAL,
    SQL_CREA_DIM_TIEMPO,
    SQL_CREA_FACT_CREDITOS,
    SQL_CREA_FACT_PREDICCIONES,
    SQL_CREATE_IDX_MV,
    SQL_INSERT_PREDICCIONES,
    SQL_REFRESH_DIM_RIESGO,
    SQL_REFRESH_DIM_SECTOR,
    SQL_REFRESH_DIM_SUCURSAL,
    SQL_REFRESH_DIM_TIEMPO,
    SQL_CREATE_MV,
    SQL_CREATE_TABLE_AMORTIZACION,
    SQL_CREATE_TABLE_CREDITOS,
    SQL_CREATE_TABLE_JUICIOS,
    SQL_DROP_MV,
    SQL_INSERT_DIM_RIESGO,
    SQL_INSERT_DIM_SECTOR,
    SQL_INSERT_DIM_SUCURSAL,
    SQL_INSERT_DIM_TIEMPO,
    SQL_UPSERT_FACT_CREDITOS,
)
from .utilidades import ejeucta_script_generico

__all__ = [
    "ejeucta_script_generico",
    "crear_tablas_estructura",
    "capturar_datos_csv",
    "SQL_CREATE_TABLE_CREDITOS",
    "SQL_CREATE_TABLE_AMORTIZACION",
    "SQL_CREATE_TABLE_JUICIOS",
    "SQL_CREA_FACT_CREDITOS",
    "SQL_CREA_DIM_TIEMPO",
    "SQL_CREA_DIM_RIESGO",
    "SQL_CREA_DIM_SECTOR",
    "SQL_CREA_DIM_SUCURSAL",
    "SQL_DROP_MV",
    "SQL_CREATE_MV",
    "SQL_CREATE_IDX_MV",
    "SQL_INSERT_DIM_TIEMPO",
    "SQL_INSERT_DIM_RIESGO",
    "SQL_INSERT_DIM_SECTOR",
    "SQL_INSERT_DIM_SUCURSAL",
    "SQL_UPSERT_FACT_CREDITOS",
    "SCRIPT_CREATE_TABLE_TEMPORAL_CSV",
]