#include <stdbool.h>
#include <flexpret.h>

bool should_print = true;
bool int_service_active = true;

static fp_thread_t tid;

void handler(void) {
    for (int i = 0; i < 1000; i++);
}

void *interrupter_thread(void *args) {
    fp_interrupt_enable();
    register_isr(EXC_CAUSE_INTERRUPT_EXPIRE, handler);
    
    while (int_service_active) {
        fp_int_on_expire(100000, cleanup);
        fp_delay_for(100000);
cleanup:
    }

    fp_print_string("Interrupt service done\n");
}

void setup_interrupts(void) {
    // If switch 1 is set, we run the interrupt service
    if (gpi_read_1() == 0b1) {
        fp_print_string("Start int service\n");
        fp_thread_create(HRTT, &tid, interrupter_thread, NULL);
    } else {
        fp_interrupt_disable();
    }
}

void disable_interrupts(void) {
    if (gpi_read_1() == 0b1) {
        fp_interrupt_disable();
        fp_thread_join(tid, NULL);
    }
}
