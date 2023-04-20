#include "ecrypt-sync.h"
#include "generated.h"
#include <stdint.h>

void ECRYPT_keysetup(ECRYPT_ctx *ctx __attribute__((unused)),
                    const u8 *key __attribute__((unused)),
                    u32 keysize __attribute__((unused)),
                    u32 ivsize __attribute__((unused))) {
  // nothing
}

void ECRYPT_ivsetup(ECRYPT_ctx *ctx __attribute__((unused)),
                    const u8 *iv __attribute__((unused))) {
  // nothing
}

void ECRYPT_encrypt_bytes(ECRYPT_ctx *ctx __attribute__((unused)),
                        const u8 *plaintext __attribute__((unused)),
                        u8 *ciphertext __attribute__((unused)),
                        u32 msglen __attribute__((unused))) {
  generated_code();
}
