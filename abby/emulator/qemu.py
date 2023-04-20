# Copyright (C) 2020-2021 Radboud University
# SPDX-License-Identifier: Apache-2.0

"""
QEMU emulator.
"""

import logging
import os
import socket
import subprocess
import tempfile

import pandas as pd

from abby.emulator.base import Emulator

# Local logger
log = logging.getLogger(__name__)


class QEMUEmulator(Emulator):
    """QEMU emulator.

    Require a patched version of QEMU with logcorestate TCG plugin.
    """

    qemu_path = "/home/sirena/abby/qemu_emulation/qemu/build/qemu-system-arm"
    plugin_path = (
        "/home/sirena/abby/qemu_emulation/qemu/build/contrib/plugins/liblogcorestate.so"
    )

    # Board profiles store QEMU machine name and trigger addresses
    boards_profiles = {
        "microbit": ("bbcmicrobit", "1342178568", "1342178572"),
        "stm32vldiscovery": ("disco_f100rb", "1073809424", "1073809424"),
        "stm32f0discovery": ("disco_f051r8", "1073809424", "1073809424"),  # TODO
    }

    def __init__(self, fw_path: str, board: str):
        """Initialize QEMU.

        We start QEMU machine only once, then feed the input via TCP.

        :param fw_path: path to the firmware compiled file.
        :type fw_path: str
        :param board: Board to emulate.
        :type board: str
        """
        # Get memory physical address of trigger begin and end (GPIO write)
        if board not in self.boards_profiles:
            raise NotImplementedError("unknown board profile")
        machine, trigger_begin, trigger_end = self.boards_profiles[board]

        # Init QEMU
        log.debug(f"Initializing QEMU machine {machine} with {fw_path}")
        self.trace_path = os.path.join(tempfile.mkdtemp(), "execution.csv")
        cmd = [
            self.qemu_path,
            "-M",
            machine,
            "-kernel",
            fw_path,
            "-serial",
            "tcp::5678,server=on,wait=off",
            "-nographic",
            "-plugin",
            f"{self.plugin_path},arg={self.trace_path},"
            f"arg={trigger_begin},arg={trigger_end},arg=3",
            "-d",
            "plugin",
        ]
        self.proc = subprocess.Popen(cmd)

        # Init socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(("127.0.0.1", 5678))

    def run(self, input_data: bytes, output_data_length: int):
        """Send input data and return output data and execution trace.

        :param input_data: input data to send to the serial port
        :type input_data: bytes
        :param output_data_length: expected length of output
        :type output_data_length: int
        :return: output data and execution trace
        :rtype: (bytes, [[str or int]])
        """
        # Send input_data to TCP socket and get output
        self.socket.sendall(input_data)
        output_data = b""
        while True:
            data = self.socket.recv(1024)
            if data == "":
                break
            output_data += data

        # Load output CSV
        df = pd.read_csv(self.trace_path)
        log.debug(f"Recorded {df.shape[0]} instructions")

        return output_data, df

    def __del__(self):
        """Close socket and kill QEMU."""
        self.socket.close()
        self.proc.terminate()
