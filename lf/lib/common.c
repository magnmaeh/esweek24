#include <platform.h>

#if defined(PLATFORM_FLEXPRET)
    #include <flexpret_time.h>
    #define work_us_macro(x) do { \
        fp_wait_for(USEC(x)); \
    } while(0)
#elif __linux__
    #include <unistd.h>
    #define work_us_macro(x) do { \
        usleep(x); \
    } while(0)
#elif defined(PLATFORM_ZEPHYR)
    #include <zephyr/kernel.h>
    #define work_us_macro(x) do { \
        k_sleep(K_USEC(x)); \
    } while(0)
#elif defined(PLATFORM_RP2040)
    #include <hardware/timer.h>
    #define work_us_macro(x) do { \
        busy_wait_us_32(x); \
    } while(0)
#else
    #error "No platform defined!"
#endif

#if defined(PLATFORM_FLEXPRET)
    #include <flexpret_io.h>

    // For FlexPRET, printf is too big
    #define printout_log_macro(it, ts1, ts2, ts3) do { \
        fp_print_int(it); \
        fp_print_string("sampled: "); \
        fp_print_int(ts1); \
        fp_print_string("processed: "); \
        fp_print_int(ts2); \
        fp_print_string("actuated: "); \
        fp_print_int(ts3); \
    } while(0)
#elif __linux__
    #include <stdio.h>
    #define printout_log_macro(it, ts1, ts2, ts3) do { \
        printf("[%i]: sampled: %lli, processed: %lli, actuated: %lli\n",
            it, ts1, ts2, ts3
        );
    } while(0)
#elif defined(PLATFORM_ZEPHYR)
    #include <zephyr/kernel.h>
    #define printout_log_macro(it, ts1, ts2, ts3) do { \
        printk("[%i]: sampled: %lli, processed: %lli, actuated: %lli\n",
            it, ts1, ts2, ts3
        );
    } while(0)
#elif defined(PLATFORM_RP2040)
    #include <stdio.h>
    #define printout_log_macro(it, ts1, ts2, ts3) do { \
        printf_custom("[%i]: sampled: %lli, processed: %lli, actuated: %lli\n",
            it, ts1, ts2, ts3
        );
    } while(0)
#else
    #error "No platform defined!"
#endif

void printout_log(const uint32_t it, const instant_t ts1, const instant_t ts2, const instant_t ts3) {
    printout_log_macro(it, ts1, ts2, ts3);
}

void work_us(const uint32_t us) {
    work_us_macro(us);
}


