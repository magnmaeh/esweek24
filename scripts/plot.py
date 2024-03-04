import re
import sys
import os
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

PLATFORMS = ('RPi',)
BENCHMARKS_C  = list((f'C/{p}/{i}' for i in ('int', 'noint') for p in PLATFORMS))
BENCHMARKS_LF = list((f'lf/{p}/int' for p in PLATFORMS))

# TODO: Find more hatches
HATCH = ["*", "//", "...", "---", "OO", "*", "//", "...", "---", "OO"]
CMAP = matplotlib.cm.get_cmap("tab10").colors
NTICKS = 10
SCRIPTPATH = os.path.dirname(__file__)

plt.rcParams.update({'font.size': 26})

def line_to_dict(line: str, type: str):
    """
    Convert a line from [<n>]: <n> to a dictionary.
    """

    ret = re.findall(r'\d+', line)
    if type == 'C':
        return {
            int(ret[0]): {
                'sampled': int(ret[1])
            }
        }
    elif type == 'lf':
        return {
            int(ret[0]): {
                'sampled': int(ret[1]),
                'processed': int(ret[2]),
                'actuated': int(ret[3])
            }
        }
    else:
        assert(False)

def file_to_dict(file: str, type: str):
    if type == 'C':
        with open(file, 'r') as f:
            d = dict()
            for line in f.readlines():
                if '[' in line:
                    d.update(line_to_dict(line, type))
    elif type == 'lf':
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
                    d.update(line_to_dict(line, type))
    return d

def benchmarks_to_dict(niterations, type):
    d = dict()
    benchmarks = BENCHMARKS_C if type == 'C' else BENCHMARKS_LF
    for b in benchmarks:
        path = SCRIPTPATH + f'/../results/{b}-it{niterations}.txt'
        d[b] = file_to_dict(path, type)
    return d

def dict_to_list(dict, key: str) -> list:
    l = list()
    for e in dict:
        l.append(dict[e][key])
    return l

def flatten(dict):
    l = list()
    for e in dict:
        l += dict[e]
    return l

#DATA_LF = benchmarks_to_dict(sys.argv[1], 'lf')
DATA_C  = benchmarks_to_dict(sys.argv[1], 'C')

TITLES = {
    'sampled': 'Input jitter distribution for different implementations of control loop',
    'processed': 'Processing jitter distribution for different implementations of control loop',
    'actuated': 'Output jitter distribution for different implementations of control loop'
}

for type in ('sampled',):
    workset = {x: dict_to_list(DATA_C[x], type) for x in BENCHMARKS_C}
    workset_flat = flatten(workset)
    workset_min = min(workset_flat)
    workset_max = max(workset_flat)

    print("min:", workset_min)
    print("max:", workset_max)

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

    index = np.arange(len(counts[BENCHMARKS_C[0]]))

    fig, ax = plt.subplots(figsize=(10, 6))

    NBARS = len(BENCHMARKS_C)
    bar_width = 1 / NBARS - 0.2
    offsets = [(-NBARS + 1 + 2*i)*bar_width / 2 for i in range(NBARS)]

    for (b, i) in zip(BENCHMARKS_C, range(NBARS)):
        ax.bar(index + offsets[i], counts[b].values(), bar_width, label=b, color=CMAP[i], hatch=HATCH[i], alpha=0.8)

    ax.set_title(TITLES[type])
    ax.set_xlabel('Time (us)')

    ax.set_xticks(index)
    ax.set_xticklabels(["{:.0f}".format(round(x / 1000.0, -1)) for x in counts[BENCHMARKS_C[0]].keys()])
    ax.legend()

    plt.show()

#for haveint in ('int', 'noint'):
#    for type in ('sampled', 'processed', 'actuated'):
#        workset = {x: dict_to_list(DATA_LF[x], type) for x in BENCHMARKS}
#        workset_flat = flatten(workset)
#        workset_min = min(workset_flat)
#        workset_max = max(workset_flat)
#
#        step = (workset_max - workset_min) / NTICKS
#        partitions = [ int(workset_min + x * step)  for x in range(NTICKS + 1) ]
#
#        counts = dict()
#        for e in workset:
#            lower = partitions[0]
#            upper = partitions[1]
#            counts[e] = dict()
#            for limit in partitions[1:]:
#                counts[e][lower] = len(list(filter(lambda x: lower <= x <= upper, workset[e])))
#
#                lower = upper
#                upper = limit
#
#        index = np.arange(len(counts['lf/RP2040/int']))
#
#        fig, ax = plt.subplots(figsize=(10, 6))
#
#        bar_width = 0.2
#        have_interrupts = '(interrupts)' if haveint == 'int' else '(no interrupts)'
#
#        #ax.bar(index - 3/2*bar_width, counts['nrf52/' + haveint].values(), bar_width, label='nrf52' + have_interrupts, color=CMAP[0], hatch=HATCH[0], alpha=0.8)
#        ax.bar(index - 1/2*bar_width, counts['lf/RP2040/' + haveint].values(), bar_width, label='rp2040 ' + have_interrupts, color=CMAP[1], hatch=HATCH[1], alpha=0.8)
#        #ax.bar(index + 1/2*bar_width, counts['FlexPRET/' + haveint].values(), bar_width, label='FlexPRET ' + have_interrupts, color=CMAP[2], hatch=HATCH[2], alpha=0.8)
#        
#        ax.set_title(TITLES[type])
#        ax.set_xlabel('Time (us)')
#
#        ax.set_xticks(index)
#        ax.set_xticklabels(["{:.0f}".format(round(x / 1000.0, -1)) for x in counts['lf/RP2040/int'].keys()])
#        ax.legend()
#
#        plt.show()
