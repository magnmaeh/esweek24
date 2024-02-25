#include <stdbool.h>
#include <hardware/gpio.h>
#include <hardware/irq.h>


#define GPIO_NUMBER_USED (1)

bool should_print = true;
bool int_service_active = true;

void callback(uint gpio, uint32_t event_mask) {
    volatile int sum = 0;
    for (int i = 0; i < 10000; i++) {
        sum += i;
    }
    printf_custom("Sum: %i\n", sum);
}

void setup_interrupts(void) {
    gpio_set_function(GPIO_NUMBER_USED, GPIO_FUNC_PIO0);
    gpio_set_input_enabled(GPIO_NUMBER_USED, true);
    gpio_set_irq_enabled_with_callback(GPIO_NUMBER_USED, GPIO_IRQ_EDGE_RISE, true, callback);
    printf_custom("Setup interrupts\n");
}

void disable_interrupts(void) {
    gpio_set_input_enabled(GPIO_NUMBER_USED, false);
}
