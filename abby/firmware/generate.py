#!/usr/bin/env python3
# Copyright (C) 2020-2021 Radboud University
# SPDX-License-Identifier: Apache-2.0

# This script can be run independently from Abby.

"""
Generate random code for training data acquisition.

To manually generate the code and check which instructions are generated,
you may use:

..  code-block:: bash

    cd abby/firmware
    export PATH=$HOME/.platformio/packages/toolchain-gccarmnoneeabi/bin/:$PATH
    ./generate.py
    arm-none-eabi-gcc -c -g lib/generated-code/generated.S '-DGENERATED_PATH="generated_code.S"' -o /tmp/tmp.o -mcpu=cortex-m0
    arm-none-eabi-objdump -Sd /tmp/tmp.o | less

Target support
~~~~~~~~~~~~~~

For now this script only targets ARM Cortex-M0 assembler.

API
~~~
"""

import random
from pathlib import Path


def rand_op(instr: str, op1_range=(256,), op2_range=(256,), op3_range=(256,)):
    """Format assembly instruction operands using random value.

    :param instr: instruction to format, containing ``{op1}``, ``{op2}`` and
        ``{op3}``.
    :type instr: str
    :param op1_range: range of op1, defaults to (256,)
    :type op1_range: tuple, optional
    :param op2_range: range of op2, defaults to (256,)
    :type op2_range: tuple, optional
    :param op3_range: range of op3, defaults to (256,)
    :type op3_range: tuple, optional
    :return: function returning assembly instruction with random operands
    :rtype: callable returning a str
    """
    return lambda: instr.format(
        op1=random.randrange(*op1_range),
        op2=random.randrange(*op2_range),
        op3=random.randrange(*op3_range),
    )


# Weight each code possibility
# r0-r9 are register variables. r10-r15 are special registers.
# r0-r7 are low register, r8-r15 are high
# r0 is reserved to contain the address of our data section
possibilities = [
    # b*, ldmia, stmia, pop, push
    # sub is only on PC
    rand_op("adcs r{op1}, r{op2}", [1, 8], [1, 8]),
    rand_op("add r{op1}, r{op1}, r{op2}", [1, 8], [1, 8]),
    rand_op("adds r{op1}, r{op1}, #{op2}", [1, 8], [256]),
    rand_op("adds r{op1}, r{op2}, #{op3}", [1, 8], [1, 8], [1, 8]),
    rand_op("adds r{op1}, r{op2}, r{op3}", [1, 8], [1, 8], [1, 8]),
    rand_op("ands r{op1}, r{op2}", [1, 8], [1, 8]),
    rand_op("asrs r{op1}, r{op2}, #{op3}", [1, 8], [1, 8], [1, 33]),
    rand_op("asrs r{op1}, r{op2}", [1, 8], [1, 8]),
    rand_op("bics r{op1}, r{op2}", [1, 8], [1, 8]),
    rand_op("cmn r{op1}, r{op2}", [1, 8], [1, 8]),
    rand_op("cmp r{op1}, #{op2}", [1, 8], [256]),
    rand_op("cmp r{op1}, r{op2}", [1, 8], [1, 8]),  # was 10, 10
    rand_op("cpy r{op1}, r{op2}", [1, 8], [1, 8]),  # was 10, 10
    rand_op("eors r{op1}, r{op2}", [1, 8], [1, 8]),
    rand_op("ldr r{op1}, [r0]", [1, 8]),
    rand_op("ldrb r{op1}, [r0]", [1, 8]),
    rand_op("ldrh r{op1}, [r0]", [1, 8]),
    rand_op("lsls r{op1}, r{op2}, #{op3}", [1, 8], [1, 8], [32]),
    rand_op("lsls r{op1}, r{op2}", [1, 8], [1, 8]),
    rand_op("lsrs r{op1}, r{op2}, #{op3}", [1, 8], [1, 8], [1, 33]),
    rand_op("lsrs r{op1}, r{op2}", [1, 8], [1, 8]),
    rand_op("mov r{op1}, r{op2}", [1, 8], [1, 8]),  # was 10, 10
    rand_op("movs r{op1}, #{op2}", [1, 8], [256]),
    rand_op("movs r{op1}, r{op2}", [1, 8], [1, 8]),  # was 10, 10
    rand_op("muls r{op1}, r{op2}", [1, 8], [1, 8]),
    rand_op("mvns r{op1}, r{op2}", [1, 8], [1, 8]),
    rand_op("negs r{op1}, r{op2}", [1, 8], [1, 8]),
    rand_op("orrs r{op1}, r{op2}", [1, 8], [1, 8]),
    rand_op("rev r{op1}, r{op2}", [1, 8], [1, 8]),
    rand_op("rev16 r{op1}, r{op2}", [1, 8], [1, 8]),
    rand_op("revsh r{op1}, r{op2}", [1, 8], [1, 8]),
    rand_op("rors r{op1}, r{op2}", [1, 8], [1, 8]),
    rand_op("sbcs r{op1}, r{op2}", [1, 8], [1, 8]),
    rand_op("str r{op1}, [r0]", [1, 8]),
    rand_op("strb r{op1}, [r0]", [1, 8]),
    rand_op("strh r{op1}, [r0]", [1, 8]),
    rand_op("subs r{op1}, #{op2}", [1, 8], [256]),
    rand_op("subs r{op1}, r{op2}, #{op3}", [1, 8], [1, 8], [8]),
    rand_op("subs r{op1}, r{op2}, r{op3}", [1, 8], [1, 8], [1, 8]),
    rand_op("sxtb r{op1}, r{op2}", [1, 8], [1, 8]),
    rand_op("sxth r{op1}, r{op2}", [1, 8], [1, 8]),
    rand_op("tst r{op1}, r{op2}", [1, 8], [1, 8]),
    rand_op("uxtb r{op1}, r{op2}", [1, 8], [1, 8]),
    rand_op("uxth r{op1}, r{op2}", [1, 8], [1, 8]),
]


def generate(stream, seed=None, count=1000):
    """Write generated assembly code to stream.

    :param seed: seed used for random number generator, defaults to system time
    :type seed: int, optional
    :param count: number of instructions generated, defaults to 1000
    :type count: int, optional
    """
    random.seed(seed)
    for _ in range(count):
        r = random.choice(possibilities)()
        stream.write(f"    {r}\n")


if __name__ == "__main__":
    with open("generated_code.S", "w") as f:
        generate(f)
