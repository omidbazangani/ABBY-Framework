Traces simulation
=================

To simulate a side channel trace, we need to emulate the firmware execution
then predict the trace using it as input data to the inference model.

Sample simulation script
------------------------

The following script simulates traces for each block cipher.

.. literalinclude:: ../scripts/trace_simulation.py
   :language: python
   :linenos:
