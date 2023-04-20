# Copyright (C) 2020-2021 
# SPDX-License-Identifier: Apache-2.0

"""
Models fitting and prediction code.
"""

import logging
import os
import pathlib

import numpy as np

from abby.model.base import Model

# Local logger
log = logging.getLogger(__name__)


class ELMOModel(Model):
    """Use ELMO model to predict power.

    ELMO is a leakage simulator designed for ARM Cortex-M0.
    See <https://eprint.iacr.org/2016/517/20160529:210156>.
    """

    def __init__(self, create=False):
        """Initialize ELMO model

        :param create: create new model without loading, defaults to False
        :type create: bool, optional
        """
        # Training not supported
        if create:
            raise NotImplementedError()

        # FIXME: integrate ELMO in Abby

    def predict(self, features) -> np.ndarray:
        """Predict target using features

        Right now this method does only return the "power" column because we
        are already calling ELMO to generate the execution trace (features).
        In a near future we will translate ELMO model to Python.

        :param features: features to input to the model
        :type features: [[int]] or pandas.DataFrame
        :return: model prediction
        :rtype: numpy.ndarray
        """
        # Nothing to do for ELMO as the dataframe already contains ELMO
        # prediction
        return np.array(features["power"])
