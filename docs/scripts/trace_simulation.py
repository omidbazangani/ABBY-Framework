#!/usr/bin/env python3

"""
Emulate target to output features and estimated trace.
"""

import argparse
import os
import pathlib
import secrets

import numpy as np
from tqdm import tqdm

import abby


def main(opt):
    # Create destination folder if missing
    dest = pathlib.Path(opt.output).absolute()
    os.makedirs(dest, exist_ok=True)

    for algo in tqdm(opt.algorithm):
        # Build firmware for simulation
        # `qemu` parameter remove RCC initialization as emulation does not
        # implement RCC
        fw_path = abby.firmware.pio_run(
            opt.board,
            algo,
            qemu=True,
            debug=opt.debug,
        )

        # Initiate QEMU
        emulator = abby.emulator.QEMUEmulator(fw_path, opt.board)

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
            if opt.only_power:
                output = dest / f"{opt.board}_{algo}_{input_text.hex()}.npy"
            else:
                output = dest / f"{opt.board}_{algo}_{input_text.hex()}.csv"
            if output.is_file():
                continue

            # Regenerate random code if necessary
            if algo.name == "generated-code":
                algo.seed = input_text
                fw_path = abby.firmware.pio_run(
                    opt.board,
                    algo,
                    elmo=True,
                    debug=opt.debug,
                )
                emulator = abby.emulator.QEMUEmulator(fw_path)

            # Emulate target
            output_len = 1 + algo.msg_length  # +1 for header
            _, execution_trace = emulator.run(input_text, output_len)
            if not opt.no_crop:
                execution_trace = emulator.crop_nop(execution_trace).drop(
                    "opcode", axis=1
                )

            # Predict using model and save
            execution_trace["power"] = opt.model.predict(execution_trace)
            if opt.only_power:
                np.save(output, execution_trace["power"])
            else:
                execution_trace.to_csv(output, index=False)


if __name__ == "__main__":
    # Arguments parser
    parser = argparse.ArgumentParser(
        description="Emulate target to output features and estimated trace.",
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
        "-b",
        "--board",
        required=True,
        choices=abby.firmware.environments,
        help="target device to simulate",
    )
    parser.add_argument(
        "-a",
        "--algorithm",
        nargs="+",
        default=[abby.firmware.blockcipher.GeneratedCode()],
        choices=abby.firmware.blockcipher.blockciphers,
        type=abby.firmware.get_blockcipher,
        help="algorithm to simulate, default to generated code",
    )
    parser.add_argument(
        "-m",
        "--model",
        required=True,
        type=abby.model.get_model,
        help="model to use to estimate trace, format `type,path`",
    )
    parser.add_argument(
        "--no_crop",
        action="store_true",
        default=False,
        help="disable cropping of NOP instructions",
    )
    parser.add_argument(
        "--only_power",
        action="store_true",
        default=False,
        help="save only power in Numpy array",
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
