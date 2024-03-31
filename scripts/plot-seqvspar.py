import pandas
import re
import seaborn as sns
import matplotlib.pyplot as plt

from pathlib import Path

HERE = Path(__file__).parent.resolve()

def unnormalize(x, minval, maxval):
    return x * (maxval - minval) + minval

def normalize(x, minval, maxval):
    return (x - minval) / (maxval - minval)

def normalize_list(lst, minval, maxval):
    return [normalize(x, minval, maxval) for x in lst]

def line_to_numbers(line: str):
    return re.findall(r'\d+', line)

def file_to_lists(file):
    idxs = list()
    bankid = list()
    befores = list()
    afters = list()

    for line in file:
        if '[' in line:
            ret = line_to_numbers(line)
            idxs.append(ret[0])
            bankid.append(int(ret[1]))
            befores.append(float(ret[2]))
            afters.append(float(ret[3]))

    return idxs, bankid, befores, afters

def benchmark_to_dataframe(benchmark, iterations):
    with open(str(HERE / '..' / 'results' / benchmark) + f'-it{iterations}-seq.txt', 'r') as f:
        file = f.readlines()

    idxs_seq, bankids_seq, befores_seq, afters_seq = file_to_lists(file)

    with open(str(HERE / '..' / 'results' / benchmark) + f'-it{iterations}-par.txt', 'r') as f:
        file = f.readlines()

    idxs_par, bankids_par, befores_par, afters_par = file_to_lists(file)

    timestamps = befores_seq + afters_seq + befores_par + afters_par
    
    minval = min(timestamps)
    maxval = max(timestamps)

    return pandas.DataFrame({
        'idx': idxs_seq + idxs_par,
        'bank': bankids_seq + bankids_par,
        'after': afters_seq + afters_par,
        'before': befores_seq + befores_par,
        'after_norm': normalize_list(afters_seq + afters_par, minval, maxval),
        'before_norm': normalize_list(befores_seq + befores_par, minval, maxval),
        'Threading': ['Single-threaded'] * len(idxs_seq) + ['Multi-threaded'] * len(idxs_par)
    })

VERTIVAL_TEXT_HEIGHT = 10
MARKER_SIZE = 800
FONTSIZE = 56

def combine_ts(df):
    return df.before.to_list() + df.after.to_list()

def annotate(x, ax, down=True, xoffset = 0):
    height = -VERTIVAL_TEXT_HEIGHT if down else VERTIVAL_TEXT_HEIGHT
    f = round(unnormalize(x, minval, maxval) / 1000.0, 2)
    ax.annotate(f'{f:.0f} us', xy=(x + xoffset, height), annotation_clip=False, fontsize=FONTSIZE, horizontalalignment='center', verticalalignment='center')
    ax.scatter(x, 0, color='black', s=MARKER_SIZE, clip_on=False, marker='X')

for p in ('FlexPRET', 'nrf52'):
    df = benchmark_to_dataframe(f'lf/{p}/Compute/noint', 100)

    print(df[(df.Threading == 'Multi-threaded')].after.mean())
    print(df[(df.Threading == 'Multi-threaded')].after.std())

    tscombined = combine_ts(df)
    minval = min(tscombined)
    maxval = max(tscombined)

    fig, ax = plt.subplots()

    sns.set_context('paper', font_scale=2)
    sns.histplot(df, x='after_norm', hue='Threading', multiple='stack', bins=50, ax=ax)

    ax.set_xticks([])
    ax.set_xlabel('')
    ax.set_xlim(left=0)

    ax.tick_params(axis='y', labelsize=.75*FONTSIZE)
    ax.set_ylabel('')
    if p == 'FlexPRET':
        ax.set_ylim(top=110)

    plt.legend(['Multi-Threaded', 'Single-Threaded'], fontsize=.75*FONTSIZE, loc='upper left')

    pts = (df[(df.Threading == 'Single-threaded')].after_norm.min(), \
           df[(df.Threading == 'Single-threaded')].after_norm.mean(), \
           df[(df.Threading == 'Single-threaded')].after_norm.max(), \
           df[(df.Threading == 'Multi-threaded')].after_norm.mean(), \
    )

    if p == 'nrf52':
        annotate(pts[0], ax, down=True)
        annotate(pts[1], ax, down=False)
        annotate(pts[2], ax, down=True)
        annotate(pts[3], ax, down=False)
    elif p == 'FlexPRET':
        annotate(pts[0], ax, down=True)
        annotate(pts[1], ax, down=False, xoffset=-0.1)
        annotate(pts[2], ax, down=False)
        annotate(pts[3], ax, down=True, xoffset=0.1)

    plt.show()
