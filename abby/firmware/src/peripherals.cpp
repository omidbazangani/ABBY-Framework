#include "peripherals.h"
#ifdef ARDUINO
// Arduino framework
#include <Arduino.h>
#include <elmoasmfunctions.h>
#elif STM32F0 || STM32F1
// LibOpenCM3 framework
#include <elmoasmfunctions.h>
#include <libopencm3/stm32/gpio.h>
#include <libopencm3/stm32/rcc.h>
#include <libopencm3/stm32/usart.h>
#else
// Native
#include <stdio.h>
#include <stdlib.h>
#endif

/**
 * Init board peripherals
 */
void init_peripherals(void) {
#ifdef ARDUINO
  // Clock is set via PlatformIO f_cpu

  // Trigger on pin 8
  pinMode(8, OUTPUT);

  // Serial port
  Serial.begin(USART_BAUDRATE);
#elif STM32F0
#ifndef QEMU
  // HSE clock at 8MHz
  rcc_osc_on(RCC_HSE);
  rcc_wait_for_osc_ready(RCC_HSE);
  rcc_set_sysclk_source(RCC_HSE);

  rcc_set_hpre(RCC_CFGR_HPRE_NODIV);
  rcc_set_ppre(RCC_CFGR_PPRE_NODIV);

  rcc_apb1_frequency = 8000000;
  rcc_ahb_frequency = 8000000;

  // Activate peripherals
  rcc_periph_clock_enable(RCC_GPIOA);
  rcc_periph_clock_enable(RCC_USART1);
#endif

  // Trigger on PA8
  gpio_mode_setup(GPIOA, GPIO_MODE_OUTPUT, GPIO_PUPD_NONE, GPIO8);

  // Serial port on PA9/PA10
  gpio_mode_setup(GPIOA, GPIO_MODE_AF, GPIO_PUPD_NONE, GPIO9 | GPIO10);
  gpio_set_af(GPIOA, GPIO_AF1, GPIO9 | GPIO10);

  // Setup serial port
  usart_set_baudrate(USART1, USART_BAUDRATE);
  usart_set_databits(USART1, USART_DATABITS);
  usart_set_stopbits(USART1, USART_STOPBITS_1);
  usart_set_mode(USART1, USART_MODE_TX_RX);
  usart_set_parity(USART1, USART_PARITY_NONE);
  usart_set_flow_control(USART1, USART_FLOWCONTROL_NONE);
  usart_enable(USART1);
#elif STM32F1
#ifndef QEMU
  // HSE clock at 8MHz
  rcc_osc_on(RCC_HSE);
  rcc_wait_for_osc_ready(RCC_HSE);
  rcc_set_sysclk_source(RCC_HSE);

  rcc_set_hpre(0);
  rcc_set_ppre1(RCC_CFGR_PPRE1_HCLK_NODIV);
  rcc_set_ppre2(RCC_CFGR_PPRE2_HCLK_NODIV);

  rcc_apb1_frequency = 8000000;
  rcc_ahb_frequency = 8000000;

  // Activate peripherals
  rcc_periph_clock_enable(RCC_GPIOA);
  rcc_periph_clock_enable(RCC_USART1);
#endif

  // Trigger on PA8
  gpio_set_mode(GPIOA, GPIO_MODE_OUTPUT_50_MHZ, GPIO_CNF_OUTPUT_PUSHPULL, GPIO8);

  // Serial port on PA9/PA10
  gpio_set_mode(GPIOA, GPIO_MODE_OUTPUT_50_MHZ, GPIO_CNF_OUTPUT_ALTFN_PUSHPULL, GPIO9);
  gpio_set_mode(GPIOA, GPIO_MODE_INPUT, GPIO_CNF_INPUT_FLOAT, GPIO10);

  // Setup serial port
  usart_set_baudrate(USART1, USART_BAUDRATE);
  usart_set_databits(USART1, USART_DATABITS);
  usart_set_stopbits(USART1, USART_STOPBITS_1);
  usart_set_mode(USART1, USART_MODE_TX_RX);
  usart_set_parity(USART1, USART_PARITY_NONE);
  usart_set_flow_control(USART1, USART_FLOWCONTROL_NONE);
  usart_enable(USART1);
#endif
}

/**
 * When program ends, tell ELMO
 */
void program_end(void) {
#if ELMO
  endprogram();
#endif
}

/**
 * Receive text
 */
void receive_text(unsigned char *text, unsigned int n) {
#if !defined(ELMO) && !defined(ARDUINO) && !defined(STM32F0) && !defined(STM32F1)
  int input = 0;
#endif
  for (uint8_t i = 0; i < n; i++) {
#ifdef ELMO
    randbyte(&text[i]);
#elif ARDUINO
    text[i] = Serial.read();
#elif STM32F0 || STM32F1
    text[i] = usart_recv_blocking(USART1);
#else
    input = getchar();
    if (input < 0) {
      exit(0); // exit because of EOF
    }
    text[i] = input;
#endif
  }
}

/**
 * Send text
 */
void send_text(unsigned char *text, unsigned int n) {
  for (uint8_t i = 0; i < n; i++) {
#ifdef ELMO
    printbyte(&text[i]);
#elif ARDUINO
    Serial.write(text[i]);
#elif STM32F0 || STM32F1
    usart_send_blocking(USART1, text[i]);
#else
    putchar(text[i]);
    fflush(stdout);
#endif
  }
}

/**
 * Set trigger
 */
void set_trigger(void) {
#if ELMO
  starttrigger();
#endif

  // We do not want gpio_set when running with ELMO
  // because it is overlapping with other memory
#ifndef ELMO
#if ARDUINO
  digitalWrite(8, HIGH);
#elif STM32F0 || STM32F1
  gpio_set(GPIOA, GPIO8);
#endif
#endif
}

/**
 * Clear trigger
 */
void clear_trigger(void) {
#if ARDUINO && !defined(ELMO)
  digitalWrite(8, LOW);
#elif (STM32F0 || STM32F1) && !defined(ELMO)
  gpio_clear(GPIOA, GPIO8);
#endif

#if ELMO
  endtrigger();
#endif
}
