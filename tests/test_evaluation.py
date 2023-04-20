# Copyright (C) 2020-2021 
# SPDX-License-Identifier: Apache-2.0

"""Test abby.evaluation
"""

import numpy as np

from abby.evaluation import correlation, ttest


def test_ttest():
    """Test t-test computed value with two simple sets of traces.

    We also check that constant values does not returns NaN.
    """
    trace_set1 = [[0, 0, 0, 1, 0, 0], [0, 0, 1, 0, 0, 1]]
    trace_set2 = [[0, 0, 0, 1, 1, 0], [0, 0, 1, 0, 0, 0]]
    t = ttest(trace_set1, trace_set2)
    assert np.all(t == np.array([0.0, 0.0, 0.0, 0.0, -1.0, 1.0]))


def test_correlation():
    """Test correlation computed value with a simple set of traces."""
    traces = [[0, 1, 0, 1, 0, 0], [1, 0, 1, 1, 1, 0], [0, 0, 1, 0, 0, 1]]
    reference_samples = [0, 0, 1]
    corr = correlation(traces, reference_samples)
    diff = corr - np.array([-0.5, -0.5, 0.5, -1.0, -0.5, 1.0])
    assert np.all(diff < 0.1)
