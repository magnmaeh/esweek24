#ifndef LIBCOMMON_H
#define LIBCOMMON_H

#define WORK_US_LOOP ((int)(1e4))
#define WORK_US_INT_PERIODIC ((int)(1e2))
#define WORK_US_INT_SPORADIC ((int)(1e3))

#if defined(PLATFORM_FLEXPRET)
    #include <flexpret_time.h>
    #define work_us_macro(x) do { \
        fp_wait_for(USEC(x)); \
    } while(0)
#elif __linux__
    #define work_us_macro(x) do { \
        for (volatile int i = 0; i < ((x) * 154); i++); \
    } while(0)
#elif defined(PLATFORM_ZEPHYR)
    #include <zephyr/kernel.h>
    #define work_us_macro(x) do { \
        k_busy_wait(x); \
    } while(0)
#elif defined(PLATFORM_RP2040)
    #define work_us_macro(x) do { \
        for (volatile int i = 0; i < ((x) / 80 * 1000); i++); \
    } while(0)
#else
    #error "No platform defined!"
#endif

#include <stdint.h>

static inline void work_us(const uint32_t us) {
    work_us_macro(us);
}

// Each platform needs to provide its own implementation of these functions
void configure_pins(void);
void send_sync(void);
void disable_interrupts(void);

#endif // LIBCOMMON_H
