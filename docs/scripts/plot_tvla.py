#!/usr/bin/env python3

"""
Plot t-test between sets of traces.
"""

import argparse
import glob
import os
import pathlib

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from tqdm import tqdm

import abby


def main(opt):
    # Create output folder
    dest_dir = pathlib.Path(opt.output).parent.absolute()
    os.makedirs(dest_dir, exist_ok=True)

    # Check sizes
    N = len(opt.legend)
    assert len(opt.set1_input) == N
    assert len(opt.set2_input) == N

    # Setup figure
    sns.set()
    plt.figure(figsize=(5, 3))
    plt.title(opt.title)

    for i in range(N):
        # Load traces into two sets
        set1 = []
        paths = list(glob.glob(str(pathlib.Path(opt.set1_input[i]) / "*.npy")))
        for trace_path in tqdm(paths):
            set1.append(np.load(trace_path))

        set2 = []
        paths = list(glob.glob(str(pathlib.Path(opt.set2_input[i]) / "*.npy")))
        for trace_path in tqdm(paths):
            set2.append(np.load(trace_path))

        # Crop sets
        min_len = min(min([len(t) for t in set1]), min([len(t) for t in set2]))
        set1 = np.array([t[:min_len] for t in set1])
        set2 = np.array([t[:min_len] for t in set2])

        # Compute t-test
        ttest = abby.evaluation.ttest(set1, set2)

        # Count leaky points
        leaky_samples = sum(np.abs(np.nan_to_num(ttest)) > 4.5)
        print(
            f"Leaky points for {opt.legend[i]} (>4.5): "
            f"{leaky_samples} / {len(ttest)}, "
            f"{leaky_samples/len(ttest)*100}%"
        )

        abby.plot.plot_ttest(ttest, absolute=True, alpha=0.6, label=opt.legend[i])

    # Save figure
    plt.xlabel(opt.xlabel)
    plt.legend(fontsize="x-small", loc="upper right")
    if opt.xlim:
        plt.xlim(opt.xlim)
    plt.tight_layout()
    plt.savefig(opt.output)


if __name__ == "__main__":
    # Arguments parser
    parser = argparse.ArgumentParser(
        description="Compute t-test between trace sets.",
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
        "--title",
        default="TVLA fixed-vs.-random data",
        help="title of the figure",
    )
    parser.add_argument(
        "--xlabel",
        default="instruction",
        help="label of X axis, default to cycles",
    )
    parser.add_argument(
        "--legend",
        nargs="+",
        default=[""],
        help="legend",
    )
    parser.add_argument(
        "--xlim",
        nargs=2,
        help="plot between these two limits",
    )
    parser.add_argument(
        "-i1",
        "--set1_input",
        required=True,
        nargs="+",
        help="folder(s) containing first set of traces in Numpy format",
    )
    parser.add_argument(
        "-i2",
        "--set2_input",
        required=True,
        nargs="+",
        help="folder(s) containing second set of traces in Numpy format",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="tvla.pdf",
        help="save figure to path as PDF",
    )
    options = parser.parse_args()
    abby.logger.setup_logger("abby", options.quiet, options.debug)
    main(options)
