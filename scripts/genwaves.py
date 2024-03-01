import argparse
import math
from datetime import date

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--device', type=str, default='something', help='The name of the waveform device')
parser.add_argument('-p', '--period', type=int, default=1, help='Period of waveform in milliseconds (ms)')

subparsers = parser.add_subparsers(dest='mode', required=True)
sporadic_parser = subparsers.add_parser('sporadic')
sporadic_parser.add_argument('-l', '--list', type=int, default=[], nargs='+', help='A list of sporadic interrupts')
periodic_parser = subparsers.add_parser('periodic')
periodic_parser.add_argument('-i', '--interrupt-period', type=int, help='The period to generate interrupts in microseconds (us)')

args = parser.parse_args()

NOW = date.today()

NSAMPLES = 32768 # The maximum number of samples Waveforms allows
LOGIC_HIGH_VOLTAGE = 5 # 5V is logic high
INTERRUPT_STABLE_TIME_US = 1 # How long an interrupt must remain long for

TIME_PER_SAMPLE = (args.period / 1e3) / NSAMPLES
INTERRUPT_STABLE_NSAMPLES = math.ceil((INTERRUPT_STABLE_TIME_US / 1e6) / TIME_PER_SAMPLE)

PREAMBLE = f"""
#Digilent WaveForms Wavegen Custom data
#Device Name: {args.device}
#Serial Number: DEMO
#Date Time: {NOW.isoformat()} 00:00:00.000

"""

def gen_interrupt_waveform(interrupt_points: list[int]) -> str:
    """
    Generate a waveform file (.csv) which is zero at all points except for the
    input points provided in a list.
    
    """

    int_points_idx = 0
    int_high_nsamples = 0

    out = PREAMBLE

    for i in range(NSAMPLES):
        if int_points_idx < len(interrupt_points) and interrupt_points[int_points_idx] == i:
            # If assertion is not correct, another interrupt is provided while
            # an interrupt already is high
            assert(int_high_nsamples == 0)
            int_high_nsamples = max(1, INTERRUPT_STABLE_NSAMPLES)
            int_points_idx += 1
        elif int_high_nsamples > 0:
            int_high_nsamples -= 1
        if int_high_nsamples > 0:
            out += str(LOGIC_HIGH_VOLTAGE) + '\n'
        else:
            out += '0\n'
        
    return out

print(f"""Configuration is:
    Period:      {args.period} (ms)
    Samples:     {NSAMPLES} (max)
    Sample rate: {NSAMPLES / args.period} kHz
    Device:      {args.device}

    Mode:        {args.mode}
    {f'* List:      {args.list}' if args.mode == 'sporadic' else
     f'* Period:    {args.interrupt_period} us'}

    Logic high: {LOGIC_HIGH_VOLTAGE} V
    Interrupt stable samples: {INTERRUPT_STABLE_NSAMPLES}

""")

if args.mode == 'sporadic':
    # List of interrupts is already passed from command line; use it directly
    with open('wave/interrupts-sporadic.csv', 'w') as f:
        f.write(gen_interrupt_waveform(args.list))
elif args.mode == 'periodic':
    # Generate list of interrupts from interrupt period parameter
    NSAMPLES_BETWEEN_INTERRUPTS = ((args.interrupt_period / 1e6) / ((args.period / 1e3) / NSAMPLES))
    
    if (args.period * 1000) % args.interrupt_period != 0:
        print(f'''WARNING: 
The interrupt period ({args.interrupt_period} us) and waveform period ({args.period * 1000} us) are not divisible.
This means there will be some discrepencies if the waveform is run multiple times consequtively.
''')
    
    ninterrupts = math.floor((args.period * 1000) / args.interrupt_period)
    intlist = [math.floor(NSAMPLES_BETWEEN_INTERRUPTS * i) for i in range(ninterrupts)]

    with open('wave/interrupts-periodic.csv', 'w') as f:
        
        
        f.write(gen_interrupt_waveform(intlist))
