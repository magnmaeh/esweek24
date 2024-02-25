# !/bin/bash

it=$1

# Oneliner from: https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script
here=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
root=$here/..

source ${here}/lib.sh

generate_normal_dist_data $it

read -r -p "Compile and flash? [y/N] " response
case "$response" in
    [yY][eE][sS]|[yY]) 
        # Build and flash SW
        cd $root/lf-zephyr-workspace
        source .venv/bin/activate
        west lfc $root/lf/src/Control_nrf52.lf --build "-p always" --board nrf52dk_nrf52832
        west flash
        deactivate
        cd -
        ;;
    *)
        echo "Skipping build and flash"
        ;;
esac

run_both_benchmarks nrf52 $it
