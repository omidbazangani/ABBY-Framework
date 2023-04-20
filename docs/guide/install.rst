Installation
============

Abby is packaged as a Python module.
You need to have a working Python 3 installation with pip module.

Prerequisites for acquisitions
------------------------------

If you want to use Abby to acquire some traces from a real target, you will
need to set up an acquisition setup and install the library associated with
your oscilloscope.

Oscilloscope
^^^^^^^^^^^^

For a PicoScope 3000a serie, you may install the official driver on Debian/Ubuntu with the following:

..  code-block:: bash

    wget -O - https://labs.picotech.com/debian/dists/picoscope/Release.gpg.key | sudo apt-key add -
    sudo apt-add-repository "deb https://labs.picotech.com/debian/ picoscope main"
    sudo apt install libps3000a

STLink v2 permissions
^^^^^^^^^^^^^^^^^^^^^

By default, your user might not be allowed to access the STLink device.
To enable any user from ``plugdev`` group to communicate with STLink v2,
you may add the following udev rule to ``/etc/udev/rules.d/stlinkv2.rules``:

..  code-block:: none

    ATTRS{idVendor}=="0483", ATTRS{idProduct}=="3748", MODE="664", GROUP="plugdev"

Then you can reboot, or try to hot-reload udev rules:

..  code-block:: bash

    udevadm control --reload-rules && udevadm trigger

If you have installed STM32Cube in the past, you might already have an udev rule
that enables every user to access the device. You can keep it like this, or use
the rule above for more security.

Build from sources
------------------

Clone the Git repository and then install the Python module:

..  code-block:: bash

    git clone --recursive https://gitlab.science.ru.nl/abby/python-abby && cd python-abby
    pip install --user -e .

``-e`` option symlinks the module files to allow editing source files during
development process.
``--user`` installs the Python module in you user ``~/.local/`` folder.
