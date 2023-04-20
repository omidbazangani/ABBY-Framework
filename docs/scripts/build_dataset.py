#!/usr/bin/env python3

"""
Build a dataset using acquisitions and side channel simulator data.

Acquisition samples/cycle must match simulator.
"""

import argparse
import glob
import os
import pathlib
from multiprocessing import Pool

import dtw
import numpy as np
import pandas as pd

import abby


def acquisition_simulation_to_dataset(paths):
    """Align acquisition and simulation using Dynamic Time Warping.

    :param paths: pair of acquisition, simulation and output
    :type paths: (str, str, str)
    """
    print(paths)
    path_acq, path_sim, output = paths
    acquisition = np.load(path_acq)
    simulation = pd.read_csv(path_sim)

    # Create a non cycle-accurate power trace using estimated power
    trace_elmo = []
    trace_elmo_row = []
    for i, row in simulation.iterrows():
        # trace_elmo += [row["power"]] * int(row["nb_cycles"])
        # trace_elmo_row += [row] * int(row["nb_cycles"])
        # Ignore nb cycles
        trace_elmo += [row["power"]]
        trace_elmo_row += [row]
    df = simulation.drop(["power", "nb_cycles"], axis=1, errors="ignore")

    # DTW alignment
    # log.debug("Aligning traces with DTW")
    # TODO: maybe we can use something better that euclidean,
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.cdist.html
    alignment = dtw.dtw(
        x=acquisition,  # query
        y=trace_elmo,  # reference
        keep_internals=True,
        dist_method="euclidean",  # see scipy.spatial.distance.cdist
        # asymmetric: slope constrained between 0 and 2
        # Matches each element of the query time series exactly once,
        # so the warping path index2~index1 is guaranteed to be single-valued.
        # Normalized by N (length of query).
        step_pattern="asymmetric",
        window_type="slantedband",
        window_args={"window_size": 10},
    )
    # log.info(f"Distance from real trace: {alignment.normalizedDistance:.6f}")

    # Annotate instructions
    # This code updates the dataframe with the number of cycles
    # log.debug("Updating instructions trace with found cycles count")
    last_index1 = -1
    last_n = -1
    df["nb_cycles"] = [1] * len(df)
    df["power"] = [np.nan] * len(df)
    for i in range(len(alignment.index1)):
        x, index1 = alignment.index1[i], alignment.index2[i]
        if index1 != last_index1:
            last_index1 = index1
            row = trace_elmo_row[index1]
        else:
            # A cycle was added to last instruction

            # increase nb of cycles in dataset
            n = trace_elmo_row[index1].name
            df.loc[n, "nb_cycles"] += 1
            continue

        if last_n == row.name:
            continue

        last_n = row.name

        # store power in dataset
        df.loc[row.name, "power"] = acquisition[x]

    df = df.dropna()
    # TODO: df = df.fillna(method="pad")
    df.to_csv(output, index=False)


def main(opt):
    # Create destination folder if missing
    dest = pathlib.Path(opt.output).absolute()
    os.makedirs(dest, exist_ok=True)

    # Run alignment process for each pair of (acquisition, simulation)
    acquisition_wildcard = str(pathlib.Path(opt.input_acquisition) / "*.npy")
    simulation_wildcard = str(pathlib.Path(opt.input_simulation) / "*.csv")
    acquisitions = sorted(glob.glob(acquisition_wildcard))
    simulations = sorted(glob.glob(simulation_wildcard))
    outputs = [dest / pathlib.Path(p_sim).name for p_sim in simulations]
    paths = list(zip(acquisitions, simulations, outputs))
    with Pool(15) as p:
        p.map(acquisition_simulation_to_dataset, paths)


if __name__ == "__main__":
    # Arguments parser
    parser = argparse.ArgumentParser(
        description="Create a new dataset using real target and model.",
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
        "-ia",
        "--input_acquisition",
        required=True,
        help="folder containing acquisition data in Numpy format",
    )
    parser.add_argument(
        "-is",
        "--input_simulation",
        required=True,
        help="folder containing simulation data in CSV format",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="destination folder for saved datasets",
    )
    options = parser.parse_args()
    abby.logger.setup_logger("abby", options.quiet, options.debug)
    main(options)
