#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>

#include <wiringPi.h>
#include "/tmp/config.h"
#include "common.h"

int main(void) {
    configure_pins();

    uint32_t timestamps[CONFIG_NITERATIONS];
    struct timespec ts_begin;
    clock_gettime(CLOCK_REALTIME, &ts_begin);
    uint32_t begin = ts_begin.tv_nsec;

    send_sync();

    struct timespec ts;
    for (int i = 0; i < CONFIG_NITERATIONS; i++) {
        work_amount(WORK_AMOUNT_LOOP);
        clock_gettime(CLOCK_REALTIME, &ts);
        timestamps[i] = (ts.tv_sec - ts_begin.tv_sec) * (int) (1e9) + ts.tv_nsec;
    }

    shutdown();
    
    for (int i = 0; i < CONFIG_NITERATIONS; i++) {
        uint32_t diff = 0;
        if (i == 0) {
            diff = timestamps[i] - begin;
        } else {
            diff = timestamps[i] - timestamps[i-1];
        }
        printf("[%i]: %i\n", i, diff);
    }
}
