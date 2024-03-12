#ifndef LIBCOMMON_H
#define LIBCOMMON_H

#define WORK_AMOUNT_LOOP ((int)(1e4))
#define WORK_AMOUNT_INT_PERIODIC ((int)(1e2))
#define WORK_AMOUNT_INT_SPORADIC ((int)(1e3))

#if defined(PLATFORM_FLEXPRET)
    #include <flexpret_time.h>
    #define USEC(t) (t * 1000LL)
    #define work_us_macro(x) do { \
        fp_wait_for(USEC(x)); \
    } while(0)
#elif __linux__
    #include <unistd.h>
    #define work_us_macro(x) do { \
        for (volatile int i = 0; i < (x) * 154; i++); \
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

#if defined(PLATFORM_FLEXPRET)
    #include <flexpret_io.h>
    #define print_string(str) do { \
        fp_print_string(str); \
    } while(0)
#elif __linux__
    #include <stdio.h>
    #define print_string(str) do { \
        printf("%s", str); \
    } while(0)
#elif defined(PLATFORM_ZEPHYR)
    #include <zephyr/kernel.h>
    #define print_string(str) do { \
        printk("%s", str); \
    } while(0)
#elif defined(PLATFORM_RP2040)
    int printf_custom(char *fmt, ...);
    #define print_string(str) do { \
        printf_custom("%s", str); \
    } while(0)
#else
    #error "No platform defined!"
#endif

#include <stdint.h>

static inline void work_amount(const uint32_t us) {
    //work_us_macro(us);
    for (volatile int i = 0; i < 10 * us; i++);
}

// Each platform needs to provide its own implementation of these functions
void configure_pins(void);
void send_sync(void);
void disable_interrupts(void);

static inline void on_periodic_interrupt_common(void) {
    extern uint32_t ninterrupts_periodic;
    
    ninterrupts_periodic++;
    work_amount(WORK_AMOUNT_INT_PERIODIC);
}

static inline void on_sporadic_interrupt_common(void) {
    extern uint32_t ninterrupts_sporadic;
    
    ninterrupts_sporadic++;
    work_amount(WORK_AMOUNT_INT_SPORADIC);
}

static inline void shutdown(void) {
    extern uint32_t ninterrupts_periodic;
    extern uint32_t ninterrupts_sporadic;

    disable_interrupts();

    print_string("Done\n");

#if defined(PLATFORM_FLEXPRET)
    fp_print_string("Got ");
    fp_print_int(ninterrupts_periodic);
    fp_print_string(" periodic interrupts\n");

    fp_print_string("Got ");
    fp_print_int(ninterrupts_sporadic);
    fp_print_string(" sporadic interrupts\n");
#elif __linux__
    printf("Got %i periodic interrupts\n", ninterrupts_periodic);
    printf("Got %i sporadic interrupts\n", ninterrupts_sporadic);
#elif defined(PLATFORM_ZEPHYR)
    printk("Got %i periodic interrupts\n", ninterrupts_periodic);
    printk("Got %i sporadic interrupts\n", ninterrupts_sporadic);
#elif defined(PLATFORM_RP2040)
    printf_custom("Got %i periodic interrupts\n", ninterrupts_periodic);
    printf_custom("Got %i sporadic interrupts\n", ninterrupts_sporadic);
#else
    #error "No platform defined!"
#endif
}

#endif // LIBCOMMON_H
