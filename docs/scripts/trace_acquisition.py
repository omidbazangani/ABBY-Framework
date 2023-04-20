#!/usr/bin/env python3

"""
Sample script to acquire traces.
"""

import argparse
import os
import pathlib
import secrets

import numpy as np
import pandas as pd
from serial import Serial
from tqdm import tqdm

import abby


def main(opt):
    # Create destination folder if missing
    dest = pathlib.Path(opt.output).absolute()
    os.makedirs(dest, exist_ok=True)

    with abby.oscilloscope.PS3000a() as ps:
        for algo in tqdm(opt.algorithm):
            # Build firmware for target then upload firmware to target board
            abby.firmware.pio_run(
                opt.board,
                algo,
                upload=True,
                debug=opt.debug,
            )

            # Open serial port after flashing
            with Serial("/dev/ttyUSB0", baudrate=115200, timeout=1) as ser:

                # Repeat acquisition with different input texts
                for _ in tqdm(range(opt.num)):
                    # Input text contains all input data for selected algorithm
                    if opt.input is not None:
                        # Read input text from file
                        input_text = bytes.fromhex(opt.input.readline())
                        input_size = algo.get_input_length() + 1
                        if len(input_text) != input_size:
                            raise IndexError(
                                f"\nInput text {input_text.hex()} does not "
                                f"match size {input_size}"
                            )
                    else:
                        # Random input text
                        input_text = b"\xAE"  # start byte
                        input_text += secrets.token_bytes(algo.get_input_length())

                    # If file already exist, skip
                    output = dest / f"{opt.board}_{algo}_{input_text.hex()}.npy"
                    if output.is_file():
                        continue

                    # Regenerate random code if necessary
                    if algo.name == "generated-code":
                        algo.seed = input_text
                        abby.firmware.pio_run(
                            opt.board,
                            algo,
                            upload=True,
                            debug=opt.debug,
                        )

                    # Acquire trace
                    output_len = 1 + algo.msg_length  # +1 for header
                    _, trace, clock = ps.run_and_acquire(
                        input_text, output_len, ser, average=opt.average
                    )

                    if not opt.no_downsample:
                        # Get the max of each cycle
                        cycles_indexes = abby.processing.find_cycles(clock)
                        downsampled_trace = np.zeros(len(cycles_indexes) - 1)
                        for i, c_index in enumerate(cycles_indexes[:-1]):
                            c_end = cycles_indexes[i + 1]
                            downsampled_trace[i] = np.max(trace[c_index:c_end])
                        downsampled_trace -= np.mean(downsampled_trace)
                        trace = downsampled_trace

                    if not opt.no_crop:
                        # Crop NOP cycles from power trace
                        trace = abby.processing.crop_cycles(trace, threshold=0.005)

                    # Save trace
                    np.save(output, trace)


if __name__ == "__main__":
    # Arguments parser
    parser = argparse.ArgumentParser(
        description="Acquire traces.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        default=False,
        help="silent mode: hide info and warnings, overrides debug",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="debug mode: show debug messages",
    )
    parser.add_argument(
        "-n",
        "--num",
        type=int,
        default=1,
        help="amount of traces for each algorithm, default to 1",
    )
    parser.add_argument(
        "--average",
        type=int,
        default=50,
        help="amount of traces averaged with same input data, default to 50",
    )
    parser.add_argument(
        "-b",
        "--board",
        required=True,
        choices=abby.firmware.environments,
        help="target device to flash",
    )
    parser.add_argument(
        "-a",
        "--algorithm",
        nargs="+",
        default=[abby.firmware.blockcipher.GeneratedCode()],
        choices=abby.firmware.blockcipher.blockciphers,
        type=abby.firmware.get_blockcipher,
        help="algorithm to flash, default to generated code",
    )
    parser.add_argument(
        "--no_downsample",
        action="store_true",
        default=False,
        help="disable downsampling",
    )
    parser.add_argument(
        "--no_crop",
        action="store_true",
        default=False,
        help="disable cropping of NOP instructions",
    )
    parser.add_argument(
        "-i",
        "--input",
        nargs="?",
        type=argparse.FileType("r"),
        help="text file containing input to send, default to random",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="destination folder for saved traces",
    )
    options = parser.parse_args()
    abby.logger.setup_logger("abby", options.quiet, options.debug)
    main(options)
