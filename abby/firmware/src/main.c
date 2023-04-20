#include "main.h"

int main(void) {
  init_peripherals();

  uint8_t start;
  uint8_t cleartext[TEXT_LENGTH] = {0};
  uint8_t ciphertext[TEXT_LENGTH] = {0};
  uint8_t key[KEY_LENGTH];
  uint8_t iv[IV_LENGTH];

  // Create context
  ECRYPT_ctx ctx;

  while (1) {
    // Wait for start byte
    receive_text(&start, 1);
    if (start != START_BYTE) {
      continue;
    }

    // Receive key, iv and cleartext
    receive_text(key, KEY_LENGTH);
    receive_text(iv, IV_LENGTH);
    receive_text(cleartext, TEXT_LENGTH);

    // Init context
    ECRYPT_keysetup(&ctx, key, ECRYPT_MAXKEYSIZE, ECRYPT_MAXIVSIZE);
    ECRYPT_ivsetup(&ctx, iv);

    // Set trigger to start power trace acquisition
    set_trigger();

    // Wait a bit with NOP instructions
    WAIT_NOP;

    // Encrypt
    ECRYPT_encrypt_bytes(&ctx, cleartext, ciphertext, TEXT_LENGTH);

    // Wait a bit with NOP instructions
    WAIT_NOP;

    // Reset trigger
    clear_trigger();

    // Send start byte
    send_text(&start, 1);
    send_text(ciphertext, TEXT_LENGTH);

#ifdef ELMO
    // Do only one trace with ELMO
    break;
#endif
  }

  program_end();

  return 0;
}
