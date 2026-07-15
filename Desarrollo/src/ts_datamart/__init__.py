##
## @file __init__.py
##
## Paquete datamart: pipeline para construir y refrescar el datamart analitico.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

from .pipeline import (
    ejecutar_datamart,
)

__all__ = [
    "ejecutar_datamart",
]