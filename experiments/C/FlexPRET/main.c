#include <string.h>
#include <stdlib.h>
#include <flexpret.h>

#define PLATFORM_FLEXPRET
#include "../../lib/common.h"
#include "/tmp/config.h"

void setup_interrupts(void);
void disable_interrupts(void);
void send_sync(void);

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
    configure_pins();

    uint32_t *timestamps = malloc(sizeof(uint32_t) * CONFIG_NITERATIONS);
    if (!timestamps) {
        fp_print_string("Could not malloc\n");
    }

    uint32_t begin = rdtime();
    send_sync();

    for (int i = 0; i < CONFIG_NITERATIONS; i++) {
        work_amount(WORK_AMOUNT_LOOP);
        timestamps[i] = rdtime();
    }

    shutdown();

    for (int i = 0; i < CONFIG_NITERATIONS; i++) {
        uint32_t diff = 0;
        if (i == 0) {
            diff = timestamps[i] - begin;
        } else {
            diff = timestamps[i] - timestamps[i-1];
        }

        print_timestamp_with_index(i, diff);
    }

    return 0;
}
