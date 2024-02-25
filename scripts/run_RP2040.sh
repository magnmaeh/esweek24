# !/bin/bash

it=$1

# Oneliner from: https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script
here=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
root=$here/..

source ${here}/lib.sh

read -r -p "Compile and flash? [y/N] " response
case "$response" in
    [yY][eE][sS]|[yY]) 
        # Build and flash SW
        lfc -c $root/lf/src/Control_RP2040.lf
        picotool load -x $root/lf/bin/Control_RP2040.elf
        ;;
    *)
        echo "Skipping build and flash"
        ;;
esac

run_both_benchmarks RP2040 $it
