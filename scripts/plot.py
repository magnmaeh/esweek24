import re
import argparse
import pandas
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

from scipy import stats
from pathlib import Path

PLATFORMS = ['FlexPRET', 'nrf52', 'RP2040', 'RPi']
LANGUAGES = ['C', 'lf']
LF_BENCHMARK_NAMES = ['Control', 'Work']

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--platforms', type=str, nargs='+', choices=PLATFORMS, default=PLATFORMS)
parser.add_argument('-b', '--benchmarks', type=str, nargs='+', choices=LANGUAGES, default=LANGUAGES)
parser.add_argument('-i', '--iterations', type=int, required=True)

args = parser.parse_args()

BENCHMARKS_C  = list((f'C/{p}/{i}' for i in ('int', 'noint') for p in args.platforms))
BENCHMARKS_LF = list((f'lf/{p}/{b}/int' for p in args.platforms for b in LF_BENCHMARK_NAMES))

HERE = Path(__file__).parent.resolve()

def line_to_numbers(line: str):
    return re.findall(r'\d+', line)

def file_to_lists(file, interrupts):
    idxs = list()
    ts1 = list()
    ts2 = list()
    ts3 = list()

    for line in file:
        if 'periodic' in line:
            print(line, interrupts)
            nperiodic_ints = int(re.findall(r'\d+', line)[0])
            if interrupts:
                assert (nperiodic_ints > 0)
            else:
                assert (nperiodic_ints == 0)
        elif 'sporadic' in line:
            print(line, interrupts)
            nsporadic_ints = int(re.findall(r'\d+', line)[0])
            if interrupts:
                assert (nsporadic_ints > 0)
            else:
                assert (nsporadic_ints == 0)
        if '[' in line:
            ret = line_to_numbers(line)
            idxs.append(ret[0])
            ts1.append(float(ret[1]))
            if len(ret) == 4:
                ts2.append(float(ret[2]))
                ts3.append(float(ret[3]))
            else:
                ts2 = None
                ts3 = None

    ts1.sort()
    if ts2:
        ts2.sort()
    if ts3:
        ts3.sort()

    return idxs, [ts1, ts2, ts3]

def benchmark_to_dataframe(benchmark, iterations):
    print(f'Processing {benchmark}')
    
    with open(str(HERE / '..' / 'results' / benchmark) + f'-it{iterations}.txt', 'r') as f:
        file = f.readlines()
    
    lang, platform, have_int = benchmark.split('/')
    _, timestamps = file_to_lists(file, have_int == 'int')
    return pandas.DataFrame({
        'platform': platform,
        'have_int': True if have_int == 'int' else False,
        'language': lang,
        'ts0': timestamps[0],
        'ts1': timestamps[1],
        'ts2': timestamps[2]
    })

def select_dataframes(dataframes, int: bool, lang: str, platforms: list[str] = args.platforms):
    ret = list()
    for d in dataframes:
        ret.append(d[(d.have_int == int) & (d.language == lang) & (d.platform.isin(platforms))])
    return pandas.concat(ret)

def filter_quantile(df, key):
    q_high = df[key].quantile(0.99)
    return df[(df[key] < q_high)]    

dataframes = list()
if 'C' in args.benchmarks:
    for b in BENCHMARKS_C:
        dataframes.append(
            benchmark_to_dataframe(b, args.iterations)
        )

if 'lf' in args.benchmarks:
    for lfb in BENCHMARKS_LF:
        dataframes.append(
            benchmark_to_dataframe(lfb, args.iterations)
        )

platforms_without_flexpret = args.platforms.copy()
platforms_without_flexpret.remove('FlexPRET')

platforms_without_flexpret_RP2040 = args.platforms.copy()
platforms_without_flexpret_RP2040.remove('FlexPRET')
platforms_without_flexpret_RP2040.remove('RP2040')

int_df                   = select_dataframes(dataframes, int=True, lang='C', platforms=platforms_without_flexpret)
int_df_flexpret          = select_dataframes(dataframes, int=True, lang='C', platforms=['FlexPRET'])
noint_df                 = select_dataframes(dataframes, int=False, lang='C', platforms=platforms_without_flexpret_RP2040)
noint_df_flexpret_RP2040 = select_dataframes(dataframes, int=False, lang='C', platforms=['FlexPRET', 'RP2040'])

int_df_lf                = select_dataframes(dataframes, int=True, lang='lf')

df = pandas.concat(dataframes)
print(df)

def dataframe_to_mean_stddev(dataframe) -> (float, float):
    return dataframe.ts0.mean(), dataframe.ts0.std()

