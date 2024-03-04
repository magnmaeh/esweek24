from serial import Serial
import time
import random

import argparse
parser = argparse.ArgumentParser()

parser.add_argument("-o", "--outfile", type=str, required=True)
parser.add_argument("-p", "--platform", type=str, 
                    choices=['FlexPRET', 'nrf52', 'RP2040', 'RPi'],
                    required=True)

args = parser.parse_args()

if args.platform == 'FlexPRET':
    receive_serial   = Serial('/dev/ttyUSB0', baudrate=115200, exclusive=True, timeout=0.01)
elif args.platform == 'nrf52':
    receive_serial   = Serial('/dev/ttyACM0', baudrate=115200, exclusive=True, timeout=0.01)
elif args.platform == 'RP2040':
    receive_serial   = Serial('/dev/ttyUSB0', baudrate=115200, exclusive=True, timeout=0.01)
else:
    pass

done = False

file = ""

while True:
    received = receive_serial.read(256).decode('utf-8')
    if 'Done' in received:
        done = True

    if done:
        if len(received) > 0:
            file += received
        elif done:
            break

with open(args.outfile, 'w') as f:
    f.write(file)
