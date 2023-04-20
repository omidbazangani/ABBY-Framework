# Copyright (C) 2020-2021 Radboud University
# SPDX-License-Identifier: Apache-2.0

"""
You may use :data:`abby.firmware.blockcipher.blockciphers` to get the list of
available ciphers.
"""


class BlockCipher:
    """Base class for all block ciphers

    All lengths are in bytes.
    """

    key_length = 0
    iv_length = 0
    mask_length = 0
    msg_length = 0

    # Corresponding PlatformIO environment
    name = ""

    def get_input_length(self):
        """Get total input length

        :return: input length
        :rtype: int
        """
        return self.key_length + self.iv_length + self.mask_length + self.msg_length

    def __str__(self):
        """Return string representation

        :return: name of block cipher
        :rtype: str
        """
        return self.name


class ByteMaskedAES(BlockCipher):
    """Byte-Masked-AES from
    https://github.com/Secure-Embedded-Systems/Masked-AES-Implementation/

    ByteMaskedAES is licensed under GPL3+ by Virginia Tech.

    This is a masked implementation of AES-128bits.
    The computed intermediate values are XOR with a mask to reduce leakage when
    reading or writing to memory.
    """

    key_length = 16
    mask_length = 10
    msg_length = 16
    name = "byte-masked-aes"

    _sbox = (
        b"c|w{\xf2ko\xc50\x01g+\xfe\xd7\xabv\xca\x82\xc9}\xfaYG\xf0\xad"
        b"\xd4\xa2\xaf\x9c\xa4r\xc0\xb7\xfd\x93&6?\xf7\xcc4\xa5\xe5\xf1q"
        b"\xd81\x15\x04\xc7#\xc3\x18\x96\x05\x9a\x07\x12\x80\xe2\xeb'\xb2"
        b"u\t\x83,\x1a\x1bnZ\xa0R;\xd6\xb3)\xe3/\x84S\xd1\x00\xed \xfc"
        b"\xb1[j\xcb\xbe9JLX\xcf\xd0\xef\xaa\xfbCM3\x85E\xf9\x02\x7fP<"
        b"\x9f\xa8Q\xa3@\x8f\x92\x9d8\xf5\xbc\xb6\xda!\x10\xff\xf3\xd2"
        b'\xcd\x0c\x13\xec_\x97D\x17\xc4\xa7~=d]\x19s`\x81O\xdc"*\x90'
        b"\x88F\xee\xb8\x14\xde^\x0b\xdb\xe02:\nI\x06$\\\xc2\xd3\xacb\x91"
        b"\x95\xe4y\xe7\xc87m\x8d\xd5N\xa9lV\xf4\xeaez\xae\x08\xbax%.\x1c"
        b"\xa6\xb4\xc6\xe8\xddt\x1fK\xbd\x8b\x8ap>\xb5fH\x03\xf6\x0ea5W"
        b"\xb9\x86\xc1\x1d\x9e\xe1\xf8\x98\x11i\xd9\x8e\x94\x9b\x1e\x87"
        b"\xe9\xceU(\xdf\x8c\xa1\x89\r\xbf\xe6BhA\x99-\x0f\xb0T\xbb\x16"
    )
    _mul2 = (
        b"\x00\x02\x04\x06\x08\n\x0c\x0e\x10\x12\x14\x16\x18\x1a\x1c\x1e"
        b' "$&(*,.02468:<>@BDFHJLNPRTVXZ\\^`bdfhjlnprtvxz|~\x80\x82\x84'
        b"\x86\x88\x8a\x8c\x8e\x90\x92\x94\x96\x98\x9a\x9c\x9e\xa0\xa2"
        b"\xa4\xa6\xa8\xaa\xac\xae\xb0\xb2\xb4\xb6\xb8\xba\xbc\xbe\xc0"
        b"\xc2\xc4\xc6\xc8\xca\xcc\xce\xd0\xd2\xd4\xd6\xd8\xda\xdc\xde"
        b"\xe0\xe2\xe4\xe6\xe8\xea\xec\xee\xf0\xf2\xf4\xf6\xf8\xfa\xfc"
        b"\xfe\x1b\x19\x1f\x1d\x13\x11\x17\x15\x0b\t\x0f\r\x03\x01\x07"
        b"\x05;9?=3175+)/-#!'%[Y_]SQWUKIOMCAGE{y\x7f}sqwukiomcage\x9b"
        b"\x99\x9f\x9d\x93\x91\x97\x95\x8b\x89\x8f\x8d\x83\x81\x87\x85"
        b"\xbb\xb9\xbf\xbd\xb3\xb1\xb7\xb5\xab\xa9\xaf\xad\xa3\xa1\xa7"
        b"\xa5\xdb\xd9\xdf\xdd\xd3\xd1\xd7\xd5\xcb\xc9\xcf\xcd\xc3\xc1"
        b"\xc7\xc5\xfb\xf9\xff\xfd\xf3\xf1\xf7\xf5\xeb\xe9\xef\xed\xe3"
        b"\xe1\xe7\xe5"
    )
    _mul3 = (
        b"\x00\x03\x06\x05\x0c\x0f\n\t\x18\x1b\x1e\x1d\x14\x17\x12\x1103"
        b"65<?:9(+.-$'\"!`cfelojix{~}twrqPSVU\\_ZYHKNMDGBA\xc0\xc3\xc6"
        b"\xc5\xcc\xcf\xca\xc9\xd8\xdb\xde\xdd\xd4\xd7\xd2\xd1\xf0\xf3"
        b"\xf6\xf5\xfc\xff\xfa\xf9\xe8\xeb\xee\xed\xe4\xe7\xe2\xe1\xa0"
        b"\xa3\xa6\xa5\xac\xaf\xaa\xa9\xb8\xbb\xbe\xbd\xb4\xb7\xb2\xb1"
        b"\x90\x93\x96\x95\x9c\x9f\x9a\x99\x88\x8b\x8e\x8d\x84\x87\x82"
        b"\x81\x9b\x98\x9d\x9e\x97\x94\x91\x92\x83\x80\x85\x86\x8f\x8c"
        b"\x89\x8a\xab\xa8\xad\xae\xa7\xa4\xa1\xa2\xb3\xb0\xb5\xb6\xbf"
        b"\xbc\xb9\xba\xfb\xf8\xfd\xfe\xf7\xf4\xf1\xf2\xe3\xe0\xe5\xe6"
        b"\xef\xec\xe9\xea\xcb\xc8\xcd\xce\xc7\xc4\xc1\xc2\xd3\xd0\xd5"
        b"\xd6\xdf\xdc\xd9\xda[X]^WTQRC@EFOLIJkhmngdabspuv\x7f|yz;8=>7"
        b"412# %&/,)*\x0b\x08\r\x0e\x07\x04\x01\x02\x13\x10\x15\x16\x1f"
        b"\x1c\x19\x1a"
    )

    def _remask(self, s, m1, m2, m3, m4, m5=0, m6=0, m7=0, m8=0):
        """Remask extracted from the firmware"""
        masks = [(m1 ^ m5), (m2 ^ m6), (m3 ^ m7), (m4 ^ m8)]
        for i in range(4):
            s[0 + i * 4] = s[0 + i * 4] ^ masks[0]
            s[1 + i * 4] = s[1 + i * 4] ^ masks[1]
            s[2 + i * 4] = s[2 + i * 4] ^ masks[2]
            s[3 + i * 4] = s[3 + i * 4] ^ masks[3]
        return s

    def get_sbox_output(self, key: bytes, mask: bytes, msg: bytes):
        """Get first round Sbox output.

        :param key: key
        :type key: bytes
        :param mask: mask
        :type mask: bytes
        :param msg: cleartext
        :type msg: bytes
        :return: first sbox output
        :rtype: bytes
        """
        # Set_mask
        mask, wordmask = list(mask[:6]), mask[6:10]

        # Init_masking
        mask += [
            self._mul2[mask[0]] ^ self._mul3[mask[1]] ^ mask[2] ^ mask[3],
            mask[0] ^ self._mul2[mask[1]] ^ self._mul3[mask[2]] ^ mask[3],
            mask[0] ^ mask[1] ^ self._mul2[mask[2]] ^ self._mul3[mask[3]],
            self._mul3[mask[0]] ^ mask[1] ^ mask[2] ^ self._mul2[mask[3]],
        ]

        # Mask sbox
        sbox_masked = [0] * 256
        for cnt in range(256):
            sbox_masked[cnt ^ mask[4]] = self._sbox[cnt] ^ mask[5]

        # Mask roundkey
        roundkey_masked = self._remask(
            list(key),
            mask[6],
            mask[7],
            mask[8],
            mask[9],
            mask[4] ^ wordmask[0],
            mask[4] ^ wordmask[1],
            mask[4] ^ wordmask[2],
            mask[4] ^ wordmask[3],
        )

        # Calculate state
        state = list(msg)
        state = self._remask(state, mask[6], mask[7], mask[8], mask[9])
        for i in range(16):
            state[i] ^= roundkey_masked[i]
            state[i] = sbox_masked[state[i] ^ wordmask[i % 4]] ^ wordmask[i % 4]
        return state


