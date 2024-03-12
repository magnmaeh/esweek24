#include <zephyr/kernel.h>
#include <zephyr/drivers/gpio.h>

#include <assert.h>

#ifndef PLATFORM_ZEPHYR
    #define PLATFORM_ZEPHYR
    #include "../common.h"
#else
    #include "../lf_common.h"
#endif

#define PERIODIC_INT_NODE DT_ALIAS(periodic_int_pin)
#define SPORADIC_INT_NODE DT_ALIAS(sporadic_int_pin)
#define SYNC_PIN DT_ALIAS(sync_pin)

#if !DT_NODE_HAS_STATUS(PERIODIC_INT_NODE, okay)
#error "Unsupported board: interrupt pin devicetree alias is not defined"
#endif

#if !DT_NODE_HAS_STATUS(SPORADIC_INT_NODE, okay)
#error "Unsupported board: interrupt pin devicetree alias is not defined"
#endif

#if !DT_NODE_HAS_STATUS(SYNC_PIN, okay)
#error "Unsupported board: sync pin devicetree alias is not defined"
#endif

static const struct gpio_dt_spec sync_pin = GPIO_DT_SPEC_GET(SYNC_PIN, gpios);

static const struct gpio_dt_spec periodic_int_spec = GPIO_DT_SPEC_GET(PERIODIC_INT_NODE, gpios);
static const struct gpio_dt_spec sporadic_int_spec = GPIO_DT_SPEC_GET(SPORADIC_INT_NODE, gpios);

static struct gpio_callback periodic_cb_data;
static struct gpio_callback sporadic_cb_data;

uint32_t ninterrupts_periodic = 0;
uint32_t ninterrupts_sporadic = 0;

void on_periodic_interrupt(const struct device *dev, struct gpio_callback *cb, uint32_t pins) {
    on_periodic_interrupt_common();
}

void on_sporadic_interrupt(const struct device *dev, struct gpio_callback *cb, uint32_t pins) {
    on_sporadic_interrupt_common();
}

void configure_pins(void) {

    // Configure periodic interrupt pin
	assert(gpio_is_ready_dt(&periodic_int_spec));
	assert(!gpio_pin_configure_dt(&periodic_int_spec, GPIO_INPUT));
    assert(!gpio_pin_interrupt_configure_dt(&periodic_int_spec, GPIO_INT_EDGE_TO_INACTIVE));

    gpio_init_callback(&periodic_cb_data, on_periodic_interrupt, BIT(periodic_int_spec.pin));
    gpio_add_callback(periodic_int_spec.port, &periodic_cb_data);

    // Configure sporadic interrupt pin
	assert(gpio_is_ready_dt(&sporadic_int_spec));
	assert(!gpio_pin_configure_dt(&sporadic_int_spec, GPIO_INPUT));
    assert(!gpio_pin_interrupt_configure_dt(&sporadic_int_spec, GPIO_INT_EDGE_TO_INACTIVE));

    gpio_init_callback(&sporadic_cb_data, on_sporadic_interrupt, BIT(sporadic_int_spec.pin));
    gpio_add_callback(sporadic_int_spec.port, &sporadic_cb_data);
}

void send_sync(void) {
    assert(device_is_ready(sync_pin.port));
    gpio_pin_configure_dt(&sync_pin, GPIO_OUTPUT_ACTIVE);

    gpio_pin_set_dt(&sync_pin, 1);
}

void disable_interrupts(void) {
    assert(!gpio_pin_interrupt_configure_dt(&periodic_int_spec, GPIO_INT_DISABLE));
    assert(!gpio_pin_interrupt_configure_dt(&sporadic_int_spec, GPIO_INT_DISABLE));
}
