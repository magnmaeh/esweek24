# esweek24
Setup for running benchmarks for paper in esweek2024.

## Zephyr instructions

Follow steps 2-6 in the [official documentation](https://www.lf-lang.org/docs/embedded/zephyr#setting-up-the-lf-zephyr-workspace). (Version 0.6.0.)

Compile the program manually to test it works:
`west lfc ../lf/src/Control_nrf52.lf --build "-p always" --board nrf52dk_nrf52832`

Flash:
`west flash`


## FlexPRET instructions



## 3pi instructions

Follow the [official documentation](west lfc ../lf/src/Control_nrf52.lf --build "-p always" --board nrf52dk_nrf52832) for 3pi setup. (Version 0.6.0.)

Compile an example program to test it works:
`lfc src/HelloPico.lf`

Make sure you have `picotool` installed, which is used for loading executables.