# Copyright (C) 2020-2021 Radboud University
# SPDX-License-Identifier: Apache-2.0

"""
Emulators to generate execution traces from firmware and input data.
These execution traces are required to fit a model or do prediction.
"""

from abby.emulator.base import Emulator
from abby.emulator.jtrace import JTraceEmulator
from abby.emulator.qemu import QEMUEmulator
from abby.emulator.thumbulator import ThumbulatorEmulator

__all__ = [
    "Emulator",
    "JTraceEmulator",
    "QEMUEmulator",
    "ThumbulatorEmulator",
]
