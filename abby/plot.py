# Copyright (C) 2020-2021 
# SPDX-License-Identifier: Apache-2.0

"""
Plotting helpers.
"""

import logging

import matplotlib.pyplot as plt
import numpy as np

# Local logger
log = logging.getLogger(__name__)


def plot_ttest(ttest, x_axis=None, xlim=None, absolute=False, **kwargs):
    """Plot t-test result on current Matplotlib figure.

    This helper function adds the 4.5 threshold line (99.999% confidence) and
    do some common formatting.

    :param ttest: t-test result
    :type ttest: [float] or np.ndarray
    :param x_axis: X-axis used for plotting, defaults to simple range
    :type x_axis: [float] or np.ndarray, optional
    :param xlim: X-axis range to plot, defaults to full range
    :type xlim: (float, float), optional
    :param absolute: plot absolute value of t-test, defaults to False
    :type absolute: bool, optional
    """
    if absolute:
        # Compute t-test absolute value
        ttest = np.abs(ttest)
        plt.yscale("log")
        plt.ylabel("absolute of t-test")
    else:
        plt.ylabel("t-test value")
        plt.axhline(y=-4.5, color="r", linestyle=":")

    if x_axis is None:
        # Default to simple range
        x_axis = np.arange(len(ttest))

    plt.axhline(y=4.5, color="r", linestyle=":")
    plt.plot(x_axis, ttest, "-", **kwargs)

    # Set X-axis range
    if xlim is None:
        plt.xlim((x_axis[0], x_axis[-1]))
    else:
        plt.xlim(xlim)

    if absolute:
        # Start from 1 when plotting with log scale
        plt.ylim((1, plt.ylim()[1]))


def plot_fourier(
    trace,
    freq_estimated=8e6,
    freq_precision=1e3,
    threshold=0.0002,
    sample_rate=500e6,
):
    """Plot trace and Fourier transform on current Matplotlib figure.

    The Fourier transform of trace should contain a spike at target clock
    frequency. You can use this function to inspect your target clock
    frequency.

    For example::

        >>> plt.figure(figsize=(16,10))
        >>> abby.plot.plot_fourier(trace)
        >>> plt.show()

    :param trace: side-channel trace to inspect
    :type trace: [float] or np.ndarray
    :param freq_estimated: estimated clock frequency in Hz, defaults to 8 MHz
    :type freq_estimated: float, optional
    :param freq_precision: clock frequency precision in Hz, defaults to 1 kHz
    :type freq_precision: float, optional
    :param threshold: threshold line for spikes detection, defaults to 0.0002
    :type threshold: float, optional
    :param sample_rate: trace sampling rate in Hz, defaults to 500 MHz
    :type sample_rate: float, optional
    """
    # Plot trace
    plt.subplot(311)
    plt.plot(np.arange(len(trace)) / sample_rate, trace)
    plt.xlabel("time (s)")

    # Compute FFT, normalize by dividing by trace length
    fft = np.fft.rfft(trace) / len(trace)
    freqs = np.fft.rfftfreq(trace.size, d=1.0 / sample_rate)

    # Plot FFT
    plt.subplot(312)
    plt.plot(freqs, np.abs(fft))
    plt.xlabel("f (Hz)")
    plt.xlim((0, freq_estimated * 1.5))

    # Plot zoomed FFT
    plt.subplot(313)
    plt.plot(freqs, np.abs(fft))
    plt.xlabel("f (Hz)")
    plt.axhline(y=threshold, color="r", linestyle=":")
    plt.axvline(x=freq_estimated - freq_precision, color="b", linestyle=":")
    plt.axvline(x=freq_estimated + freq_precision, color="b", linestyle=":")
    plt.xlim(
        (
            freq_estimated - freq_precision * 50,
            freq_estimated + freq_precision * 50,
        )
    )


def instruction_frequency_table(
    execution_trace, x="instr_stage3", y="instr_stage2", instructions=None
) -> str:
    """Generate HTML table with each couple of instructions frequency.

    :param execution_trace: execution trace to analyse
    :type execution_trace: pandas.DataFrame
    :param x: vertical axis of table, defaults to "instr_stage3"
    :type x: str, optional
    :param y: horizontal axis of table, defaults to "instr_stage2"
    :type y: str, optional
    :param instructions: list of instruction to show, defaults to automatic
    :type instructions: [str], optional
    :return: HTML code
    :rtype: str
    """
    header = """<meta charset="utf-8">\n<style>
    /* Table style */
    table { border-collapse: collapse; }
    td { height: 20px; padding: 0; }
    th { padding: 0 1px; font-size: 9pt; }
    td div { height: inherit; }
    </style>"""

    def c_format(s):
        """Format number as a HTML square."""
        if np.isnan(s) or s == 0:
            return ""
        s = 200 * (1 - s)
        return f'<div style="background:rgb({s},{s},{s})"></div>'

    # Count instructions
    freqs = execution_trace.groupby([x, y]).size()
    freqs = freqs / max(freqs)

    # Reindex and replace NaN
    if instructions is not None:
        new_index = [(i, j) for i in instructions for j in instructions]
        freqs = freqs.reindex(new_index)
    freqs.fillna(0, inplace=True)

    # Generate table
    freqs = freqs.unstack()
    return header + freqs.to_html(
        formatters=[c_format] * len(freqs.columns),
        escape=False,
    )
