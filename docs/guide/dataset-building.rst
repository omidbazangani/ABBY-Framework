Training data creation
======================

To create training data, it is required to align execution traces to the
acquired side channel traces. Without alignment, it is impossible to know
which instruction is running and affecting the side channel.

Aligning with an existing model
-------------------------------

Using an existing model, it is possible to use algorithms such as Dynamic Time
Wrapping to align instructions with side channel trace.

.. graphviz::

   digraph dataset_pipeline {
       Emulator [color="blue"];
       Model [color="blue"];
       "Firmware builder" -> Emulator [label="machine code", color="blue"];
       Emulator -> Model [label="execution trace", color="blue"];
       Model -> Alignment [label="instruction-accurate\nside channel trace", color="blue"];
       Alignment -> "Training data" [label="instructions annoted\nwith acquired side channel"];
       "Firmware builder" -> "Real target" [label="machine code"];
       "Real target" -> Acquisition [label="side channel"];
       Acquisition -> Alignment [label="cycle-accurate\nside channel trace"];
   }

The following script generates a set of data using this pipeline.

.. literalinclude:: ../scripts/build_dataset.py
   :language: python
   :linenos:

Aligning with a tracing probe
-----------------------------

Using a tracing probe such as the Segger J-Trace it is possible to know
how many cycles each instruction took.

.. graphviz::

   digraph dataset_pipeline {
       "Tracing probe" [color="blue"];
       Alignment -> "Training data" [label="instructions annoted\nwith acquired side channel"];
       "Firmware builder" -> "Real target" [label="machine code"];
       "Real target" -> Acquisition [label="side channel"];
       "Real target" -> "Tracing probe" [label="debug interface", color="blue"];
       "Tracing probe" -> Alignment [label="number of cycles\nfor each instruction", color="blue"];
       Acquisition -> Alignment [label="cycle-accurate\nside channel trace"];
   }

Tracing setup
^^^^^^^^^^^^^

In this section we describe the setup using a Segger J-Trace, but this should
be similar to other tracing probes.

When connected the probe, please note that the 20-pin 0.1'' JTAG connector does
not carry trace data. On J-Trace, only the 19-pin 0.05'' Samtec FTSH connector
can be used to trace.

You might need
`an adaptor <https://www.segger.com/products/debug-probes/j-link/accessories/adapters/19-pin-cortex-m-adapter/>`_
to adapt the 19-pin 0.05'' to 20-pin 0.1''.
Then you will need to manually solder the tracing data and clock pins.

..  figure:: ../_static/images/trace_19pin_connector.*
    :width: 220
    :alt: Tracing pins on 19-pin 0.05'' Samtec FTSH connector

    Tracing pins on 19-pin 0.05'' Samtec FTSH connector.

On most ST STM32F4, the tracing pins are located on ``GPIOE`` device. You should
double check with your specific target.
