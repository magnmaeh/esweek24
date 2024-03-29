#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/uart.h"

#include <stdarg.h>

#define UART_ID uart0
#define BAUD_RATE 115200
#define DATA_BITS 8
#define STOP_BITS 1
#define PARITY    UART_PARITY_NONE

// We are using pins 0 and 1, but see the GPIO function select table in the
// datasheet for information on which other pins can be used.
#define UART_TX_PIN 0
#define UART_RX_PIN 1

void printf_custom_init(void) {
    // Set up our UART with the required speed.
    uart_init(UART_ID, BAUD_RATE);
    
    // Set the TX and RX pins by using the function select on the GPIO
    // Set datasheet for more information on function select
    gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);
}

void out(char c, void *arg) {
    uart_putc(UART_ID, c);
}

int printf_custom(char *fmt, ...) {
    va_list va;
    va_start(va, fmt);
    int ret = vfctprintf(out, NULL, fmt, va);
    va_end(va);
    return ret;
}
