cd ~/projects/c-lf-bench/lf/src

# Set pin low so the program can set it high for waveform generation trigger
gpio mode 15 out
gpio write 15 0

mkdir -p build && cd build
cmake ..
make

./RPi_$1 > ../results.txt
