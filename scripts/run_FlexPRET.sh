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
        export FLEXPRET_ROOT_DIR=$root/lf-flexpret/flexpret
        $root/lf-flexpret/lingua-franca/bin/lfc -c $root/lf/src/Control_FlexPRET.lf
        make -C $root/lf/src-gen/Control_FlexPRET clean all flash TARGET=fpga WANT_DEBUG=false PRINTF_ENABLED=false
        ;;
    *)
        echo "Skipping build and flash"
        ;;
esac

#run_both_benchmarks FlexPRET $it
