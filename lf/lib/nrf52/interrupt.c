#include <zephyr/kernel.h>
#include <zephyr/drivers/gpio.h>

#include <assert.h>

#define STACKSIZE_DEFAULT (1024)

#define LED0_NODE DT_ALIAS(led0)
#define INT_NODE  DT_ALIAS(intpin)

#if !DT_NODE_HAS_STATUS(LED0_NODE, okay)
#error "Unsupported board: led0 devicetree alias is not defined"
#endif

#if !DT_NODE_HAS_STATUS(INT_NODE, okay)
#error "Unsupported board: interrupt pin devicetree alias is not defined"
#endif

static const struct gpio_dt_spec led        = GPIO_DT_SPEC_GET(LED0_NODE, gpios);
static const struct gpio_dt_spec intservice = GPIO_DT_SPEC_GET(INT_NODE , gpios);

static struct gpio_callback intservice_cb_data;

bool int_service_active     = true;
bool should_print           = true;
static uint32_t ninterrupts = 0;

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
    
    // Configure interrupt pin
	assert(gpio_is_ready_dt(&intservice));
	assert(!gpio_pin_configure_dt(&intservice, GPIO_INPUT));
    assert(!gpio_pin_interrupt_configure_dt(&intservice, GPIO_INT_EDGE_TO_ACTIVE));

    gpio_init_callback(&intservice_cb_data, on_interrrupt, BIT(intservice.pin));
    gpio_add_callback(intservice.port, &intservice_cb_data);

    while (int_service_active) {
        gpio_pin_toggle_dt(&led);
        k_sleep(K_MSEC(500));
    }

    return NULL;
}

K_THREAD_DEFINE(board_on_tid, STACKSIZE_DEFAULT, board_on, NULL, NULL, NULL, 0, 0, 0);
