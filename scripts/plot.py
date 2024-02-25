import re
import sys
import os
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

BENCHMARKS = ('nrf52/int', 'nrf52/noint', 'RP2040/int', 'RP2040/noint')
LEGEND_NAMES = ('FP baseline', 'FP decoupled', 'FP bounded', 'i7 Linux baseline', 'i7 Linux decoupled')
HATCH = ["*", "//", "...", "---", "OO"]
CMAP = matplotlib.cm.get_cmap("tab10").colors
NTICKS = 10
SCRIPTPATH = os.path.dirname(__file__)

plt.rcParams.update({'font.size': 26})

def line_to_dict(line: str):
    """
    Convert a line from [<n>]: sampled: <n>, processed: <n>, actuated: <n> 
    to a dictionary.
    """

    ret = re.findall(r'\d+', line)
    return {
        int(ret[0]): {
            'sampled': int(ret[1]),
            'processed': int(ret[2]),
            'actuated': int(ret[3])
        }
    }

def file_to_dict(file: str):
    first = True
    with open(file, 'r') as f:
        d = dict()
        for line in f.readlines():
            if 'sampled:' in line:
                if first:
                    first = False
                    continue
                #if 'Laptop' not in file:
                #    line = line[4:]
                d.update(line_to_dict(line))
    return d

def benchmarks_to_dict(niterations):
    d = dict()
    for b in BENCHMARKS:
        d[b] = file_to_dict(SCRIPTPATH + f'/../results/{b}-it{niterations}.txt')
    return d

def dict_to_list(dict, key: str) -> list():
    l = list()
    for e in dict:
        l.append(dict[e][key])
    return l

def flatten(dict):
    l = list()
    for e in dict:
        l += dict[e]
    return l

DATA = benchmarks_to_dict(sys.argv[1])
TITLES = {
    'sampled': 'Input jitter distribution for different implementations of control loop',
    'processed': 'Processing jitter distribution for different implementations of control loop',
    'actuated': 'Output jitter distribution for different implementations of control loop'
}


for type in ('sampled', 'processed', 'actuated'):
    workset = {x: dict_to_list(DATA[x], type) for x in BENCHMARKS}
    workset_flat = flatten(workset)
    workset_min = min(workset_flat)
    workset_max = max(workset_flat)

    step = (workset_max - workset_min) / NTICKS
    partitions = [ int(workset_min + x * step)  for x in range(NTICKS + 1) ]

    counts = dict()
    for e in workset:
        lower = partitions[0]
        upper = partitions[1]
        counts[e] = dict()
        for limit in partitions[1:]:
            counts[e][lower] = len(list(filter(lambda x: lower <= x <= upper, workset[e])))

            lower = upper
            upper = limit

    index = np.arange(len(counts['nrf52/int']))
    
    fig, ax = plt.subplots(figsize=(10, 6))

    bar_width = 0.2
    ax.bar(index - 3/2*bar_width, counts['nrf52/int'].values(), bar_width, label='nrf52 (interrupts)', color=CMAP[0], hatch=HATCH[0], alpha=0.8)
    ax.bar(index - 1/2*bar_width, counts['nrf52/noint'].values(), bar_width, label='nrf52 (no interrupts)', color=CMAP[1], hatch=HATCH[1], alpha=0.8)
    ax.bar(index + 1/2*bar_width, counts['RP2040/int'].values(), bar_width, label='rp2040 (interrupts)', color=CMAP[2], hatch=HATCH[2], alpha=0.8)
    ax.bar(index + 3/2*bar_width, counts['RP2040/noint'].values(), bar_width, label='rp2040 (no interrupts)', color=CMAP[3], hatch=HATCH[3], alpha=0.8)


    """if type == 'sampled':
        # Combine the first three counts, because they are all the same
        bar_width = 0.4
        ax.bar(index - 1/2*bar_width, counts['int'].values(), bar_width, label='FP baseline + decoupled + bounded', color=CMAP[0], hatch=HATCH[0], alpha=0.8)
        ax.bar(index + 1/2*bar_width, counts['noint'].values(), bar_width, label=LEGEND_NAMES[4], color=CMAP[4], hatch=HATCH[4], alpha=0.8)


    elif type == 'processed':
        bar_width = 0.15
        ax.bar(index - 2*bar_width, counts['BasicControl'].values(), bar_width, label=LEGEND_NAMES[0], color=CMAP[0], hatch=HATCH[0], alpha=0.8)
        ax.bar(index - 1*bar_width, counts['NoJitterControl'].values(), bar_width, label=LEGEND_NAMES[1], color=CMAP[1], hatch=HATCH[1], alpha=0.8)
        ax.bar(index + 0*bar_width, counts['NoJitterBoundedControl'].values(), bar_width, label=LEGEND_NAMES[2], color=CMAP[2], hatch=HATCH[2], alpha=0.8)
        ax.bar(index + 1*bar_width, counts['BasicControlLaptop'].values(), bar_width, label=LEGEND_NAMES[3], color=CMAP[3], hatch=HATCH[3], alpha=0.8)
        ax.bar(index + 2*bar_width, counts['NoJitterControlLaptop'].values(), bar_width, label=LEGEND_NAMES[4], color=CMAP[4], hatch=HATCH[4], alpha=0.8)
        
    else:
        # Combine the 2nd and 3rd counts because they are the same
        bar_width = 0.20
        ax.bar(index - 3*bar_width/2, counts['BasicControl'].values(), bar_width, label=LEGEND_NAMES[0], color=CMAP[0], hatch=HATCH[0], alpha=0.8)
        ax.bar(index + 1*bar_width/2, counts['NoJitterControl'].values(), bar_width, label='FP decoupled + bounded', color=CMAP[1], hatch=HATCH[1], alpha=0.8)
        ax.bar(index - 1*bar_width/2, counts['BasicControlLaptop'].values(), bar_width, label=LEGEND_NAMES[3], color=CMAP[3], hatch=HATCH[3], alpha=0.8)
        ax.bar(index + 3*bar_width/2, counts['NoJitterControlLaptop'].values(), bar_width, label=LEGEND_NAMES[4], color=CMAP[4], hatch=HATCH[4], alpha=0.8)
"""
    ax.set_title(TITLES[type])
    ax.set_xlabel('Time (us)')

    ax.set_xticks(index)
    ax.set_xticklabels(["{:.0f}".format(round(x / 1000.0, -1)) for x in counts['nrf52/int'].keys()])
    ax.legend()

    plt.show()
