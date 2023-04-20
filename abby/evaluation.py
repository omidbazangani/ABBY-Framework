# Copyright (C) 2020-2021 
# SPDX-License-Identifier: Apache-2.0

"""
Utilities to evaluate model quality.
"""

import logging

import numpy as np
from scipy import stats

# Local logger
log = logging.getLogger(__name__)


def ttest(trace_set1, trace_set2) -> np.ndarray:
    """Compute Welch's t-test between two set of traces.

    When a set contains traces with a constant value at a specific index, the
    variance is null and a division by zero occurs. We choose to remplace these
    values by 0 as there is no leakage detected.

    You may use :func:`abby.plot.plot_ttest` to visualize results.

    For example::

        >>> import abby
        >>> trace_set1 = [[0, 0, 0, 1, 0, 0],
        ...               [0, 0, 1, 0, 0, 1]]
        >>> trace_set2 = [[0, 0, 0, 1, 1, 0],
        ...               [0, 0, 1, 0, 0, 0]]
        >>> abby.evaluation.ttest(trace_set1, trace_set2)
        array([0.,  0.,  0.,  0., -1.,  1.])

    :param trace_set1: set of traces
    :type trace_set1: [[float]] or np.ndarray
    :param trace_set2: set of traces
    :type trace_set2: [[float]] or np.ndarray
    :return: computed ttest
    :rtype: np.ndarray
    """
    # Ignore comparison with NaN error
    with np.errstate(invalid="ignore"):
        t, _ = stats.ttest_ind(trace_set1, trace_set2, equal_var=False)

    # Replace NaN with 0, NaN happens when sets are constant which is common
    # when using models. We choose 0 as replacement as the model does not show
    # leakage.
    t = np.nan_to_num(t, nan=0)

    return t


def correlation(traces, reference_samples) -> np.ndarray:
    """Compute Pearson correlation coefficient at each index of traces set.

    To use this function to do a correlation attack, you can compute the Hamming
    weight of an intermediate value for each trace as reference_sample.

    For example::

        >>> import abby
        >>> traces = [[0, 1, 0, 1, 0, 0],
        ...           [1, 0, 1, 1, 1, 0],
        ...           [0, 0, 1, 0, 0, 1]]
        >>> intermediate_values = [0b0, 0b0, 0b1]
        >>> def hw(n: int):
        ...     return sum((n >> i) & 0b1 for i in range(16))
        >>> reference_samples = [hw(i) for i in intermediate_values]
        >>> abby.evaluation.correlation(traces, reference_samples)
        array([-0.5, -0.5, 0.5, -1.0, -0.5, 1.0])

    :param traces: traces set
    :type traces: [[float]] or np.ndarray
    :param reference_samples: reference to correlate, length should match the
        number of traces
    :type reference_samples: [float] or np.ndarray
    :return: correlation result
    :rtype: np.ndarray
    """
    # Compute correlation for each sample of all traces
    length_trace = len(traces[0])
    corr = np.zeros(length_trace)
    traces = np.array(traces)
    for i in range(length_trace):
        trace_samples = traces[:, i]
        corr[i], _ = stats.pearsonr(trace_samples, reference_samples)

    # Replace NaN with 0, NaN happens when sets are constant which is common
    # when using models. We choose 0 as replacement as the model does not show
    # leakage.
    corr = np.nan_to_num(corr, nan=0)

    return corr


def correlation_bruteforce_key_byte(samples, input_data, inter_func):
    """Correlate samples with all possibles values for key byte.

    Correlate samples with the Hamming weight of the intermediate values for
    all 256 values of the key byte. A key byte leading to a higher correlation
    has more probability to be the secret key byte.

    This function can be used when the evaluator knows the position of the
    leakage of one key byte and knows how to compute the intermediate value.

    You may plot the rank of the good key by the number of traces by repeating
    this evaluation with different number of traces.

    :param samples: samples to attack, one sample per trace
    :type samples: [float]
    :param input_data: input data used for each trace, passed to inter_func
    :type input_data: [any]
    :param inter_func: function to compute the intermediate value from
        input_data and key
    :type inter_func: callable
    :return: correlation results for all 256 possibilities
    :rtype: np.ndarray
    """
    # Make sure we have input data for all traces
    assert len(samples) == len(input_data)

    # Bruteforce 256 values for this byte
    corr = np.zeros(256)
    for key_byte in range(256):
        # Compute intermediate values when using this key
        inter_value = [inter_func(i, key_byte) for i in input_data]

        # Correlate using Hamming weight
        inter_samples = [sum((n >> i) & 0b1 for i in range(16)) for n in inter_value]
        corr[key_byte], _ = stats.pearsonr(samples, inter_samples)

    return corr
