
#include "/tmp/config.h"
#include <zephyr/kernel.h>
#include <stdlib.h>

#define PLATFORM_ZEPHYR
#include "../../../lib/common.h"

#define SECOND(t) (t * 1000000000LL)

static uint32_t timer_freq = 0;
static uint32_t begin = 0;

void clock_init(void) {
    timer_freq = CONFIG_SYS_CLOCK_HW_CYCLES_PER_SEC;
}

int clock_get(uint32_t* t) {
    uint32_t now_cycles = k_cycle_get_32();
    *t = (SECOND(1)/CONFIG_SYS_CLOCK_HW_CYCLES_PER_SEC)*now_cycles;
    return 0;
}

int main(void) {
    clock_init();
    configure_pins();
    printf("Start app\n");

    uint32_t *timestamps = malloc(sizeof(uint32_t) * CONFIG_NITERATIONS);
    
    clock_get(&begin);
    send_sync();
    
    for (int i = 0; i < CONFIG_NITERATIONS; i++) {
        work_amount(WORK_AMOUNT_LOOP);
        clock_get(&timestamps[i]);
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