class ChaCha8(BlockCipher):
    """Chacha8 from https://cr.yp.to/chacha.html

    Chacha8 is licensed under Public domain by D. J. Bernstein.

    ChaCha is a modification of Salsa20.
    The round function uses modular Additions, Rotations and XOR (ARX block
    cipher).
    """

    key_length = 32
    iv_length = 8
    msg_length = 8
    name = "chacha8"


class ChaCha20(BlockCipher):
    """Chacha20 from https://cr.yp.to/chacha.html

    Chacha20 is licensed under Public domain by D. J. Bernstein.

    ChaCha is a modification of Salsa20.
    The round function uses modular Additions, Rotations and XOR (ARX block
    cipher).
    """

    key_length = 32
    iv_length = 8
    msg_length = 8
    name = "chacha20"


class GeneratedCode(BlockCipher):
    """Generate random assembly code.

    See :func:`abby.firmware.generate.generate`.
    """

    msg_length = 16
    name = "generated-code"

    # Random number generator seed, default to system time
    # Trace_simulation and acquisition need to use same seed
    seed = None

    # Number of instructions generated
    count = 1000


class Rabbit(BlockCipher):
    """Rabbit from https://bench.cr.yp.to/supercop.html

    Rabbit is licensed for non commercial use by Cryptico A/S.
    """

    key_length = 16
    iv_length = 8
    msg_length = 2
    name = "rabbit"


