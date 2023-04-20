#!/usr/bin/env python3
# Copyright (C) 2020-2021 
# SPDX-License-Identifier: Apache-2.0

"""
Plot instructions statistics.

To see what instructions are being used by a specific algorithm, you may use:

..  code-block:: bash

    ./docs/scripts/trace_simulation.py -b disco_f051r8 -a generated-code  \
        -m elmo -o tmp_dir
    ./docs/scripts/plot_instructions.py -i tmp_dir/*
    rm -rf tmp_dir

To fix showed instructions, for example you can use,

..  code-block:: plain

    --instructions ADC ADD#imm ADDS ANDS ASRS B BCC BCS BEQ BICS BL BNE BX CMP
    CMPS CPY EORS LDR LDRB LDRH LSLS LSLS#imm LSRS LSRS#imm MOV MOVS MULS MVNS
    NEGS ORRS POP PUSH REV SBC STR STRB STRH SUB SUBS UXTB UXTH

"""

import argparse

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from tqdm import tqdm

import abby


def main(opt):
    # Load dataset
    dfs = []
    for path in tqdm(opt.input):
        dfs.append(pd.read_csv(path))
    df = pd.concat(dfs)

    # Remove all NOP
    if "opcode" in df.columns:
        df = df[df.opcode != 0x46C0]

    # Count instructions in stage 2 and plot
    count_stage2 = df.instr_stage2.value_counts().sort_index().reset_index()
    count_stage2 = count_stage2.rename(
        columns={"index": "instruction", "instr_stage2": "count"}
    )
    print(count_stage2)
    sns.set()
    plt.figure(figsize=(6, 8))
    sns.barplot(data=count_stage2, x="count", y="instruction")
    plt.tight_layout()
    plt.savefig(opt.pdf_output)

    # Plot instruction frequency table
    with open(opt.html_output, "w") as f:
        f.write(
            abby.plot.instruction_frequency_table(
                df, x="instr_stage3", y="instr_stage2", instructions=opt.instructions
            )
        )


if __name__ == "__main__":
    # Arguments parser
    parser = argparse.ArgumentParser(
        description="Plot instructions statistics.",
    )
    parser.add_argument(
        "-i",
        "--input",
        nargs="+",
        required=True,
        help="set of data in CSV format",
    )
    parser.add_argument(
        "--instructions",
        nargs="+",
        help="instructions to consider",
    )
    parser.add_argument(
        "--html_output",
        default="instructions_table.html",
        help="path to save HTML frequency table of instructions",
    )
    parser.add_argument(
        "--pdf_output",
        default="instructions.pdf",
        help="path to save PDF bar char of instructions, default to instructions.pdf",
    )
    options = parser.parse_args()
    main(options)
