/*
 * Custom ecrypt layer
 */

#include "ecrypt-sync.h"
#include "byte_mask_aes.h"
#include <string.h>

void ECRYPT_keysetup(ECRYPT_ctx *ctx __attribute__((unused)), const u8 *key,
                     u32 keysize __attribute__((unused)),
                     u32 ivsize __attribute__((unused))) {
  KeyExpansion(key);
}

void ECRYPT_ivsetup(ECRYPT_ctx *ctx __attribute__((unused)), const u8 *iv) {
  // Use IV input to set mask
  // Mask should be random, but as we want the same instructions on real
  // target and simulation, we need to provide it
  set_mask(iv);
  init_masking();
}

void ECRYPT_encrypt_bytes(ECRYPT_ctx *ctx __attribute__((unused)),
                          const u8 *plaintext, u8 *ciphertext,
                          u32 msglen __attribute__((unused))) {
  memcpy(ciphertext, plaintext, 16);
  maskstate(ciphertext);
  aes128(ciphertext);
}
