##
## @file __init__.py
##
## Contiene constantes y funciones principales del paquete ts_cnn.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

    
from ..ts_csv.pipelineCSV import capturar_datos_csv, crear_tablas_estructura

__all__ = [
    "crear_tablas_estructura",
    "capturar_datos_csv",
    "VENTANA_CNN",
    "MAX_HORIZONTE",
    "EPOCHS",
    "BATCH_SIZE",
    "PATIENCE",
]

VENTANA_CNN = 6
MAX_HORIZONTE = 18
EPOCHS = 100
BATCH_SIZE = 32
PATIENCE = 10