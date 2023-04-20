#!/usr/bin/env bash
# This is a demo script to evaluate a model using TVLA.
#
# You may copy and tweak this script to your needs.
# You should launch this script while piping stdout to a file with ``>> logs``.
#
# See section 5.1 "General Test: Fixed-vs.-Random Data Datasets" of
# TVLA-DTR-with-AES.pdf for more background.

# Print and exit if any command fails
set -x -e

# On exit, cleanup
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

# Configuration, you should not use algorithms similar that those you might use
# for training.
ALGORITHMS="byte-masked-aes"
TRACES_PER_ALGORITHM="50000"
TOTAL_TRACES=$(( 2*TRACES_PER_ALGORITHM ))
BOARD="disco_f051r8"
OUR_MODEL="catboost,my_trained_model.json"
KEY="0123456789abcdef123456789abcdef023456789abcdef013456789abcdef012"
MSG="da39a3ee5e6b4b0d3255bfef95601890"

mkdir -p tvla

# Acquire TVLA data
# Input data alternate between random and fixed sets
# Do not crop traces because it can misalign
./docs/scripts/generate_input.py -a ${ALGORITHMS} -n ${TRACES_PER_ALGORITHM} --key ${KEY} --msg ${MSG} --tvla -o tvla/input_tvla.txt
./docs/scripts/trace_simulation.py -a ${ALGORITHMS} -n ${TOTAL_TRACES} -b ${BOARD} --model elmo --only_power --no_crop -i tvla/input_tvla.txt -o tvla/elmo &
./docs/scripts/trace_simulation.py -a ${ALGORITHMS} -n ${TOTAL_TRACES} -b ${BOARD} --model ${OUR_MODEL} --only_power --no_crop -i tvla/input_tvla.txt -o tvla/our_model &
./docs/scripts/trace_acquisition.py -a ${ALGORITHMS} -n ${TOTAL_TRACES} -b ${BOARD} --no_crop --average 1 -i tvla/input_tvla.txt -o tvla/acquisition
wait

# Split sets using files name
mkdir -p tvla/elmo_fixed tvla/our_model_fixed tvla/acquisition_fixed
find "tvla/elmo" -name "*${MSG}.npy" -exec mv {} tvla/elmo_fixed/ \;
find "tvla/our_model" -name "*${MSG}.npy" -exec mv {} tvla/our_model_fixed/ \;
find "tvla/acquisition" -name "*${MSG}.npy" -exec mv {} tvla/acquisition_fixed/ \;

# Plot t-test
./docs/scripts/plot_tvla.py -i1 tvla/acquisition -i2 tvla/acquisition_fixed --xlabel cycle --legend real -o tvla_acquisition.pdf
./docs/scripts/plot_tvla.py -i1 tvla/elmo tvla/our_model -i2 tvla/elmo_fixed tvla/our_model_fixed --xlabel instruction --legend elmo "our model" -o tvla_models.pdf
