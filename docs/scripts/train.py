#!/usr/bin/env python3

"""
Sample file to train a model on a set of data
"""

import argparse
import glob
import pathlib

import abby


def main(opt):
    # Get all CSV files in provided folder
    data_files = glob.glob(str(pathlib.Path(opt.input) / "*.csv"))

    # Create and train new model
    model = abby.model.get_model(opt.output, create=True)
    model.fit(data_files)
    model.save()


if __name__ == "__main__":
    # Arguments parser
    parser = argparse.ArgumentParser(
        description="Learn a new model.",
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
        "-i",
        "--input",
        required=True,
        help="folder containing training data in CSV format",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="xgb,model.json",
        help="new trained model, format `type,path`",
    )
    options = parser.parse_args()
    abby.logger.setup_logger("abby", options.quiet, options.debug)
    main(options)
