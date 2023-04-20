Quick start
===========

You will find in Abby repository some scripts to quickly start using it if your
setup is already ready and supported.
This quick start guide will take the example of building then evaluating a power
model for a ST STM32F0 Discovery target using ELMO for initial alignment.

..  contents:: Table of Contents
    :depth: 3

Building model
--------------

All these steps are executed directly at the root of ``python-abby`` repository.
You may adapt the path to the script or copy the script.

Step 1: Generate input data
~~~~~~~~~~~~~~~~~~~~~~~~~~~

We need to generate some random input data. When training with random generated
code this is also use for the random number generator seed to make sure
simulation and acquisition capture the same code.

To generate 100 input data and save it to ``input.txt``, you may call:

..  code-block:: bash

    ./docs/scripts/generate_input.py -n 100 -o input.txt

Step 2: Simulate power traces
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using the input data generated at previous step, we can use ELMO leakage
simulation to generate corresponding power traces with the code execution trace.

The resulting data is saved as CSV (spreadsheet) files in ``simulation`` folder.

..  code-block:: bash

    ./docs/scripts/trace_simulation.py -n 100 -b disco_f051r8 --model elmo -i input.txt -o simulation

If you are curious about what instructions are present, you can generate some
figures with:

..  code-block:: bash

    ./docs/scripts/plot_instructions.py -i simulation/*.csv

Step 3: Acquire power traces
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using the same input data, we may also acquire some real traces from the target.

The resulting data is saved as Numpy data files in ``acquisition`` folder.

..  code-block:: bash

    ./docs/scripts/trace_acquisition.py -n 100 -b disco_f051r8 -i input.txt -o acquisition

Step 4: Building training data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now we would like to match the acquired power samples with the simulation.
This is equivalent to annotating the power trace with the processor pipeline
state at each point in time.

Using data from ``simulation`` and ``acquisition`` folder, we generate CSV
files in ``dataset`` folder.

..  code-block:: bash

    ./docs/scripts/build_dataset.py -is simulation -ia acquisition -o dataset

Step 5: Training new model
~~~~~~~~~~~~~~~~~~~~~~~~~~

Now you could eject from this framework and use your own tools to fit a model
on these training data, or you might use our built-in script to fit a boosted
trees model:

..  code-block:: bash

    ./docs/scripts/train.py -i dataset -o catboost,new_models.json

*Voilà! You have just built a new model for your target.*

You may now use the model to generate power traces:

..  code-block:: bash

    ./docs/scripts/trace_simulation.py -b disco_f051r8 --model catboost,new_models.json -o demo

Bash script
~~~~~~~~~~~

You might want to automate this process. We provide this script as an example
to realise 3 passes of training.

..  literalinclude:: scripts/build_model.sh
    :language: bash
    :linenos:

TVLA Evaluation
---------------

Bash script
~~~~~~~~~~~

..  literalinclude:: scripts/evaluate_tvla.sh
    :language: bash
    :linenos:
