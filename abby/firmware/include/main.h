#ifndef MAIN_H
#define MAIN_H

#include "peripherals.h"
#include <ecrypt-sync.h>
#include <stdint.h>

// Convert bit length from eCrypt sync to bytes length
#define TEXT_LENGTH (ECRYPT_BLOCKLENGTH / 8)
#define KEY_LENGTH (ECRYPT_MAXKEYSIZE / 8)
#define IV_LENGTH (ECRYPT_MAXIVSIZE / 8)

// WAIT_NOP does 500 NOP
// We do not want to use a function for NOP to keep assembly simple
#define tNOP __asm__("NOP;NOP;NOP;NOP;NOP;NOP;NOP;NOP;NOP;NOP;") // NOLINT
#define hNOP tNOP;tNOP;tNOP;tNOP;tNOP;tNOP;tNOP;tNOP;tNOP;tNOP // NOLINT
#define WAIT_NOP hNOP;hNOP;hNOP;hNOP;hNOP // NOLINT

// A serial message begin with START_BYTE
// This is used to be compatible with Inspector Pinata scripts
#define START_BYTE 0xAE

#endif
