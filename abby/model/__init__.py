# Copyright (C) 2020-2021 
# SPDX-License-Identifier: Apache-2.0

"""
Models fitting and prediction code.

Abby provides abstraction over common model types to help training them.
"""

from abby.model.base import Model
from abby.model.catboost import CatBoostModel
from abby.model.elmo import ELMOModel
from abby.model.hamming_weight import HammingWeightModel
from abby.model.mlp import MlpModel
from abby.model.xgboost import XgbModel

__all__ = [
    "CatBoostModel",
    "ELMOModel",
    "get_model",
    "HammingWeightModel",
    "MlpModel",
    "Model",
    "XgbModel",
]


def get_model(model_cfg: str, create=False) -> Model:
    """Get corresponding model (elmo, xgb or mlp).

    :param model_cfg: type and path of the model, must be formatted as ``elmo``
        for ELMO, ``hd`` for Hamming distance, ``xgb,path`` for boosted tree
        using XGBoost or ``mlp,path`` for MLP.
    :type model_cfg: str
    :param create: create a new model, defaults to False
    :type create: bool, optional
    :return: model
    :rtype: Model
    """
    # Load corresponding model
    if model_cfg == "elmo":
        return ELMOModel(create)
    elif model_cfg == "hw":
        return HammingWeightModel(create)
    elif model_cfg.startswith("xgb,"):
        return XgbModel(model_cfg[4:], create)
    elif model_cfg.startswith("catboost,"):
        return CatBoostModel(model_cfg[9:], create)
    elif model_cfg.startswith("mlp,"):
        return MlpModel(model_cfg[4:], create)

    raise ValueError(
        f"Failed to recognize {model_cfg}, "
        "it should be `elmo`, `xgb,path` or `mlp,path`."
    )
