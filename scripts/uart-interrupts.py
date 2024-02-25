from serial import Serial
import time
import random

import argparse
parser = argparse.ArgumentParser()

parser.add_argument("-o", "--outfile", type=str, required=True)
parser.add_argument("-i", "--interrupts", type=bool, required=True)
parser.add_argument("-p", "--platform", type=str, 
                    choices=['FlexPRET', 'nrf52', 'RP2040', 'RPi'],
                    required=True)

args = parser.parse_args()

if args.platform == 'FlexPRET':
    receive_serial   = Serial('/dev/ttyUSB0', baudrate=115200, exclusive=True, timeout=0.01)
    interrupt_serial = receive_serial
elif args.platform == 'nrf52':
    receive_serial   = Serial('/dev/ttyACM0', baudrate=115200, exclusive=True, timeout=0.01)
    interrupt_serial = Serial('/dev/ttyUSB0', baudrate=115200, exclusive=True, timeout=0.01)
elif args.platform == 'RP2040':
    receive_serial   = Serial('/dev/ttyUSB0', baudrate=115200, exclusive=True, timeout=0.01)
    interrupt_serial = receive_serial
else:
    pass

done = False

file = ""

while True:
    if not done and args.interrupts:
        interrupt_serial.write(b'\x00')
        wait = random.randint(80, 120) / 1000.0
        time.sleep(wait)
    
    received = receive_serial.read(256).decode('utf-8')
    if "sampled" in received:
        done = True
    
    if done:
        if len(received) > 0:
            file += received
        elif done:
            break

with open(args.outfile, 'w') as f:
    f.write(file)
