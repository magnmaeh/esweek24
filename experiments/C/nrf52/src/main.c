
#include "/tmp/config.h"
#include <zephyr/drivers/counter.h>
#include <zephyr/kernel.h>
#include <stdlib.h>

#define PLATFORM_ZEPHYR
#include "../../../lib/common.h"

#define SECOND(t) (t * 1000000000LL)
#define TIMER DT_NODELABEL(timer1)

const struct device *const counter_dev = DEVICE_DT_GET(TIMER);

static int64_t epoch_duration_nsec;
static int64_t epoch_duration_usec;
static volatile int64_t last_epoch_nsec = 0;
static uint32_t counter_freq;

static uint32_t begin = 0;

static void overflow_callback(const struct device *dev, void *user_data) {
    printk("Overflow\n");
}

/**
 * Initialize the Counter device. Check its frequency and compute epoch
 * durations.
 */
void clock_init() {
    struct counter_top_cfg counter_top_cfg;
    uint32_t counter_max_ticks=0;
    int res;
	
    // Verify that we have the device
    if (!device_is_ready(counter_dev)) {
        printk("ERROR: counter device not ready.\n");
    }

    // Verify that it is working as we think
    if(!counter_is_counting_up(counter_dev)) {
        printk("ERROR: Counter is counting down \n");
    }
    
    // Get the frequency of the timer
    counter_freq = counter_get_frequency(counter_dev);

    // Calculate the duration of an epoch. Compute both
    //  nsec and usec now at boot to avoid these computations later
    counter_max_ticks = counter_get_max_top_value(counter_dev);
    epoch_duration_usec = counter_ticks_to_us(counter_dev, counter_max_ticks);
    epoch_duration_nsec = epoch_duration_usec * 1000LL;
    
    // Set the max_top value to be the maximum
    counter_top_cfg.ticks = counter_max_ticks;
    counter_top_cfg.callback = overflow_callback;
    res = counter_set_top_value(counter_dev, &counter_top_cfg);
    if (res != 0) {
        printk("ERROR: Timer couldnt set top value\n");
    }

    printk("--- Using LF Zephyr Counter Clock with a frequency of %u Hz and wraps every %u sec\n", 
      counter_freq, counter_max_ticks/counter_freq);
    
    // Start counter
    counter_start(counter_dev);
}

int clock_get(uint32_t* t) {
    static uint64_t last_nsec = 0;
    uint32_t now_cycles;
    int res;
    uint64_t now_nsec;
    
    res = counter_get_value(counter_dev, &now_cycles);
    now_nsec = counter_ticks_to_us(counter_dev, now_cycles)*1000ULL + last_epoch_nsec;

    // Make sure that the clock is monotonic. We might have had a wrap but the
    // epoch has not been updated because interrupts are disabled.
    if (now_nsec < last_nsec) {
        now_nsec = last_nsec + 1;
    }

    *t = now_nsec;
    last_nsec = now_nsec;
    return 0;
}

int main(void) {
    clock_init();
    configure_pins();
    printf("Start app\n");

    uint32_t *timestamps = malloc(sizeof(uint32_t) * CONFIG_NITERATIONS);
    
    send_sync();
    clock_get(&begin);
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

