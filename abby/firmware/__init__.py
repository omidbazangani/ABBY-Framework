# Copyright (C) 2020-2021 Radboud University
# SPDX-License-Identifier: Apache-2.0

"""
Abby comes with a device-agnostic firmware that can run multiple block ciphers
and can be flashed on a large variety of boards.
This firmware is meant to be used to generate training or evaluation data for
side-channel models.

Building and flashing process
-----------------------------

To simplify build and flashing process, Abby uses
`PlatformIO <https://platformio.org/>`_.
This tool provides a common abstraction over multiples boards.
Depending on targeted board, it will automatically download matching
cross-compilation toolchain and flashing utilities.

Each board is in a separate PlatformIO environment such as ``disco_f051r8``.
The algorithm is given to PlatformIO via ``PLATFORMIO_ALGORITHM`` environment
variable.

To manually use PlatformIO without Abby scripts, you can go to ``abby/firmware``
then launch ``PLATFORMIO_ALGORITHM=tinyaes pio run -t upload -e disco_f051r8``
to flash TinyAES on a ST STM32F051 Discovery.

Target support
--------------

For now this firmware supports only Arduino and LibOpenCM3 frameworks to target
a large variety of boards.

These boards are supported and tested:

* ST Discovery STM32F051 and STM32F030 (``disco_f051r8``)

These boards are implemented but not tested yet:

* Waveshare Core407I or Riscure Piñata, STM32F407IGT6 (``genericSTM32F407IGT6``)
* BBC Micro:bit v1, Nordic nRF51822 (``bbcmicrobit``)

Code padding
------------

After sending some input data, the firmware runs :

* 500 ``NOP`` instructions,
* the selected algorithm,
* 500 ``NOP`` instructions again.

On ARM Cortex-M0, ``NOP`` is equivalent to ``MOV r8, r8``.
Using ``NOP``, we are adding a reference to ease debugging and alignment.
We also make sure that the instructions triggering acquisitions do not effect
acquired data as activating a GPIO may have an effect on the beginning of the
trace.

Flashing and execution
----------------------

These functions enables you to choose a block cipher and build and flash it.
"""

import contextlib
import logging
import os
import pathlib
import sys
import tempfile

import abby.firmware.blockcipher as blockcipher

__all__ = ["blockcipher", "pio_run", "get_blockcipher", "environments"]

# Local logger
log = logging.getLogger(__name__)

# Supported environments, matching platformio.ini
environments = [
    "bbcmicrobit",
    "disco_f051r8",
    "native",
    "disco_f100rb",
]


def pio_run(
    env: str,
    algorithm: blockcipher.BlockCipher,
    upload=False,
    elmo=False,
    qemu=False,
    debug=False,
) -> pathlib.Path:
    """Run one PlatformIO environment and return path to built firmware.

    PlatformIO is written in Python, but lacks an API. A workaround is to
    manually call run Click command with arguments. By doing this we will
    still compatible with different versions.

    Using ``elmo=True`` you can compile a firmware calling ELMO specific code
    and disable some board specific code that interfere with ELMO such as
    ``gpio_set``.

    :param env: name of the PlatformIO environment to run
    :type env: str
    :param algorithm: algorithm to use
    :type algorithm: blockcipher.BlockCipher
    :param upload: uploads firmware to the first board found by PlatformIO,
        defaults to False
    :type upload: bool, optional
    :param elmo: compiles firmware with ``-DELMO`` option, defaults to False
    :type elmo: bool, optional
    :param qemu: compiles firmware with ``-DQEMU`` option, defaults to False
    :type qemu: bool, optional
    :param debug: outputs compilation logs, defaults to False
    :type debug: bool, optional
    :raises ImportError: when PlatformIO is missing
    :return: path to built firmware
    :rtype: pathlib.Path
    """

    # Locate firmware
    project_dir = pathlib.Path(__file__).parent.absolute()
    workspace_dir = tempfile.mkdtemp(prefix="pio")

    # Generate random code if we are building it
    build_flags = ""
    if isinstance(algorithm, blockcipher.GeneratedCode):
        from abby.firmware.generate import generate

        src_file = tempfile.NamedTemporaryFile(
            mode="w+", prefix="generated", suffix=".S"
        )
        log.debug(f"Generating assembly code to {src_file.name}")
        generate(src_file, seed=algorithm.seed, count=algorithm.count)
        build_flags += f"'-DGENERATED_PATH=\"{src_file.name}\"' "

    # Disable some code that breaks the emulator
    if elmo:
        build_flags += "-DELMO"
    if qemu:
        build_flags += "-DQEMU"

    log.info(f"Building {env} with algorithm {algorithm}, elmo version: {elmo}")
    os.environ["PLATFORMIO_BUILD_FLAGS"] = build_flags
    os.environ["PLATFORMIO_ALGORITHM"] = str(algorithm)
    os.environ["PLATFORMIO_WORKSPACE_DIR"] = workspace_dir

    args = ["-e", env, "-d", project_dir]
    if not debug:
        # Make silent unless debug
        args += ["-s"]
    if upload:
        args += ["-t", "upload"]

    # Import PlatformIO
    try:
        from platformio.commands.run.command import cli
    except ImportError as e:
        raise ImportError("You need to install platformio module.") from e

    # Run PlatformIO
    try:
        with contextlib.redirect_stderr(sys.stdout):
            cli(args)  # pylint: disable=no-value-for-parameter
    except SystemExit:
        pass  # Do not let platformio exit script

    if env == "native":
        output_name = "program"
    else:
        output_name = "firmware.bin"

    return pathlib.Path(workspace_dir) / "build" / env / output_name


def get_blockcipher(name: str) -> blockcipher.BlockCipher:
    """Get a block cipher by name

    :param name: name of the block cipher to get
    :type name: str
    :raises ValueError: cipher not found
    :return: block cipher object
    :rtype: blockcipher.BlockCipher
    """
    for cipher in blockcipher.blockciphers:
        if cipher.name == name:
            return cipher
    raise ValueError(f"{name} is not implemented")
