# Copyright (C) 2020-2021 
# SPDX-License-Identifier: Apache-2.0

"""
Hamming weight model
"""

import numpy as np

from abby.model.base import Model


class HammingWeightModel(Model):
    """Hamming weight model

    Model the power comsuption as the hamming weight of operand 2.
    If you compile ELMO with ``POWERMODEL_HW`` you will get the same estimation.
    """

    def __init__(self, create=False):
        """Initialize Hamming weight model

        Nothing requires initialization, but we still check that create is not
        true.

        :param create: create new model without loading, defaults to False
        :type create: bool, optional
        """
        # Training not supported
        if create:
            raise NotImplementedError()

    def predict(self, features) -> np.ndarray:
        """Predict target using features

        Apply the Hamming weight model.

        :param features: features to input to the model
        :type features: [[int]] or pandas.DataFrame
        :return: model prediction
        :rtype: numpy.ndarray
        """
        hw = np.sum([features[f"op2_value_current_{i}"] for i in range(32)], axis=1)
        return hw