def get_statistcs(df):
    stats = dict()
    for p in args.platforms:
        for i in [True, False]:
            d = df[(df.platform == p) & (df.have_int == i)]
            mean, stddev = dataframe_to_mean_stddev(d)
            print(f'{p} {i} {mean} {stddev}')
            stats[(p, i)] = (mean, stddev)
    return stats

stats = get_statistcs(df)
print(stats)

def normalize(df):
    for p in platforms_without_flexpret:
        minval = df[(df.platform == p)].ts0.min()
        maxval = df[(df.platform == p)].ts0.max()
        df.loc[(df.platform == p), 'ts0'] = (df[(df.platform == p)].ts0 - minval) / (maxval - minval)

if 'C' in args.benchmarks:
    for platform in args.platforms:
        print('{} (int)  : {:.2f} ± {:.2f} ns'.format(platform, stats[(platform, True)][0], stats[(platform, True)][1]))
        print('{} (noint): {:.2f} ± {:.2f} ns'.format(platform, stats[(platform, False)][0], stats[(platform, False)][1]))
        print('{} max    : {:.2f} ns'.format(platform, df[df.platform == platform].ts0.max()))

VERTIVAL_LINEWIDTH = 8
FONTSIZE = 30

################################################################################
# Plot first graph
################################################################################

if 'C' in args.benchmarks:
    normalize(int_df)
    #grid = sns.displot(data=int_df, x='ts0', hue='platform', kind='kde', fill=True, palette='tab10', legend=False, hue_norm=True, facet_kws={'legend_out': False})
    grid = sns.violinplot(data=int_df, x='platform', y='ts0', palette='tab10')
    #grid.ax.axvline(1.0, ymin=0, ymax=1, color='black', linewidth=VERTIVAL_LINEWIDTH, label='FlexPRET')

    #grid.add_legend(title='Platform', fontsize=FONTSIZE, labels=['RPi', 'RP2040', 'nrf52', 'FlexPRET'])
    #grid.set_xlabels('Execution time (ns)', fontsize=FONTSIZE)
    ##grid.ax.set_title('Execution time distribution with interrupts', fontsize=FONTSIZE)
#
    ##ymax = grid.ax.get_ylim()[1]
    #FlexPRET_std_dev = round(stats[('FlexPRET', True)][1], 2)
#
    #mean = 1.04 * stats[('FlexPRET', True)][0]

    #grid.ax.text(
    #    mean,
    #    0.8*ymax,
    #    f'FlexPRET std.dev.: {FlexPRET_std_dev} ns',
    #    fontsize=FONTSIZE
    #)
    plt.show()

################################################################################
# Plot second graph
################################################################################

if 'C' in args.benchmarks:
    grid = sns.displot(data=noint_df, x='ts0', hue='platform', kind='kde', fill=True, palette='tab10', legend=False, facet_kws={'legend_out': False})
    grid.ax.axvline(stats[('FlexPRET', False)][0], ymin=0, ymax=1, color='black', linewidth=VERTIVAL_LINEWIDTH, label='FlexPRET\n + RP2040')

    grid.add_legend(title='Platform', fontsize=FONTSIZE, labels=['RPi', 'nrf52', 'FlexPRET\n + RP2040'])
    grid.set_xlabels('Execution time (ns)', fontsize=FONTSIZE)
    grid.ax.set_title('Execution time distribution without interrupts', fontsize=FONTSIZE)

    ymax = grid.ax.get_ylim()[1]
    FlexPRET_std_dev = round(stats[('FlexPRET', True)][1], 2)
    RP2040_std_dev = round(stats[('RP2040', False)][1], 2)

    FlexPRET_mean = 1.003 * stats[('FlexPRET', False)][0]
    RP2040_mean = 1.003 * stats[('RP2040', False)][0]
    mean = (FlexPRET_mean + RP2040_mean) / 2.0

    grid.ax.text(
        mean,
        0.8*ymax,
        f'FlexPRET std.dev.: {FlexPRET_std_dev} ns',
        fontsize=FONTSIZE
    )
    grid.ax.text(
        mean,
        0.7*ymax,
        f'RP2040  std.dev.: {RP2040_std_dev} ns',
        fontsize=FONTSIZE
    )

    plt.show()

################################################################################
# Plot LF
################################################################################

if 'lf' in args.benchmarks:
    grid = sns.displot(data=int_df_lf, x='ts0', hue='platform', kind='kde', fill=True, palette='tab10', legend=False, facet_kws={'legend_out': False})

    plt.show()