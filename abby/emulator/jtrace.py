# Copyright (C) 2020-2021 Radboud University
# SPDX-License-Identifier: Apache-2.0

"""
Segger J-Trace support to get an execution trace.
"""

import logging

from abby.emulator.base import Emulator

# Local logger
log = logging.getLogger(__name__)


class JTraceEmulator(Emulator):
    """J-Trace emulator to control and trace device execution.

    Segger J-Trace is able to trace target in real-time and get cycle-accurate
    execution traces.
    """

    def __init__(self, fw_path, flash_address=0):
        """Initialize J-Trace.

        :param fw_path: path to the firmware compiled file.
        :type fw_path: str
        :param flash_address: flashing address, defaults to 0x0
        :type flash_address: int, optional
        """
        try:
            import pylink
        except ImportError as e:
            raise ImportError("You need to install pylink-square module.") from e

        # Initiate connection
        self.jlink = pylink.JLink()
        self.jlink.open()
        log.debug(f"Opened connection with {self.jlink.product_name}")

        # Version check
        if self.jlink.firmware_outdated():
            raise RuntimeError("J-Trace firmware is outdated.")

        # Connect to target
        self.jlink.connect("TARGET NAME")

        # To trace we require ETM support
        if not self.jlink.etm_supported():
            raise NotImplementedError("Target does not support ETM.")

        # Flash target
        self.jlink.flash_file(fw_path, flash_address)

    def run(self, input_data: bytes):
        """Run emulation.

        :param input_data: input data to send to the serial port
        :type input_data: bytes
        :return: output data and execution trace
        :rtype: (bytes, [[str or int]])
        """
        raise NotImplementedError()
