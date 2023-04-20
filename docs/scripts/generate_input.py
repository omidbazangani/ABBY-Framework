#!/usr/bin/env python3

"""
Generate input data for acquisition and simulation.
"""

import argparse
from secrets import token_bytes

from tqdm import tqdm

import abby


def main(opt):
    # For each algorithm and trace create a input text
    for algo in tqdm(opt.algorithm):
        for _ in range(opt.num):
            # Start byte
            input_text = b"\xAE"

            # Key
            if opt.key:
                assert len(opt.key) >= algo.key_length, "Key too short"
                input_text += opt.key[: algo.key_length]
            else:
                input_text += token_bytes(algo.key_length)

            # Random initialization value or mask
            input_text += token_bytes(algo.iv_length + algo.mask_length)

            # Message
            if opt.msg:
                assert len(opt.msg) >= algo.msg_length, "Message too short"
                input_text += opt.msg[: algo.msg_length]
            else:
                input_text += token_bytes(algo.msg_length)

            opt.output.write(input_text.hex() + "\n")

            # If TVLA mode, then also add a version with a random message
            if opt.tvla:
                input_text = input_text[: -algo.msg_length] + token_bytes(
                    algo.msg_length
                )
                opt.output.write(input_text.hex() + "\n")


if __name__ == "__main__":
    # Arguments parser
    parser = argparse.ArgumentParser(
        description="Generate input data for acquisition and simulation.",
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
        "-a",
        "--algorithm",
        nargs="+",
        default=[abby.firmware.blockcipher.GeneratedCode],
        choices=abby.firmware.blockcipher.blockciphers,
        type=abby.firmware.get_blockcipher,
        help="algorithm to simulate, default to generated code",
    )
    parser.add_argument(
        "--key",
        type=bytes.fromhex,
        help="set to fix the key, default to random",
    )
    parser.add_argument(
        "--msg",
        type=bytes.fromhex,
        help="set to fix the message, default to random",
    )
    parser.add_argument(
        "--tvla",
        action="store_true",
        default=False,
        help=(
            "alternate between fixed and random messages, double output size. "
            "This is used to show leakage that depends on data using Test "
            "Vector Leakage Assessment."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        type=argparse.FileType("w"),
        help="text file containing input to send",
    )
    options = parser.parse_args()
    abby.logger.setup_logger("abby", options.quiet, options.debug)
    main(options)
