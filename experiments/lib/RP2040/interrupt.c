#include <stdbool.h>
#include <hardware/gpio.h>
#include <hardware/irq.h>

#define PLATFORM_RP2040
#include "../common.h"

#define GPIO_SYNC_PIN (13)
#define GPIO_PERIODIC_INTS (14)
#define GPIO_SPORADIC_INTS (15)

uint32_t ninterrupts_periodic = 0;
uint32_t ninterrupts_sporadic = 0;

void callback(uint gpio, uint32_t event_mask) {
    if (gpio == GPIO_PERIODIC_INTS) {
        on_periodic_interrupt_common();
    } else if (gpio == GPIO_SPORADIC_INTS) {
        on_sporadic_interrupt_common();
    } else {
        printf_custom("Got unknown int\n");
    }
}

void configure_pins(void) {
    // Set up periodic interrupt pin
    gpio_set_function(GPIO_PERIODIC_INTS, GPIO_FUNC_PIO0);
    gpio_set_input_enabled(GPIO_PERIODIC_INTS, true);
    gpio_set_irq_enabled_with_callback(GPIO_PERIODIC_INTS, GPIO_IRQ_EDGE_RISE, true, callback);
    
    // Set up sporadic interrupt pin
    gpio_set_function(GPIO_SPORADIC_INTS, GPIO_FUNC_PIO0);
    gpio_set_input_enabled(GPIO_SPORADIC_INTS, true);
    gpio_set_irq_enabled_with_callback(GPIO_SPORADIC_INTS, GPIO_IRQ_EDGE_RISE, true, callback);

    // Set up synchronization pin
    gpio_set_function(GPIO_SYNC_PIN, GPIO_FUNC_PIO0);
    gpio_init(GPIO_SYNC_PIN);
    gpio_set_dir(GPIO_SYNC_PIN, true);
}

void send_sync(void) {
    gpio_put(GPIO_SYNC_PIN, true);
}

void disable_interrupts(void) {
    gpio_set_input_enabled(GPIO_PERIODIC_INTS, false);
    gpio_set_input_enabled(GPIO_SPORADIC_INTS, false);

    printf_custom("Got %i periodic interrupts\n", ninterrupts_periodic);
    printf_custom("Got %i sporadic interrupts\n", ninterrupts_sporadic);
}
