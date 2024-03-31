#ifndef LIBLFCOMMON_H
#define LIBLFCOMMON_H

#include <platform.h>

#include "common.h"

#if defined(PLATFORM_FLEXPRET)
    #include <flexpret_io.h>

    #define make_log1str(it, ts) do { \
        strcat(string, "["); \
        itoa(it, number, 10); \
        strcat(string, number); \
        strcat(string, "]: sampled: "); \
        itoa(ts, number,  10); \
        strcat(string, number); \
    } while(0)

    #define printout_log1_macro(it, ts) do { \
        char string[128] = ""; \
        char number[64] = ""; \
        make_log1str(it, ts); \
        strcat(string, "\n\0"); \
        fp_print_string(string); \
    } while(0)

    #define printout_log2_macro(it, b, ts1, ts2) do { \
        char string[128] = ""; \
        char number[64] = ""; \
        strcat(string, "["); \
        itoa(it, number, 10); \
        strcat(string, number); \
        strcat(string, "]: bank: "); \
        itoa(b, number, 10); \
        strcat(string, number); \
        strcat(string, ", before: "); \
        itoa(ts1, number,  10); \
        strcat(string, number); \
        strcat(string, ", after: "); \
        itoa(ts2, number,  10); \
        strcat(string, number); \
        strcat(string, "\n\0"); \
        fp_print_string(string); \
    } while(0)

    // For FlexPRET, printf is too big
    #define printout_log3_macro(it, ts1, ts2, ts3) do { \
        char string[128] = ""; \
        char number[64] = ""; \
        make_log1str(it, ts1); \
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
    #define printout_log1_macro(it, ts) do { \
        printf("[%i]: sampled: %i\n", it, ts); \
    } while(0)

    #define printout_log2_macro(it, b, ts1, ts2) do { \
        printf("[%i]: bank: %i, before: %i, after: %i\n", it, b, ts1, ts2); \
    } while(0)
    #define printout_log3_macro(it, ts1, ts2, ts3) do { \
        printf("[%i]: sampled: %i, processed: %i, actuated: %i\n", \
            it, ts1, ts2, ts3 \
        ); \
    } while(0)
#elif defined(PLATFORM_ZEPHYR)
    #include <zephyr/kernel.h>
    #include <stdio.h>
    #define printout_log1_macro(it, ts) do { \
        printk("[%i]: sampled: %i\n", it, ts); \
    } while(0)
    #define printout_log2_macro(it, b, ts1, ts2) do { \
        printf("[%i]: bank: %i, before: %i, after: %i\n", it, b, ts1, ts2); \
    } while(0)
    #define printout_log3_macro(it, ts1, ts2, ts3) do { \
        printk("[%i]: sampled: %i, processed: %i, actuated: %i\n", \
            it, ts1, ts2, ts3 \
        ); \
    } while(0)
#elif defined(PLATFORM_RP2040)
    #include <stdio.h>
    #define printout_log1_macro(it, ts) do { \
        printf_custom("[%i]: sampled: %i\n", it, ts); \
    } while(0)
    #define printout_log2_macro 
    #define printout_log3_macro(it, ts1, ts2, ts3) do { \
        printf_custom("[%i]: sampled: %i, processed: %i, actuated: %i\n", \
            it, ts1, ts2, ts3 \
        ); \
    } while(0)
#else
    #error "No platform defined!"
#endif

static inline void printout_log1(const uint32_t it, const uint32_t ts) {
    printout_log1_macro(it, ts);
}

static inline void printout_log2(const uint32_t it, const uint32_t bank_index, const uint32_t ts1, const uint32_t ts2) {
    printout_log2_macro(it, bank_index, ts1, ts2);
}

static inline void printout_log3(const uint32_t it, const uint32_t ts1, const uint32_t ts2, const uint32_t ts3) {
    printout_log3_macro(it, ts1, ts2, ts3);
}

#endif // LIBLFCOMMON_H
