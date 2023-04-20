# Copyright (C) 2020-2021 Radboud University
# SPDX-License-Identifier: Apache-2.0

"""
Thumbulator wrapper to get an execution trace.
"""

import logging
import tempfile

import pandas as pd

from abby.emulator.base import Emulator

# Local logger
log = logging.getLogger(__name__)


class ThumbulatorEmulator(Emulator):
    """Thumbulator emulator for Cortex-M0.

    This version of Thumbulator was patched by ELMO authors to add ELMO
    power model inside. It was also patched by Abby authors to output needed
    features.

    This class depends on ``elmotrace`` Python module which wrap our modified
    version of ELMO as a Python module.

    When using this emulator, some instruction related to GPIO might create
    unpredictable outputs. To circumvent this, we need a firmware compiled with
    ``ELMO`` flag.
    """

    _features_32bits = [
        "op1_value_current",
        "op2_value_current",
        "op1_value_previous",
        "op2_value_previous",
        "readbus_value_previous",
        "readbus_value_current",
        "writebus_value_previous",
        "writebus_value_current",
    ]

    _features_categorical = [
        "instr_stage3",
        "instr_stage2",
        "instr_stage1",
    ]

    def __init__(self, fw_path):
        """Initialize Thumbulator.

        We are currently using ELMO version of Thumbulator so we also get
        a power trace inside the execution trace.

        :param fw_path: path to the firmware compiled file.
        :type fw_path: str
        :param flash_address: flashing address, defaults to 0x0
        :type flash_address: int, optional
        """
        # FIXME: show error when file is missing
        self.model_path = (
            "/media/lab/HDD/Abby/trained_models/stm32f0308_discovery/elmo.txt"
        )
        self.fw_path = fw_path

        # Build dtypes
        self.dtypes = {
            "power": "float32",
            "opcode": "uint16",
        }
        for n in self._features_32bits:
            self.dtypes[n] = "uint32"

    def run(self, input_data: bytes, output_data_length: int):
        """Run emulation.

        :param input_data: input data to send to the serial port
        :type input_data: bytes
        :return: output data and execution trace
        :rtype: (bytes, [[str or int]])
        """
        import elmotrace

        log.debug(f"Running ELMO on {self.fw_path}")
        with tempfile.NamedTemporaryFile() as f:
            output_data = elmotrace.run(
                str(self.fw_path),
                str(self.model_path),
                input_data,
                output_data_length,
                f.name,
            )
            df = pd.read_csv(
                f.name,
                sep=",",
                names=self._features_categorical
                + self._features_32bits
                + ["power", "opcode"],
                dtype=self.dtypes,
                index_col=False,
                skiprows=1,  # first row has previous data not defined
            )
            log.debug(f"Thumbulator recorded {df.shape[0]} instructions")

        return output_data, df

    @staticmethod
    def crop_nop(df: pd.DataFrame):
        """Truncate data surrounded by NOP instructions.

        Search for operand code `0x46C0` = NOP around the trace and crop without
        including them.

        :param df: execution trace to crop
        :type df: pandas.DataFrame
        :return: cropped execution trace
        :rtype: pandas.DataFrame
        """
        middle_index = len(df) // 2
        nop_indexes = df.index[df["opcode"] == 0x46C0]
        crop_start = max(nop_indexes[nop_indexes < middle_index])
        crop_end = min(nop_indexes[nop_indexes > middle_index])
        df = df.truncate(crop_start + 1, crop_end - 1)
        df = df.reset_index().drop("index", axis=1)
        return df
