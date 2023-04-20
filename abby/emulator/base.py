# Copyright (C) 2020-2021 Radboud University
# SPDX-License-Identifier: Apache-2.0

"""
Base emulator
"""

import logging

# Local logger
log = logging.getLogger(__name__)


class Emulator:
    """Common interface for emulators

    All emulators should inherit this base class.
    """

    def run(self, input_data: bytes):
        """Run emulation.

        :param input_data: input data to send to the serial port
        :type input_data: bytes
        :return: output data and execution trace
        :rtype: (bytes, [[str or int]])
        """
        raise NotImplementedError()
