# Configure cleanup so exiting does not leave interrupt serivice on
set -e

# Check input
if [ $# -eq 0 ] 
then
    echo "Usage: $0 <number of iterations>"
    exit 1
fi

C_exp=$root/experiments/C/$platform
LF_exp=$root/experiments/lf/src/Control_$platform.lf

# $1: How many data points to generate
generate_normal_dist_data() {
    # Generate /tmp/config.h and /tmp/normal.txt, which are included
    # by the applications
    python3 $here/normal.py $1
}

prompt_disable_interrupts() {
    echo "Please disable interrupts, reset the board, and press any key to continue..."
    read -s -n 1
}

prompt_enable_interrupts() {
    echo "Please enable interrupts, reset the board, and press any key to continue..."
    read -s -n 1
}

run_benchmark_common() {
    python3 $here/uart.py --platform $2 --outfile $here/../results/$3/$2/$4-it$1.txt    
}

# $1: Iterations
# $2: Platform
# $3: Language
# $4: int/noint
run_benchmark_RPi_common() {
    # Compiles and runs the programs on RPi
    if [ $3 == "C" ]
    then
        script=RPi_run_C_benchmark.sh
        results_location=$3
    elif [ $3 == "lf" ]
    then
        script=RPi_run_lf_benchmark.sh
        results_location=$3/src
    fi

    ssh blueberry 'bash -s' < $root/scripts/remote/$script
    scp blueberry:~/projects/c-lf-bench/$results_location/results.txt $root/results/$3/$2/$4-it$1.txt
}

run_benchmark_noint() {
    prompt_disable_interrupts
    echo "Starting benchmark WITHOUT interrupts"
    if [ $2 == "FlexPRET" ]
    then
        make -C $C_exp flash TARGET=fpga
        run_benchmark_common $1 $2 $3 noint
    elif [ $2 == "RPi" ]
    then
        run_benchmark_RPi_common $1 $2 $3 noint
    else
        run_benchmark_common $1 $2 $3 noint
    fi
}

run_benchmark_int() {
    prompt_enable_interrupts
    echo "Starting benchmark WITH interrupts"
    if [ $2 == "FlexPRET" ]
    then
        if [ $3 == "C" ]
        then
            make -C $C_exp flash TARGET=fpga
        elif [ $3 == "lf" ]
        then
            make -C $root/experiments/src-gen/Control_$2 flash TARGET=fpga
        fi
        
        run_benchmark_common $1 $2 $3 int
    elif [ $2 == "RPi" ]
    then
        run_benchmark_RPi_common $1 $2 $3 int
    else
        run_benchmark_common $1 $2 $3 int
    fi
}

# $1: Iterations
# $2: Platform
prompt_run_C_benchmarks() {
    read -r -p "Run $2 C benchmarks? (will recompile and flash) [y/N] " response
    case "$response" in
        [yY][eE][sS]|[yY]) 
            # Build and flash SW
            if [ $2 == "FlexPRET" ]
            then
                make -C $C_exp clean all TARGET=fpga WANT_DEBUG=false PRINT_ENABLED=false
            elif [ $2 == "nrf52" ]
            then
                source $root/lf-zephyr-workspace/.venv/bin/activate
                west build -b nrf52dk_nrf52832 -p always $C_exp
                west flash
                deactivate
            elif [ $2 == "RP2040" ]
            then
                cmake -S $C_exp -B $C_exp/build
                make -C $C_exp/build
                picotool load -x $C_exp/build/app/app.elf
            elif [ $2 == "RPi" ]
            then
                scp $root/experiments/lib/common.h blueberry:~/projects/c-lf-bench/C
                scp $root/experiments/lib/RPi/interrupt.c blueberry:~/projects/c-lf-bench/C
                scp $root/experiments/C/$platform/* blueberry:~/projects/c-lf-bench/C
            else
                echo "Not supported platform: $2"
            fi

            run_benchmark_noint $1 $2 C
            run_benchmark_int $1 $2 C
            ;;
        *)
            echo "Skipping $2 C benchmarks"
            ;;
    esac
}

# $1: Iterations
# $2: Platform
prompt_run_lf_benchmarks() {
    read -r -p "Run $2 lf benchmarks? (will recompile and flash) [y/N] " response
    case "$response" in
        [yY][eE][sS]|[yY]) 
            # Build and flash SW
            if [ $2 == "FlexPRET" ]
            then
                # Need to use lfc inside lf-flexpret since FlexPRET is not yet
                # supported by LF and the port uses lf 0.4.1
                ./lf-flexpret/lingua-franca/bin/lfc -c $LF_exp -o $root/experiments
                make -C $root/experiments/src-gen/Control_$2 clean all TARGET=fpga WANT_DEBUG=false PRINTF_ENABLED=false
            elif [ $2 == "nrf52" ]
            then
                cd $root/lf-zephyr-workspace/
                source .venv/bin/activate
                west lfc $root/experiments/lf/src/Control_nrf52.lf --build "-p always" --board nrf52dk_nrf52832 --lfc $root/../../lingua-franca/bin/lfc-dev
                west flash
                deactivate
                cd -
            elif [ $2 == "RP2040" ]
            then
                lfc -c $LF_exp
                picotool load -x $root/experiments/lf/bin/Control_$platform.elf
            elif [ $2 == "RPi" ]
            then
                lfc -c -n $LF_exp -o $root/experiments
                scp -r $root/experiments/src-gen/Control_$platform/* blueberry:~/projects/c-lf-bench/lf/src
            else
                echo "Not supported platform: $2"
            fi

            run_benchmark_int $1 $2 lf
            ;;
        *)
            echo "Skipping $2 lf benchmarks"
            ;;
    esac
}
