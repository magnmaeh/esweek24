add_executable(app
        main.c
        ../../../lib/RP2040/printf_custom.c
        ../../../lib/RP2040/interrupt.c
        )

# pull in common dependencies
target_link_libraries(app pico_stdlib)

# create map/bin/hex file etc.
pico_add_extra_outputs(app)

# add url via pico_set_program_url
example_auto_set_url(app)
