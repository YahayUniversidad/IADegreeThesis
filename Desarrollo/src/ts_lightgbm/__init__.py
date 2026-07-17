##
## @file __init__.py
##
## Constantes y funciones principales del paquete ts_lightgbm.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

__all__ = [
    "VENTANA_LGBM",
    "MAX_HORIZONTE",
    "TEST_SIZE",
    "VAL_SIZE",
    "NUM_BOOST_ROUND",
    "EARLY_STOPPING_ROUNDS",
    "LGBM_PARAMS",
]

VENTANA_LGBM = 6
MAX_HORIZONTE = 18
TEST_SIZE = 0.3
VAL_SIZE = 0.2
NUM_BOOST_ROUND = 1000
EARLY_STOPPING_ROUNDS = 50

LGBM_PARAMS = {
    "objective": "binary",
    "metric": "binary_logloss",
    "boosting_type": "gbdt",
    "num_leaves": 31,
    "learning_rate": 0.05,
    "feature_fraction": 0.8,
    "bagging_fraction": 0.8,
    "bagging_freq": 5,
    "verbose": -1,
    "n_jobs": -1,
    "seed": 42,
}
