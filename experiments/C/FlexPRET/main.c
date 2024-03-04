#include <string.h>
#include <stdlib.h>
#include <flexpret.h>

#define USEC(t) (t * 1000LL)
#define PLATFORM_FLEXPRET
#include "../../lib/common.h"
#include "/tmp/config.h"

void setup_interrupts(void);
void disable_interrupts(void);
void send_sync(void);

void main_handler(void) {
    fp_print_string("Test\n");
}

void print_timestamp_with_index(int idx, uint32_t timestamp) {
    char string[128] = "";
    char number[64]  = "";
    
    strcat(string, "[");
    itoa(idx, number, 10);
    strcat(string, number);
    strcat(string, "]: ");
    itoa(timestamp, number, 10);
    strcat(string, number);
    strcat(string, "\n\0");
    
    fp_print_string(string);
}

int main(void) {
    setup_interrupts();

    uint32_t *timestamps = malloc(sizeof(uint32_t) * CONFIG_NITERATIONS);
    if (!timestamps) {
        fp_print_string("Could not malloc\n");
    }
    
    uint32_t begin = rdtime();
    send_sync();

    for (int i = 0; i < CONFIG_NITERATIONS; i++) {
        fp_delay_for(10000000);
        timestamps[i] = rdtime();
    }

    disable_interrupts();
    fp_print_string("FlexPRET: Done app\n");

    for (int i = 0; i < CONFIG_NITERATIONS; i++) {
        uint32_t diff = 0;
        if (i == 0) {
            diff = timestamps[i] - begin;
        } else {
            diff = timestamps[i] - timestamps[i-1];
        }

        print_timestamp_with_index(i, diff);
    }

#if 0
    extern uint32_t periodic_timestamps[100];
    extern uint32_t sporadic_timestamps[100];
    extern uint32_t periodic_timestamps_idx;
    extern uint32_t sporadic_timestamps_idx;
    
    fp_print_string("Some periodic interrupt timestamps\n");
    for (int i = 0; i < periodic_timestamps_idx; i++) {
        print_timestamp_with_index(i, periodic_timestamps[i]);
    }

    fp_print_string("Some sporadic interrupt timestamps\n");
    for (int i = 0; i < sporadic_timestamps_idx; i++) {
        print_timestamp_with_index(i, sporadic_timestamps[i]);
    }
#endif

    return 0;
}
