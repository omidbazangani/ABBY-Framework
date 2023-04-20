# Copyright (C) 2020-2021 
# SPDX-License-Identifier: Apache-2.0

"""Test abby.firmware
"""

import subprocess

import pytest

from abby.firmware import environments, get_blockcipher, pio_run
from abby.firmware.blockcipher import blockciphers


@pytest.mark.parametrize("env", environments)
@pytest.mark.parametrize("algorithm", blockciphers)
def test_pio_run(env, algorithm):
    """Test that PlatformIO can compile all algorithms for all boards."""
    if env == "native" and algorithm.name == "generated-code":
        return  # skip as generated-code does only support ARM Thumb
    pio_run(env, algorithm)


def test_byte_masked_aes():
    """Test byte-masked-aes.

    Example of test creation::
        >>> from Crypto.Cipher import AES
        >>> key = b"f\xe9K\xd4\xef\x8a,;\x88L\xfaY\xca4+."
        >>> cipher = AES.new(key, AES.MODE_ECB)
        >>> msg = b"K6\xbd\xc8\x1d\x8b\xd2\xbc\xedKdh\x05\xa7\x08\xb4"
        >>> b"\xAE" + cipher.encrypt(msg)
        b'\xae\x8d\xb0\x1e\xa0\rNdyv\x06\xa6\x96\xcd\xf4 \xf0'
    """
    # Compile native program
    algorithm = get_blockcipher("byte-masked-aes")
    fw_path = pio_run("native", algorithm)

    # Run native program and kill after 1s
    key = b"f\xe9K\xd4\xef\x8a,;\x88L\xfaY\xca4+."
    mask = b"\xabK6\xbd\xc8\x1d\x8b\xd2\xbc\xed"
    msg = b"K6\xbd\xc8\x1d\x8b\xd2\xbc\xedKdh\x05\xa7\x08\xb4"
    input_text = b"\xAE" + key + mask + msg

    # Check size input_text
    assert algorithm.get_input_length() == len(input_text) - 1

    # Check that algorithm can run
    p = subprocess.Popen([fw_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        output, _ = p.communicate(input_text, timeout=1)
    except subprocess.TimeoutExpired:
        p.kill()
        output, _ = p.communicate()

    # Check output
    assert output == b"\xae\x8d\xb0\x1e\xa0\rNdyv\x06\xa6\x96\xcd\xf4 \xf0"


def test_byte_masked_aes_sbox_output():
    """Test byte-masked-aes sbox output code."""
    algorithm = get_blockcipher("byte-masked-aes")

    key = b"f\xe9K\xd4\xef\x8a,;\x88L\xfaY\xca4+."
    mask = b"\xabK6\xbd\xc8\x1d\x8b\xd2\xbc\xed"
    msg = b"K6\xbd\xc8\x1d\x8b\xd2\xbc\xedKdh\x05\xa7\x08\xb4"
    sbox_out = algorithm.get_sbox_output(key, mask, msg)

    assert bytes(sbox_out) == b"NQ\xe3l\x1f\xb3\x1a\xe7\xdb\n\xaa7\x1c\x13\x87H"
