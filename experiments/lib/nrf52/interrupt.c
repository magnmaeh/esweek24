#include <zephyr/kernel.h>
#include <zephyr/drivers/gpio.h>

#include <assert.h>

#ifndef PLATFORM_ZEPHYR
    #define PLATFORM_ZEPHYR
    #include "../common.h"
#else
    #include "../lf_common.h"
#endif



#define STACKSIZE_DEFAULT (1024)

#define LED0_NODE DT_ALIAS(led0)
#define PERIODIC_INT_NODE DT_ALIAS(periodic_int_pin)
//#define SPORADIC_INT_NODE DT_ALIAS(sporadic_int_pin)
//#define SYNC_PIN DT_ALIAS(sync_pin)

#if !DT_NODE_HAS_STATUS(LED0_NODE, okay)
#error "Unsupported board: led0 devicetree alias is not defined"
#endif

#if !DT_NODE_HAS_STATUS(PERIODIC_INT_NODE, okay)
#error "Unsupported board: interrupt pin devicetree alias is not defined"
#endif

/* #if !DT_NODE_HAS_STATUS(SPORADIC_INT_NODE, okay)
#error "Unsupported board: interrupt pin devicetree alias is not defined"
#endif

#if !DT_NODE_HAS_STATUS(SYNC_PIN, okay)
#error "Unsupported board: sync pin devicetree alias is not defined"
#endif */

static const struct gpio_dt_spec led = GPIO_DT_SPEC_GET(LED0_NODE, gpios);
//static const struct gpio_dt_spec sync_pin = GPIO_DT_SPEC_GET(SYNC_PIN, gpios);

static const struct gpio_dt_spec periodic_int_spec = GPIO_DT_SPEC_GET(PERIODIC_INT_NODE, gpios);
//static const struct gpio_dt_spec sporadic_int_spec = GPIO_DT_SPEC_GET(SPORADIC_INT_NODE, gpios);

static struct gpio_callback periodic_cb_data;
static struct gpio_callback sporadic_cb_data;


bool int_service_active     = true;
bool should_print           = true;
static uint32_t ninterrupts = 0;

void on_periodic_interrupt(const struct device *dev, struct gpio_callback *cb, uint32_t pins) {
    //printf("periodic\n");
    work_us(100);
}

void on_sporadic_interrupt(const struct device *dev, struct gpio_callback *cb, uint32_t pins) {
    //printf("sporadic\n");
    work_us(1000);
}

int configure_interrupts(void) {

    // Configure periodic interrupt pin
	assert(gpio_is_ready_dt(&periodic_int_spec));
	assert(!gpio_pin_configure_dt(&periodic_int_spec, GPIO_INPUT));
    assert(!gpio_pin_interrupt_configure_dt(&periodic_int_spec, GPIO_INT_EDGE_TO_INACTIVE));

    gpio_init_callback(&periodic_cb_data, on_periodic_interrupt, BIT(periodic_int_spec.pin));
    gpio_add_callback(periodic_int_spec.port, &periodic_cb_data);

    // Configure sporadic interrupt pin
	/* assert(gpio_is_ready_dt(&sporadic_int_spec));
	assert(!gpio_pin_configure_dt(&sporadic_int_spec, GPIO_INPUT));
    assert(!gpio_pin_interrupt_configure_dt(&sporadic_int_spec, GPIO_INT_EDGE_TO_INACTIVE));

    gpio_init_callback(&sporadic_cb_data, on_sporadic_interrupt, BIT(sporadic_int_spec.pin));
    gpio_add_callback(sporadic_int_spec.port, &sporadic_cb_data); */

    return 0;
}

int set_sync_pin(void) {
/*     assert(device_is_ready(sync_pin.port));
    gpio_pin_configure_dt(&sync_pin, GPIO_OUTPUT_ACTIVE);

    gpio_pin_set_dt(&sync_pin, 1); */
    return 0;
}

int disable_interrupts(void) {
    assert(!gpio_pin_interrupt_configure_dt(&periodic_int_spec, GPIO_INT_DISABLE));
    //assert(!gpio_pin_interrupt_configure_dt(&sporadic_int_spec, GPIO_INT_DISABLE));
    return 0;
}

void on_interrrupt(const struct device *dev, struct gpio_callback *cb, uint32_t pins) {
    ninterrupts++;

    // Simulate some workload
    // Probably optimized away
    uint32_t sum = 0;
    for (int i = 0; i < 10000; i++) {
        sum += i;
    }
    printk("sum: %i\n", sum);
}

void *board_on(void *args) {
    // Configure LED
    assert(device_is_ready(led.port));
    gpio_pin_configure_dt(&led, GPIO_OUTPUT_ACTIVE);

    while (int_service_active) {
        gpio_pin_toggle_dt(&led);
        k_sleep(K_MSEC(500));
    }

    return NULL;
}

K_THREAD_DEFINE(board_on_tid, STACKSIZE_DEFAULT, board_on, NULL, NULL, NULL, 0, 0, 0);
