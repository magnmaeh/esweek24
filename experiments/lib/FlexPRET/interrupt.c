#include <stdbool.h>
#include <string.h>

#include <flexpret.h>

#ifndef PLATFORM_FLEXPRET
#define PLATFORM_FLEXPRET
#endif 
#include "../common.h"

volatile bool int_service_active = true;

static fp_thread_t tid[2];

uint32_t ninterrupts_periodic = 0;
uint32_t ninterrupts_sporadic = 0;

void handler(void) {
    uint32_t hartid = read_hartid();
    if (hartid == 1) {
        on_periodic_interrupt_common();
    } else if (hartid == 2) {
        on_sporadic_interrupt_common();
    }
}

void *interrupter_thread(void *args) {
    register_isr(EXC_CAUSE_EXTERNAL_INT, handler);
    
    fp_interrupt_enable();
    while (int_service_active);
    fp_interrupt_disable();
}

void send_sync(void) {
    gpo_write_3(0b11);
}

void configure_pins(void) {
    if (fp_thread_create(HRTT, &tid[0], interrupter_thread, NULL) == 0) {
        fp_print_string("Started periodic int service\n");
    } else {
        fp_print_string("Failed to start int service\n");
    }
    if (fp_thread_create(HRTT, &tid[1], interrupter_thread, NULL) == 0) {
        fp_print_string("Started sporadic int service\n");
    } else {
        fp_print_string("Failed to start int service\n");
    }
}

void disable_interrupts(void) {
    fp_interrupt_disable();
    int_service_active = false;
    fp_thread_join(tid[0], NULL);
    fp_thread_join(tid[1], NULL);
}
