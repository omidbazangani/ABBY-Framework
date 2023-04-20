# Copyright (C) 2020-2021 
# SPDX-License-Identifier: Apache-2.0

"""Test abby.emulator
"""

import pandas as pd
import pytest

from abby.emulator import Emulator, ThumbulatorEmulator


def test_base_class():
    """Test that emulator base class cannot emulate."""
    emu = Emulator()
    with pytest.raises(NotImplementedError):
        emu.run(b"abcd")


def test_crop_nop_thumbulator():
    """Test Thumbulator emulator cropping function."""
    df = pd.DataFrame.from_dict(
        {
            "instruction": ["A", "B", "C"],
            "opcode": [0x46C0, 0, 0x46C0],
        }
    )
    df = ThumbulatorEmulator.crop_nop(df)
    assert len(df) == 1
