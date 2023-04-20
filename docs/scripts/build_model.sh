#!/usr/bin/env bash
# This is a demo script to create a new model from ELMO using Abby framework.
#
# You may copy and tweak this script to your needs.
# You should launch this script while piping stdout to a file with ``>> logs``.

# Print and exit if any command fails
set -x -e

TRACES="100"
BOARD="disco_f051r8"
INIT_MODEL="elmo"

# Pass 1 using initial model
./docs/scripts/generate_input.py -n ${TRACES} -o input_01.txt
./docs/scripts/trace_simulation.py -n ${TRACES} -b ${BOARD} --model ${INIT_MODEL} -i input_01.txt -o simulation_01 &
./docs/scripts/trace_acquisition.py -n ${TRACES} -b ${BOARD} -i input_01.txt -o acquisition_01
./docs/scripts/build_dataset.py -is simulation_01 -ia acquisition_01 -o dataset_01
./docs/scripts/train.py -i dataset_01 -o catboost,models/model_01.json

# Pass 2 using previous pass model
./docs/scripts/generate_input.py -n ${TRACES} -o input_02.txt
./docs/scripts/trace_simulation.py -n ${TRACES} -b ${BOARD} --model catboost,models/model_01.json -i input_02.txt -o simulation_02 &
./docs/scripts/trace_acquisition.py -n ${TRACES} -b ${BOARD} -i input_02.txt -o acquisition_02
./docs/scripts/build_dataset.py -is simulation_02 -ia acquisition_02 -o dataset_02
./docs/scripts/train.py -i dataset_02 -o catboost,models/model_02.json

# Pass 3 using previous pass model
./docs/scripts/generate_input.py -n ${TRACES} -o input_03.txt
./docs/scripts/trace_simulation.py -n ${TRACES} -b ${BOARD} --model catboost,models/model_02.json -i input_03.txt -o simulation_03 &
./docs/scripts/trace_acquisition.py -n ${TRACES} -b ${BOARD} -i input_03.txt -o acquisition_03
./docs/scripts/build_dataset.py -is simulation_03 -ia acquisition_03 -o dataset_03
./docs/scripts/train.py -i dataset_03 -o catboost,models/model_03.json
