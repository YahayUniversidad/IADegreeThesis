##
## @file __init__.py
##
## Contiene las funciones y clases principales del paquete eva.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

from .analisis_riguroso import AnalisisRiguroso
from .pipelineEVA import PipelineEVA, analizar_eda_eva
from .utilidades import espacio_tiempo

__all__ = [
    "AnalisisRiguroso",
    "PipelineEVA",
    "espacio_tiempo",
    "analizar_eda_eva"
]
