# Copyright (C) 2020-2021 
# SPDX-License-Identifier: Apache-2.0

"""
Boosted tree model using XGBoost.

TODO: expand uint32 from dataset to 32 boolean features
"""

import logging
import os

import numpy as np
import pandas as pd

from abby.model.base import Model

# Local logger
log = logging.getLogger(__name__)


class XgbModel(Model):
    """Boosted tree model using XGBoost

    By default it will try to use GPU for learning and prediction.

    XGBoost is currently working on adding categorical feature support but it is
    still experimental: <https://github.com/dmlc/xgboost/pull/5949>.
    For now we recommend using CatBoost.
    """

    def __init__(self, path, create=False):
        """Initialize boosted tree model

        XGBoost learning configuration is accessible at ``params`` method.

        :param path: path to load or save model
        :type path: str
        :param create: create new model without loading, defaults to False
        :type create: bool, optional
        """

        self.bst = None
        self.path = path

        # See https://xgboost.readthedocs.io/en/latest/parameter.html
        self.params = {
            "max_depth": 12,  # maximum depth of a tree
            "eta": 0.1,  # learning rate (eta).
            "subsample": 0.9,  # sample training data to prevent overfitting
            "seed": 0,  # for random number generator
            "nthread": 8,  # CPU threads
            "tree_method": "gpu_hist",  # GPU acceleration
            "predictor": "gpu_predictor",
        }

        # The number of trees (or rounds) in XGBoost
        self.n_trees = 256

        # Load existing model
        if not create:
            if not os.path.exists(path):
                raise FileNotFoundError(f"{path} does not exist.")

            import xgboost as xgb

            self.bst = xgb.Booster()
            self.bst.load_model(path)
            self.bst.set_param(self.params)

    def predict(self, features) -> np.ndarray:
        """Predict target using features

        If features contains "power" and "nb_cycles" it will be dropped before
        calling XGBoost.

        :param features: features to input to the model
        :type features: pandas.DataFrame
        :return: model prediction
        :rtype: numpy.ndarray
        """
        if self.bst is None:
            log.error("Cannot predict empty model.")
            exit(1)

        # Make sure power and nb_cycles are not in features
        features = features.drop(
            ["power", "nb_cycles"],
            axis=1,
            errors="ignore",
        )
        # FIXME: do not import xgb here
        import xgboost as xgb

        features = xgb.DMatrix(features)

        prediction = self.bst.predict(features)
        return np.array(prediction)

    def fit(self, data_files, test_size=0.2):
        """Train model on target using features

        :param data_files: dataset files
        :type data_files: [str]
        :param test_size: portion of the dataset using for evaluation, default
            to 0.2
        :type test_size: float, optional
        """
        import xgboost as xgb

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

        # FIXME: get INSTRUCTIONS from Cortex-M0 set
        INSTRUCTIONS = []

        # Encode categorical features
        train_features = self._encode_categorical_features(
            train_features, "instr_stage1", INSTRUCTIONS
        )
        train_features = self._encode_categorical_features(
            train_features, "instr_stage2", INSTRUCTIONS
        )
        train_features = self._encode_categorical_features(
            train_features, "instr_stage3", INSTRUCTIONS
        )

        # FIXME: use test dataset
        dtrain = xgb.DMatrix(train_features, label=train_target)
        self.bst = xgb.train(
            params=self.params,
            dtrain=dtrain,
            num_boost_round=self.n_trees,
            evals=[(dtrain, "train")],
            verbose_eval=64,
            xgb_model=self.bst,
        )

        # Statistics
        r2 = self.rsquare(test_features, test_target)
        print(f"r² for power model: {r2}")

    def save(self):
        """Save model to path provided

        For XGBoost it is recommended to use a JSON file. You should provide
        a path ending with ``.json``.
        """
        if self.bst is None:
            log.error("Cannot save empty model.")
            exit(1)

        log.debug(f"Saving power model at {self.path}")
        self._create_parent_folder(self.path)
        self.bst.save_model(self.path)
