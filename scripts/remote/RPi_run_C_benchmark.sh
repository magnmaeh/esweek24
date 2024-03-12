cd ~/projects/c-lf-bench/C

# Set pin low so the program can set it high for waveform generation trigger
gpio mode 15 out
gpio write 15 0
gcc *.c -o run.elf -lwiringPi

./run.elf > results.txt
