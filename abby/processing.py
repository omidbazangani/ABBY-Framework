# Copyright (C) 2020-2021 
# SPDX-License-Identifier: Apache-2.0

"""
Trace processing tools.
"""

import logging

import numpy as np
from scipy import signal

# Local logger
log = logging.getLogger(__name__)


def crop_cycles(trace, threshold, samples_per_cycle=1):
    """Crop cycles at beginning and end of trace.

    Abby firmware injects 500 ``NOP`` instructions before and after cipher
    execution for alignment and debug purposes. We search for a group of
    ``500*samples_per_cycle`` samples under the threshold.

    :param trace: trace to process
    :type trace: [float] or np.ndarray
    :param threshold: threshold for cropping
    :type threshold: float
    :param samples_per_cycle: number of samples for each cycle,
        default to 1
    :type samples_per_cycle: int, optional
    :return: cropped trace
    :rtype: np.ndarray
    """
    # TODO: implement samples_per_cycle usage
    trace = np.array(trace)

    # Search groups of 500 NOP instructions
    above_ts = np.abs(trace) > threshold
    index_ts = np.array(
        [x for x in range(len(above_ts)) if np.all(above_ts[x : x + 450] == 0)]
    )

    # Split into two groups
    p = np.mean(index_ts)
    index_start = max(index_ts[index_ts < p]) + 450
    index_end = min(index_ts[index_ts > p])

    return trace[index_start:index_end]


def find_clock_freq_phase(
    trace,
    freq_estimated=8e6,
    freq_precision=1e3,
    threshold=0.0002,
    sample_rate=250e6,
):
    """Find the CPU clock frequency and phase from the trace.

    Compute the fast Fourier transform of the trace then search for the spike
    corresponding to clock frequency. Using the frequency and phase from
    this spike, you can align trace with clock cycles.

    Using this function to cut clock cycles is rather imprecise when clock
    jitter occurs. Using the crystal oscillator on a STM32F0 Discovery board, we
    observed different clock frequency between executing ``NOP`` instructions
    and ``STR`` instructions. If you are profiling a small amount of
    instructions surrounded by ``NOP`` instructions, you might want to use
    :func:`abby.processing.crop_cycles` with
    ``samples_per_cycle = sample_rate / freq_estimated``.

    You can visualize what this function does using
    :func:`abby.plot.plot_fourier`.

    :param trace: side-channel trace to process
    :type trace: [float] or np.ndarray
    :param freq_estimated: estimated clock frequency in Hz, defaults to 8 MHz
    :type freq_estimated: float, optional
    :param freq_precision: clock frequency precision in Hz, defaults to 1 kHz
    :type freq_precision: float, optional
    :param threshold: threshold line for spikes detection, defaults to 0.0002
    :type threshold: float, optional
    :param sample_rate: trace sampling rate in Hz, defaults to 250 MHz
    :type sample_rate: float, optional
    :return: found frequency and phase
    :rtype: (float, float)
    """
    # FFT normalized by dividing by trace length
    fft = np.fft.rfft(trace) / len(trace)
    freqs = np.fft.rfftfreq(len(trace), d=1.0 / sample_rate)

    # Find all spikes that are higher than threshold
    spikes = np.argwhere(np.abs(fft) >= threshold)
    spikes_freqs = freqs[spikes]
    spikes_values = fft[spikes]

    # Search frequencies in range estimated +/- precision
    near_index = np.abs(spikes_freqs - freq_estimated) <= freq_precision
    freqs = spikes_freqs[near_index]
    angles = np.angle(spikes_values[near_index]) / np.pi * 180
    if len(freqs) < 1:
        raise ValueError("Did not find CPU frequency")
    if len(freqs) > 1:
        raise ValueError("Found multiple CPU frequency")
    return freqs[0], angles[0]


def find_cycles(clock: np.ndarray, freq_estimated=8e6, sample_rate=250e6):
    """Find CPU cycles from clock signal.

    :param clock: acquired clock signal
    :type clock: np.ndarray
    :param freq_estimated: estimation of the clock frequency in Hz, used for
        high pass filtering, defaults to 8 MHz
    :type freq_estimated: float, optional
    :param sample_rate: trace sampling rate in Hz, defaults to 250 MHz
    :type sample_rate: float, optional
    :return: indexes of cycles beginning
    :rtype: numpy.ndarray
    """
    # Filter clock signal with second order high pass filter
    sos = signal.butter(2, freq_estimated, "hp", fs=sample_rate, output="sos")
    clock = signal.sosfilt(sos, clock)

    # Get falling edges of clock signal
    cycles_indexes = np.where((clock[:-1] > 0) & (clock[1:] < 0))[0]
    return cycles_indexes
