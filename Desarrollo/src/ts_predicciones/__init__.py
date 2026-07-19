##
## @file __init__.py
##
## Paquete de predicciones multi-modelo.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

from .pipeline import (
    ejecutar_predicciones,
)

VENTANA = 6
MAX_HORIZONTE = 18

__all__ = [
    "VENTANA",
    "MAX_HORIZONTE",
    "ejecutar_predicciones",
]
