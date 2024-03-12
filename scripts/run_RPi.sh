# !/bin/bash

it=$1

# Oneliner from: https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script
here=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
root=$here/..

platform=RPi
source ${here}/lib.sh

generate_normal_dist_data $it

scp /tmp/config.h blueberry:/tmp
scp /tmp/normal.txt blueberry:/tmp

prompt_run_C_benchmarks $it $platform
prompt_run_lf_benchmarks $it $platform $LF_exp_control
