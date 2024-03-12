#include <wiringPi.h>
#include <stdlib.h>

#include "common.h"

#define SYNC_PIN (15)
#define PERIODIC_INT_PIN (16)
#define SPORADIC_INT_PIN (1)

uint32_t ninterrupts_periodic = 0;
uint32_t ninterrupts_sporadic = 0;

void periodic_isr(void) {
    on_periodic_interrupt_common();
}

void sporadic_isr(void) {
    on_sporadic_interrupt_common();
}

void configure_pins(void) {
    wiringPiSetup();

    // Set up interrupts
    wiringPiISR(PERIODIC_INT_PIN, INT_EDGE_RISING, periodic_isr);
    wiringPiISR(SPORADIC_INT_PIN, INT_EDGE_RISING, sporadic_isr);
}

void send_sync(void) {
    // Write trigger to waveform generation
    pinMode(SYNC_PIN, OUTPUT);
    digitalWrite(SYNC_PIN, HIGH);
}

void disable_interrupts(void) {
    system("/usr/bin/gpio edge 16 none");
    system("/usr/bin/gpio edge 1 none");
}
