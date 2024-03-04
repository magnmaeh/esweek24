#ifndef LIBLFCOMMON_H
#define LIBLFCOMMON_H

#include <platform.h>

#include "common.h"

#if defined(PLATFORM_FLEXPRET)
    #include <flexpret_io.h>

    // For FlexPRET, printf is too big
    #define printout_log_macro(it, ts1, ts2, ts3) do { \
        char string[128] = ""; \
        char number[64] = ""; \
        strcat(string, "["); \
        itoa(it, number, 10); \
        strcat(string, number); \
        strcat(string, "]: sampled: "); \
        itoa(ts1, number,  10); \
        strcat(string, number); \
        strcat(string, ", processed: "); \
        itoa(ts2, number,  10); \
        strcat(string, number); \
        strcat(string, ", actuated: "); \
        itoa(ts3, number,  10); \
        strcat(string, number); \
        strcat(string, "\n\0"); \
        fp_print_string(string); \
    } while(0)
#elif __linux__
    #include <stdio.h>
    #define printout_log_macro(it, ts1, ts2, ts3) do { \
        printf("[%i]: sampled: %lli, processed: %lli, actuated: %lli\n", \
            it, ts1, ts2, ts3 \
        ); \
    } while(0)
#elif defined(PLATFORM_ZEPHYR)
    #include <zephyr/kernel.h>
    #include <stdio.h>
    #define printout_log_macro(it, ts1, ts2, ts3) do { \
        printf("[%i]: sampled: %lli, processed: %lli, actuated: %lli\n", \
            it, ts1, ts2, ts3 \
        ); \
    } while(0)
#elif defined(PLATFORM_RP2040)
    #include <stdio.h>
    #define printout_log_macro(it, ts1, ts2, ts3) do { \
        printf_custom("[%i]: sampled: %lli, processed: %lli, actuated: %lli\n", \
            it, ts1, ts2, ts3 \
        ); \
    } while(0)
#else
    #error "No platform defined!"
#endif

static inline void printout_log(const uint32_t it, const instant_t ts1, const instant_t ts2, const instant_t ts3) {
    printout_log_macro(it, ts1, ts2, ts3);
}

#endif // LIBLFCOMMON_H
