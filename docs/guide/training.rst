Models training
===============

We suppose that you have a set of data such as a CSV file with features and
target (power consumption or other side channel).

Sample training script
----------------------

Abby includes modules to help loading and creating models.
If you do not like it, you can always eject from the framework and train from
the CSV file.

The following script trains models on specified set of data.

.. literalinclude:: ../scripts/train.py
   :language: python
   :linenos:
