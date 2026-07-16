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
 ]