# Copyright (C) 2020-2021 
# SPDX-License-Identifier: Apache-2.0

"""Test abby.processing
"""

import numpy as np

from abby.processing import crop_cycles, find_clock_freq_phase


def test_crop_cycles():
    """Test that crop_cycles does not overcrop or undercrop traces."""
    trace = [1] * 500 + [0] * 500 + [1] * 10 + [0] * 500 + [1] * 500
    result = crop_cycles(trace, 0.5)
    assert len(result) == 10
    assert np.all(result == 1)


def test_find_clock_freq_phase():
    """Test that find_clock_freq_phase can find the frequency of phase of a
    sinusoide.
    """
    freq = 1001  # Hz
    sample_rate = 1e4  # Hz
    t = np.arange(0, 1, 1 / sample_rate)
    trace = np.sin(2 * np.pi * freq * t)
    found_freq, found_angle = find_clock_freq_phase(
        trace,
        freq_estimated=1000,
        freq_precision=10,
        threshold=0.0002,
        sample_rate=sample_rate,
    )
    assert round(found_freq) == freq
    assert round(found_angle) == -90
