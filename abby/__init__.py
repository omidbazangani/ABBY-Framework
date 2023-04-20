# Copyright (C) 2020-2021 
# SPDX-License-Identifier: Apache-2.0

"""
Abby is a framework to build side-channel models and evaluate them.
"""

import abby.emulator as emulator
import abby.evaluation as evaluation
import abby.firmware as firmware
import abby.logger as logger
import abby.model as model
import abby.oscilloscope as oscilloscope
import abby.plot as plot
import abby.processing as processing

try:
    from abby.version import version as __version__
except ImportError:
    __version__ = "dev"

# See https://www.python.org/dev/peps/pep-0008/#module-level-dunder-names
__all__ = [
    "evaluation",
    "firmware",
    "logger",
    "model",
    "oscilloscope",
    "plot",
    "processing",
    "__version__",
]
