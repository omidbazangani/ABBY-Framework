/*
 * Custom ecrypt layer
 */

#include "ecrypt-sync.h"
#include "xoodoo.h"

/*
 * 4 byte align arrays to make sure we don't load invalid data
 * for state of byte-wise operations (ARM loads/stores 4 bytes
 * from addr & ~(0b11) when load/storing from address addr).
 * In ARM, Addresses that are not divisable by 4 are invalid when used
 * with wordwise instructions (ldr, str)
 */
volatile uint8_t XoodooState[48] __attribute__((aligned(4)));

extern uint32_t XoodooMask[12];

void Absorb_Block(uint32_t *state, uint32_t *block);

void ECRYPT_keysetup(ECRYPT_ctx *ctx __attribute__((unused)),
                     const u8 *key __attribute__((unused)),
                     u32 keysize __attribute__((unused)),
                     u32 ivsize __attribute__((unused))) {
  // Init state with fixed random key
  // FIXME: we should use provided key
  XoodooState[0] = 0xfa;
  XoodooState[1] = 0x6f;
  XoodooState[2] = 0x44;
  XoodooState[3] = 0x1a;
  XoodooState[4] = 0x3f;
  XoodooState[5] = 0xeb;
  XoodooState[6] = 0x90;
  XoodooState[7] = 0xa0;
  XoodooState[8] = 0xad;
  XoodooState[9] = 0x72;
  XoodooState[10] = 0xb9;
  XoodooState[11] = 0x6f;
  XoodooState[12] = 0xf2;
  XoodooState[13] = 0xaa;
  XoodooState[14] = 0x1f;
  XoodooState[15] = 0xbe;
  XoodooState[16] = 0xd7;
  XoodooState[17] = 0x24;
  XoodooState[18] = 0xce;
  XoodooState[19] = 0x97;
  XoodooState[20] = 0x3c;
  XoodooState[21] = 0x28;
  XoodooState[22] = 0xb4;
  XoodooState[23] = 0x93;
  XoodooState[24] = 0x03;
  XoodooState[25] = 0x02;
  XoodooState[26] = 0x5d;
  XoodooState[27] = 0x51;
  XoodooState[28] = 0x4c;
  XoodooState[29] = 0xa5;
  XoodooState[30] = 0x8d;
  XoodooState[31] = 0x3e;
  XoodooState[32] = 0x0a;
  XoodooState[33] = 0x02;
  XoodooState[34] = 0xb1;
  XoodooState[35] = 0x66;
  XoodooState[36] = 0x94;
  XoodooState[37] = 0x38;
  XoodooState[38] = 0xcf;
  XoodooState[39] = 0x10;
  XoodooState[40] = 0x52;
  XoodooState[41] = 0xf8;
  XoodooState[42] = 0x68;
  XoodooState[43] = 0x67;
  XoodooState[44] = 0xa2;
  XoodooState[45] = 0xad;
  XoodooState[46] = 0xcf;
  XoodooState[47] = 0x89;
}

void ECRYPT_ivsetup(ECRYPT_ctx *ctx __attribute__((unused)), const u8 *iv) {
  // Use IV input to set mask
  // Mask should be random, but as we want the same instructions on real
  // target and simulation, we need to provide it
  Xoodoo_Initialize_Masks(XoodooMask, iv);
}

void Absorb_Block(uint32_t *state, uint32_t *block) {
  for (int i = 0; i < 4; i++) {
    state[i] ^= block[i];
  }
}

void ECRYPT_encrypt_bytes(ECRYPT_ctx *ctx __attribute__((unused)),
                          const u8 *plaintext, u8 *ciphertext,
                          u32 msglen __attribute__((unused))) {
  Absorb_Block((uint32_t *)XoodooState, (uint32_t *)plaintext);
  Xoodoo_Permute_12rounds((uint32_t *)XoodooState, XoodooMask);
  for (int j = 0; j < ECRYPT_BLOCKLENGTH / 8; j++) {
    ciphertext[j] = XoodooState[j];
  }
}
