# Copyright (C) 2020-2021 
# SPDX-License-Identifier: Apache-2.0

"""
Base model
"""

import logging
import os
import pathlib

import numpy as np
import pandas as pd

# Local logger
log = logging.getLogger(__name__)


class Model:
    """Common interface for models

    All models should inherit this base class.
    """

    def __init__(self, path: str, create=False):
        """Initialize a model

        :param path: path to load or save model
        :type path: str
        :param create: create new model without loading, defaults to False
        :type create: bool, optional
        """
        super().__init__()

    @staticmethod
    def _create_parent_folder(path):
        """Create destination folder if missing"""
        dest = pathlib.Path(path).parent.absolute()
        os.makedirs(dest, exist_ok=True)

    def predict(self, features) -> np.ndarray:
        """Predict target using features

        :param features: features to input to the model
        :type features: [[int]] or pandas.DataFrame
        :return: model prediction
        :rtype: numpy.ndarray
        """
        raise NotImplementedError()

    def fit(self, data_files, test_size=0.2):
        """Fit model on target using provided data

        :param data_files: dataset files
        :type data_files: [str]
        :param test_size: portion of the dataset using for evaluation, default
            to 0.2
        :type test_size: float, optional
        """
        raise NotImplementedError()

    def save(self):
        """Save model to path provided"""
        raise NotImplementedError()

    def rsquare(self, features, target) -> float:
        """Compute r2 between prediction from features and target

        :param features: features to input to the model, should be different
            from training phase
        :type features: [[int]] or pandas.DataFrame
        :param target: real target to compare with
        :type target: [float] or numpy.ndarray
        :return: r2 score
        :rtype: float
        """
        ypred = self.predict(features)
        sse = sum((ypred - target) ** 2)
        mean_target = sum(target) / len(target)
        sst = sum((target - mean_target) ** 2)
        return 1 - sse / sst

    @staticmethod
    def _encode_categorical_features(features, name, possible_values):
        """Encode categorical features to numerical features.

        This method is useful when using a model that does not support
        categorical features.

        Example::
            >>> model._encode_categorical_features(features, "instr_stage1",
            ...                                    INSTRUCTIONS)

        :param features: all features
        :type features: pandas.DataFrame
        :param name: feature to encode
        :type name: str
        :param possible_values: set of possible values taken by the features
        :type possible_values: list
        :return: all features with encoded features
        :rtype: pandas.DataFrame
        """
        # Create new columns to keep order and make sure all values are
        # represented
        log.debug(f"Converting categorical {name} to numerical features")
        for i in possible_values:
            features[f"{name}_{i}"] = 0

        # Categorical features to numerical
        d = pd.get_dummies(features[name], prefix=name)
        features.update(d)
        features = features.drop(name, axis=1)

        return features
