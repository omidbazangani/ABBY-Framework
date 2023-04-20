# Copyright (C) 2020-2021 
# SPDX-License-Identifier: Apache-2.0

"""
Boosted tree model using CatBoost.

TODO: expand uint32 from dataset to 32 boolean features
"""

import logging
import os

import numpy as np
import pandas as pd

from abby.model.base import Model

# Local logger
log = logging.getLogger(__name__)


class CatBoostModel(Model):
    """Boosted tree model using CatBoost

    By default learning and prediction is done using GPU.
    To use CPU you can add ``task_type="CPU"`` when instancing this class.

    The default hyperparameters were optimized with a grid search on the power
    consumption of an ST STM32F0308 Discovery board.
    """

    def __init__(self, path, create=False, **kwargs):
        """Initialize boosted tree model

        CatBoost learning configuration is accessible at ``params`` method.

        :param path: path to load or save model
        :type path: str
        :param create: create new model without loading, defaults to False
        :type create: bool, optional
        """

        self.model = None
        self.path = path

        # See https://catboost.ai/docs/concepts/
        self.params = {
            # These hyperparameters were optimized with a grid search on
            # ST STM32F0308 Discovery
            "learning_rate": 0.5,
            "depth": 11,
            "l2_leaf_reg": 7,
            "iterations": 8192,
            # Instruction in all the pipeline stage are categorical features
            "cat_features": ["instr_stage1", "instr_stage2", "instr_stage3"],
            "task_type": "GPU",
            "verbose": 10,
            "train_dir": "/tmp/catboost_info",
            "bootstrap_type": "No",  # disable Bayesian bootstrap
            "early_stopping_rounds": 256,
        }
        self.params.update(kwargs)

        # Load existing model
        if not create:
            if not os.path.exists(path):
                raise FileNotFoundError(f"{path} does not exist.")

            from catboost import CatBoostRegressor

            self.model = CatBoostRegressor()
            self.model.load_model(path, format="json")

    def predict(self, features) -> np.ndarray:
        """Predict target using features

        If features contains "power" and "nb_cycles" it will be dropped before
        predicting.

        :param features: features to input to the model
        :type features: [[int]] or pandas.DataFrame
        :return: model prediction
        :rtype: numpy.ndarray
        """
        if self.model is None:
            log.error("Cannot predict empty model.")
            exit(1)

        # Make sure power and nb_cycles are not in features
        features = features.drop(
            ["power", "nb_cycles"],
            axis=1,
            errors="ignore",
        )

        prediction = self.model.predict(features)
        return prediction

    def fit(self, data_files, test_size=0.2):
        """Train model on target using features

        :param data_files: dataset files
        :type data_files: [str]
        :param test_size: portion of the dataset using for evaluation, default
            to 0.2
        :type test_size: float, optional
        """
        from catboost import CatBoostRegressor

        # Load all training set in memory
        dfs = []
        for path in data_files:
            dfs.append(pd.read_csv(path))
        all_features = pd.concat(dfs)
        all_features = all_features.drop("nb_cycles", axis=1, errors="ignore")

        # Shuffle and split into training and test sets
        train_features, test_features = train_test_split(all_features, test_size)

        # Split target
        train_target = train_features.pop("power")
        test_target = test_features.pop("power")

        self.model = CatBoostRegressor(**self.params)
        self.model = self.model.fit(
            train_features, train_target, eval_set=(test_features, test_target)
        )

    def save(self):
        """Save model to path provided

        You should provide a path ending with ``.json``.
        """
        if self.model is None:
            log.error("Cannot save empty model.")
            exit(1)

        log.debug(f"Saving power model at {self.path}")
        self._create_parent_folder(self.path)
        self.model.save_model(self.path, format="json")
