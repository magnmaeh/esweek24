# Configure cleanup so exiting does not leave interrupt serivice on
set -e

# Check input
if [ $# -eq 0 ] 
then
    echo "Usage: $0 <number of iterations>"
    exit 1
fi

C_exp=$root/experiments/C/$platform
LF_exp_folder=$root/experiments/lf/src
LF_srcgen_folder=$root/experiments/src-gen
LF_exp_control=$root/experiments/lf/src/Control_$platform.lf
LF_exp_control_delayed=$root/experiments/lf/src/ControlDelayed_$platform.lf

mkdir -p $here/../results/C/$platform
mkdir -p $here/../results/lf/$platform/Work
mkdir -p $here/../results/lf/$platform/Control

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

# $1: Iterations
# $2: Platform
# $3: Language
# $4: int/noint
# $5: Benchmark name (only relevant if $3 == "lf")
run_benchmark_common() {
    if [ $3 == "lf" ]
    then
        outfile=$here/../results/$3/$2/$5/$4-it$1.txt
    else
        outfile=$here/../results/$3/$2/$4-it$1.txt
    fi

    echo "Outfile is:" $outfile
    python3 $root/scripts/uart.py --platform $2 --outfile $outfile
}

# $1: Iterations
# $2: Platform
# $3: Language
# $4: int/noint
# $5: Benchmark name (only relevant if $3 == "lf")
run_benchmark_RPi_common() {
    # Compiles and runs the programs on RPi
    if [ $3 == "C" ]
    then
        script=RPi_run_C_benchmark.sh
        results_location=$3
        outfile=$root/results/$3/$2/$4-it$1.txt
    elif [ $3 == "lf" ]
    then
        script=RPi_run_lf_benchmark.sh
        results_location=$3/src
        outfile=$root/results/$3/$2/$5/$4-it$1.txt
    fi

    ssh blueberry 'bash -s' < $root/scripts/remote/$script $5
    scp blueberry:~/projects/c-lf-bench/$results_location/results.txt $outfile
}

# $1: Iterations
# $2: Platform
# $3: Language
# $4: Benchmark name
run_benchmark_noint() {
    prompt_disable_interrupts
    echo "Starting benchmark WITHOUT interrupts"
    if [ $2 == "FlexPRET" ]
    then
        if [ $3 == "C" ]
        then
            make -C $C_exp flash TARGET=fpga
        elif [ $3 == "lf" ]
        then
            make -C $root/experiments/src-gen/$2_$4 flash TARGET=fpga
        fi
        run_benchmark_common $1 $2 $3 noint $4
    elif [ $2 == "RPi" ]
    then
        run_benchmark_RPi_common $1 $2 $3 noint $4
    else
        run_benchmark_common $1 $2 $3 noint $4
    fi
}

# $1: Iterations
# $2: Platform
# $3: Language
# $4: Benchmark name (only relevant if $3 == "lf")
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
            make -C $root/experiments/src-gen/$2_$4 flash TARGET=fpga
        fi
        
        run_benchmark_common $1 $2 $3 int $4
    elif [ $2 == "RPi" ]
    then
        run_benchmark_RPi_common $1 $2 $3 int $4
    else
        run_benchmark_common $1 $2 $3 int $4
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
# $3: Benchmark name
# $4: int/noint
prompt_run_single_lf_benchmark() {
    read -r -p "Run $2 lf benchmarks? (will recompile and flash) [y/N] " response
    case "$response" in
        [yY][eE][sS]|[yY]) 
            # Build and flash SW
            if [ $2 == "FlexPRET" ]
            then
                # Need to use lfc inside lf-flexpret since FlexPRET is not yet
                # supported by LF and the port uses lf 0.4.1
                ./lf-flexpret/lingua-franca/bin/lfc -c $LF_exp_folder/$2_$3.lf -o $root/experiments
                make -C $LF_srcgen_folder/$2_$3 clean all TARGET=fpga WANT_DEBUG=false PRINTF_ENABLED=false
            elif [ $2 == "nrf52" ]
            then
                cd $root/lf-zephyr-workspace/
                source env.sh
                west lfc $LF_exp_folder/$2_$3.lf --build "-p always" --board nrf52dk_nrf52832
                west flash
                deactivate
                cd -
            elif [ $2 == "RP2040" ]
            then
                lfc -c $LF_exp_folder/$2_$3.lf
                picotool load -x $root/experiments/lf/bin/$2_$3.elf
            elif [ $2 == "RPi" ]
            then
                lfc -c -n $LF_exp_folder/$2_$3.lf
                scp -r $root/experiments/lf/src-gen/$2_$3/* blueberry:~/projects/c-lf-bench/lf/src
            else
                echo "Not supported platform: $2"
            fi

            if [ $4 == "int" ]
            then
                run_benchmark_int $1 $2 lf $3
            elif [ $4 == "noint" ]
            then
                run_benchmark_noint $1 $2 lf $3
            fi
            ;;
        *)
            echo "Skipping $2 lf benchmarks"
            ;;
    esac
}

# $1: Iterations
# $2: Platform
prompt_run_lf_benchmarks() {
    #prompt_run_single_lf_benchmark $1 $2 Work noint
    prompt_run_single_lf_benchmark $1 $2 Control int
}
