/**
 * Peripherals manage triggers and text input/output with outside world.
 * When compiling with ELMO flag, we use ELMO library to trigger and and send
 * and receive text. When compiling for a board, we use GPIO and UART from
 * corresponding framework.
 */

#ifndef PERIPHERALS_H
#define PERIPHERALS_H

#include <stdint.h>

#define USART_BAUDRATE 115200
#define USART_DATABITS 8

// peripherals.cpp uses C++ for Arduino framework
#ifdef __cplusplus
extern "C" {
#endif

void init_peripherals(void);
void program_end(void);
void receive_text(unsigned char *text, unsigned int n);
void send_text(unsigned char *text, unsigned int n);
void set_trigger(void);
void clear_trigger(void);

#ifdef __cplusplus
}
#endif

#endif
