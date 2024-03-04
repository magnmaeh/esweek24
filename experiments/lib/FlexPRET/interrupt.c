#include <stdbool.h>
#include <string.h>

#include <flexpret.h>


volatile bool int_service_active = true;

static fp_thread_t tid[2];

uint32_t periodic_timestamps[100];
uint32_t sporadic_timestamps[100];
uint32_t periodic_timestamps_idx = 0;
uint32_t sporadic_timestamps_idx = 0;

void handler(void) {
    uint32_t hartid = read_hartid();
    if (hartid == 1) {
        // Periodic
        fp_delay_for(100000);
        if (periodic_timestamps_idx < 100) {
            periodic_timestamps[periodic_timestamps_idx++] = rdtime();
        }
    } else if (hartid == 2) {
        // Sporadic
        fp_delay_for(1000000);
        if (sporadic_timestamps_idx < 100) {
            sporadic_timestamps[sporadic_timestamps_idx++] = rdtime();
        }
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

void setup_interrupts(void) {
    memset(periodic_timestamps, 0, sizeof(periodic_timestamps));
    memset(sporadic_timestamps, 0, sizeof(sporadic_timestamps));

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
