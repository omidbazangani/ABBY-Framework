/*
 * Custom ecrypt layer
 */

#include "aes.h"
#include "ecrypt-sync.h"
#include <string.h>

void ECRYPT_keysetup(ECRYPT_ctx *ctx, const u8 *key,
                     u32 keysize __attribute__((unused)),
                     u32 ivsize __attribute__((unused))) {
  AES_init_ctx(&ctx->ctx, key);
}

void ECRYPT_ivsetup(ECRYPT_ctx *ctx __attribute__((unused)),
                    const u8 *iv __attribute__((unused))) {
  // nothing
}

void ECRYPT_encrypt_bytes(ECRYPT_ctx *ctx, const u8 *plaintext, u8 *ciphertext,
                          u32 msglen __attribute__((unused))) {
  memcpy(ciphertext, plaintext, 16);

  // TinyAES works in place, so copy value
  AES_ECB_encrypt(&ctx->ctx, ciphertext);
}