class Salsa20(BlockCipher):
    """Salsa20 from https://bench.cr.yp.to/supercop.html

    Salsa20 is licensed under Public domain by D. J. Bernstein.

    The round function uses modular Additions, Rotations and XOR (ARX block
    cipher).
    """

    key_length = 32
    iv_length = 8
    msg_length = 8
    name = "salsa20"


class Sosemanuk(BlockCipher):
    """Sosemanuk from https://bench.cr.yp.to/supercop.html

    Sosemanuk was written by X-CRYPT project.
    """

    key_length = 32
    iv_length = 16
    msg_length = 10
    name = "sosemanuk"


class TinyAES(BlockCipher):
    """TinyAES from https://github.com/kokke/tiny-AES-c/

    TinyAES is licensed under The Unlicense.

    This is an unprotected implementation of AES-128bits.
    """

    key_length = 16
    msg_length = 16
    name = "tinyaes"


class Xoodoo(BlockCipher):
    """Xoodoo from https://github.com/0xADE1A1DE/Rosita/tree/master/TESTS/xoodoo/

    This version of Xoodoo is licensed under Apache 2.0 by ROSITA authors.

    This is a masked implementation of Xoodoo primitives.
    The computed intermediate values are XOR with a mask to reduce leakage when
    reading or writing to memory.
    """

    key_length = 16
    mask_length = 48
    msg_length = 16
    name = "xoodoo"


blockciphers = [
    ByteMaskedAES(),
    ChaCha8(),
    ChaCha20(),
    Rabbit(),
    Salsa20(),
    Sosemanuk(),
    TinyAES(),
    Xoodoo(),
    GeneratedCode(),
]
