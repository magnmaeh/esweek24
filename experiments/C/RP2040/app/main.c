#include <pico/sync.h>
#include "/tmp/config.h"

#define PLATFORM_RP2040
#include "../../../lib/common.h"

void printf_custom_init(void);

int clock_get(uint32_t* t) {
    if (!t) {
        return -1;
    }
    // time struct
    absolute_time_t now;
    uint64_t ns_from_boot;

    now = get_absolute_time();
    ns_from_boot = to_us_since_boot(now) * 1000;
    *t = (uint32_t) ns_from_boot;
    return 0; 
}


int main(void) {
    printf_custom_init();
    configure_pins();

    uint32_t timestamps[CONFIG_NITERATIONS];
    uint32_t begin = 0;

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
        printf_custom("[%i]: %i\n", i, diff);
    }
}

