# Configure cleanup so exiting does not leave interrupt serivice on
set -e

# Check input
if [ $# -eq 0 ] 
then
    echo "Usage: $0 <number of iterations>"
    exit 1
fi

# $1: How many data points to generate
generate_normal_dist_data() {
    # Generate /tmp/config.h and /tmp/normal.txt, which are included
    # by the applications
    python3 ${lflib_scripts}/normal.py $1
}

prompt_any_key() {
    echo "Please reset the board and press any key to continue..."
    read -s -n 1
}

# $1: Platform [FlexPRET, nrf52, RP2040, Linux]
# $2: Number of iterations
run_benchmark_interrupts() {
    echo "Running benchmark with interrupts..."
    python3 $here/uart-interrupts.py --platform $1 --outfile $here/../results/$1/int-it$2.txt --interrupts True

}

# $1: Platform [FlexPRET, nrf52, RP2040, Linux]
# $2: Number of iterations
run_benchmark_no_interrupts() {
    echo "Running benchmark without interrupts..."
    python3 $here/uart-interrupts.py --platform $1 --outfile $here/../results/$1/noint-it$2.txt --interrupts False

}

# $1: Platform [FlexPRET, nrf52, RP2040, Linux]
# $2: Number of iterations
run_both_benchmarks() {
    prompt_any_key
    run_benchmark_interrupts $1 $2
    prompt_any_key
    run_benchmark_no_interrupts $1 $2
}


