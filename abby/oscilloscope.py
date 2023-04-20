# Copyright (C) 2020-2021 
# SPDX-License-Identifier: Apache-2.0

"""
Oscilloscope abstraction layer.

This module automates traces acquisition process.
"""

import logging
from time import sleep

import numpy as np

# Local logger
log = logging.getLogger(__name__)


class Oscilloscope:
    """Common interface for oscilloscope

    This class can be used as a context manager such as
    ``with Oscilloscope(param) as osc:``. Doing this will automatically close
    connection on error.

    All oscilloscopes should inherit this base class to get a common
    abstraction layer.
    """

    def __init__(self):
        """Initialize an oscilloscope"""
        log.info("Connecting")
        super().__init__()

    def __enter__(self):
        """For use with context manager.

        :return: oscilloscope object
        :rtype: Oscilloscope
        """
        return self

    def __exit__(self, *args, **kwargs):
        """Called on context close."""
        log.info("Closing connection")
        self.close()

    def close(self):
        """Close connection"""
        raise NotImplementedError()

    def arm(self):
        """Arm to acquire next trigger"""
        raise NotImplementedError()

    def get_trace(self, trigger_crop=True):
        """Download acquired data and return side channel trace

        Trace will be a numpy array with float64 samples.

        :param trigger_crop: crop trace using trigger signal, defaults to True
        :type trigger_crop: bool, optional
        :return: acquired trace and clock
        :rtype: (np.ndarray, np.ndarray)
        """
        raise NotImplementedError()

    def run_and_acquire(self, input_txt: bytes, output_len: int, serial, average=1):
        """Acquire a trace with clock while an algorithm is running

        Arm the oscilloscope, send input data to serial to trigger and then
        wait for returned serial data.

        Set ``average`` parameter to do multiple acquisitions and reduce noise.

        :param input_txt: input data
        :type input_txt: bytes
        :param output_len: size of the returned data to expect
        :type output_len: int
        :param serial: serial device
        :type serial: serial.Serial
        :param average: amount of acquisitions to average, default to 1
        :type average: int, optional
        :raises IndexError: if timeout when waiting for message
        :return: received message and acquired trace and clock
        :rtype: (bytes, np.ndarray, np.ndarray)
        """
        traces, clocks = [], []
        for _ in range(average):
            # Arm scope then send input_txt to trigger acquisition
            log.debug(f"Arm picoscope and send input text: {input_txt.hex()}")
            self.arm()
            serial.write(input_txt)

            # Receive output text
            log.debug(f"Waiting for {output_len} bytes from serial")
            output_txt = b""
            for i in range(output_len):
                try:
                    b = serial.read(1)[0]
                except IndexError as e:
                    raise IndexError(f"Timeout while receiving {i}-th byte") from e
                output_txt += bytes([b])

            # Download power trace from the oscilloscope
            trace, clock = self.get_trace()
            traces.append(trace)
            clocks.append(clock)

        # Return average, crop to smallest trace
        min_length = min([len(t) for t in traces])
        traces = np.array([t[:min_length] for t in traces])
        clocks = np.array([t[:min_length] for t in clocks])
        return output_txt, np.average(traces, axis=0), np.average(clocks, axis=0)


class Chipwhisperer(Oscilloscope):
    """Chipwhisperer Nano, Lite and Pro support.

    See <https://chipwhisperer.readthedocs.io/en/latest/api.html> for API
    documentation.
    """

    def __init__(self, type=None, sn=None):
        """Initialize Chipwhisperer.

        :param type: scope type to connect to. Types
            can be found in chipwhisperer.scopes module. Defaults to auto.
        :type type: ScopeTemplate, optional
        :param sn: serial number to connect to. Defaults to auto.
        :type sn: str, optional
        :raises ImportError: if chipwhisperer module is missing
        """
        try:
            from chipwhisperer import scope
        except ImportError as e:
            raise ImportError("You need to install chipwhisperer module.") from e
        super().__init__()

        # Init OpenADC or CWNano with sane defaults
        self.scope = scope(type=type, sn=sn)
        self.scope.default_setup()

    def close(self):
        """Close connection"""
        self.scope.dis()

    def arm(self):
        """Arm to acquire next trigger"""
        self.scope.arm()

    def get_trace(self):
        """Download acquired data and return side channel trace

        Trace will be a numpy array with float64 samples.

        :return: acquired trace
        :rtype: np.ndarray
        :raises TimeoutError: if acquisition timed out
        """
        # Wait for oscilloscope to be ready
        log.debug("Waiting for acquisition")
        timeout = self.scope.capture()
        if timeout:
            raise TimeoutError("Acquisition timed out.")

        # Download data
        log.debug("Downloading traces")
        trace = self.scope.get_last_trace()

        return trace


class PS3000a(Oscilloscope):
    """Abstraction on top of colinoflynn/pico-python for Picoscope 3000a series

    We consider that signal is measured on channel A,
    external clock on channel B and trigger on channel EXT.
    """

    def __init__(
        self, signal_range=50e-3, clock_range=2.0, sample_interval=4e-9, duration=2e-3
    ):
        """Initialize Picoscope 3000a series

        :param signal_range: range of channel A, defaults to 50 mV
        :type signal_range: float, optional
        :param clock_range: range of channel B, defaults to 2.0 V
        :type clock_range: float, optional
        :param sample_interval: time interval between samples in seconds,
            defaults to 4 ns
        :type sample_interval: float, optional
        :param sample_interval: time duration of the acquisition, defaults to
            2 ms
        :type sample_interval: float, optional
        :raises ImportError: if picoscope module is missing
        """
        try:
            from picoscope.ps3000a import PS3000a as ps_PS3000a
        except ImportError as e:
            raise ImportError("You need to install picoscope module.") from e

        super().__init__()
        self.ps = ps_PS3000a()

        # Channel A is connected to the current probe
        # Channel B is connected to the clock
        # Channel EXT is connected to the trigger
        self.ps.setChannel(channel="A", coupling="DC", VRange=signal_range)
        self.ps.setChannel(channel="B", coupling="AC", VRange=clock_range)
        self.ps.setSimpleTrigger("External", threshold_V=1.0, timeout_ms=10000)

        # One capture at a time and allocate all memory to this acquisition
        self.ps.setNoOfCaptures(1)
        self.ps.memorySegments(1)

        # Set sample interval and total acquisition time
        self.ps.setSamplingInterval(sample_interval, duration)

    def close(self):
        """Close connection"""
        self.ps.close()

    def arm(self):
        """Arm to acquire next trigger

        Sleep 100ms to make sure the device armed.
        """
        self.ps.runBlock()

        # Wait a bit for arming process
        sleep(0.1)

    def get_trace(self):
        """Download acquired data and return side channel trace

        Trace will be a numpy array with float64 samples.

        :return: acquired trace and clock
        :rtype: (np.ndarray, np.ndarray)
        """
        # Wait for oscilloscope to be ready
        log.debug("Waiting for acquisition")
        self.ps.waitReady()

        # Download data from channel A and B
        log.debug("Downloading traces")
        trace = self.ps.getDataV(channel="A")
        clock = self.ps.getDataV(channel="B")

        return trace, clock
