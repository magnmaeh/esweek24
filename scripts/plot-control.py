import re
import argparse
import pandas
import seaborn as sns
import matplotlib.pyplot as plt
import statistics

from pathlib import Path

PLATFORMS = ['FlexPRET', 'RP2040', 'nrf52', 'RPi']
LANGUAGES = ['C', 'lf']
LF_BENCHMARK_NAMES = ['Control',]

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--platforms', type=str, nargs='+', choices=PLATFORMS, default=PLATFORMS)
parser.add_argument('-l', '--languages', type=str, nargs='+', choices=LANGUAGES, default=LANGUAGES)
parser.add_argument('-i', '--iterations', type=int, required=True)

args = parser.parse_args()

BENCHMARKS_C  = list((f'C/{p}/{i}' for i in ('noint', 'int') for p in args.platforms))
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
            nperiodic_ints = int(re.findall(r'\d+', line)[0])
            if interrupts:
                assert (nperiodic_ints > 0)
            else:
                assert (nperiodic_ints == 0)
        elif 'sporadic' in line:
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

def unnormalize(x, minval, maxval):
    return x * (maxval - minval) + minval

def normalize(x, minval, maxval):
    return (x - minval) / (maxval - minval)

def normalize_list(lst, maxval, minval):
    if type(lst) == type(None):
        return None

    return [normalize(x, minval, maxval) for x in lst]

def benchmark_to_dataframe(benchmark, iterations, lang):
    print(f'Processing {benchmark}')
    
    with open(str(HERE / '..' / 'results' / benchmark) + f'-it{iterations}.txt', 'r') as f:
        file = f.readlines()
    
    if lang == 'lf':
        lang, platform, bench, have_int = benchmark.split('/')
    elif lang == 'C':
        lang, platform, have_int = benchmark.split('/')
    else:
        print('Bad language')
        exit(1)

    _, timestamps = file_to_lists(file, have_int == 'int')

    if timestamps[1] is not None and timestamps[2] is not None:
        timestamps[2] = [x + 5e6 for x in timestamps[2]]
        timestamps_combined = timestamps[0] + timestamps[1] + timestamps[2]
    else:
        timestamps_combined = timestamps[0]
    maxval = max(timestamps_combined)
    minval = min(timestamps_combined)
    return pandas.DataFrame({
        'platform': platform,
        'have_int': True if have_int == 'int' else False,
        'language': lang,
        'benchmark': bench if lang == 'lf' else None,
        'ts0': [statistics.mean(timestamps[0])] + timestamps[0] + [statistics.mean(timestamps[0])],
        'ts1': [statistics.mean(timestamps[1])] + timestamps[1] + [statistics.mean(timestamps[1])],
        'ts2': [statistics.mean(timestamps[2])] + timestamps[2] + [statistics.mean(timestamps[2])],
        'ts0_norm': [0.0] + normalize_list(timestamps[0], max(timestamps[0]), min(timestamps[0])) + [1.0],
        'ts1_norm': [0.0] + normalize_list(timestamps[1], max(timestamps[1]), min(timestamps[1])) + [1.0],
        'ts2_norm': [0.0] + normalize_list(timestamps[2], max(timestamps[2]), min(timestamps[2])) + [1.0],
        'ts0_common_norm': [0.0] + normalize_list(timestamps[0], maxval, minval) + [1.0],
        'ts1_common_norm': [0.0] + normalize_list(timestamps[1], maxval, minval) + [1.0],
        'ts2_common_norm': [0.0] + normalize_list(timestamps[2], maxval, minval) + [1.0]
    })

def select_dataframes(d, int: bool, lang: str, benchmark: str = None, platforms: list[str] = args.platforms):
    ret = list()
    for d in dataframes:
        if benchmark is not None:
            ret.append(d[(d.have_int == int) & (d.language == lang) & (d.platform.isin(platforms)) & (d.benchmark == benchmark)])
        else:
            ret.append(d[(d.have_int == int) & (d.language == lang) & (d.platform.isin(platforms))])
    return pandas.concat(ret)

def filter_quantile(df, key):
    q_high = df[key].quantile(0.99)
    return df[(df[key] < q_high)]    

dataframes = list()
if 'C' in args.languages:
    for b in BENCHMARKS_C:
        dataframes.append(
            benchmark_to_dataframe(b, args.iterations, 'C')
        )

if 'lf' in args.languages:
    for lfb in BENCHMARKS_LF:
        dataframes.append(
            benchmark_to_dataframe(lfb, args.iterations, 'lf')
        )



def dataframe_to_mean_stddev(dataframe) -> (float, float):
    return dataframe.ts0.mean(), dataframe.ts0.std()

def get_statistcs(dataframe):
    stats = dict()
    for p in args.platforms:
        for i in [True, False]:
            d = dataframe[(dataframe.platform == p) & (dataframe.have_int == i)]
            mean, stddev = dataframe_to_mean_stddev(d)
            stats[(p, i)] = (mean, stddev)
    return stats

def print_stats(dataframe):
    for platform in args.platforms:
        print('{} min ts0: {:.2f} ns'.format(platform, df[df.platform == platform].ts0.min()))
        print('{} min ts1: {:.2f} ns'.format(platform, df[df.platform == platform].ts1.min()))
        print('{} min ts2: {:.2f} ns'.format(platform, df[df.platform == platform].ts2.min()))

        print('{} mean ts0: {:.2f} ns'.format(platform, df[df.platform == platform].ts0.mean()))
        print('{} mean ts1: {:.2f} ns'.format(platform, df[df.platform == platform].ts1.mean()))
        print('{} mean ts2: {:.2f} ns'.format(platform, df[df.platform == platform].ts2.mean()))

        print('{} max ts0: {:.2f} ns'.format(platform, df[df.platform == platform].ts0.max()))
        print('{} max ts1: {:.2f} ns'.format(platform, df[df.platform == platform].ts1.max()))
        print('{} max ts2: {:.2f} ns'.format(platform, df[df.platform == platform].ts2.max()))

int_df                   = select_dataframes(dataframes, int=True, lang='C', platforms=args.platforms)
noint_df                 = select_dataframes(dataframes, int=False, lang='C', platforms=args.platforms)
lf_df                    = select_dataframes(dataframes, int=True, lang='lf', benchmark='Control', platforms=args.platforms)

df = pandas.concat(dataframes)

FONTSIZE = 56

def combine_ts(df):
    return df.ts0.to_list() + df.ts1.to_list() + df.ts2.to_list()

if 'lf' in args.languages:
    print_stats(lf_df)

    VERTIVAL_TEXT_HEIGHT = {
        'FlexPRET': 25,
        'RP2040': 25,
        'nrf52': 20,
        'RPi': 25,
    }
    NBINS = {
        'FlexPRET': 100,
        'RP2040': 100,
        'nrf52': 100,
        'RPi': 100,
    }
    MARKER_SIZE = 800

    sns.set_context('paper', font_scale=2)

    figlist = list()
    for p in args.platforms:
        f, axes = plt.subplots(ncols=2, nrows=2, sharex=False, sharey=False, gridspec_kw={'hspace': .2, 'wspace': .3, 'height_ratios': [1, 4], 'width_ratios': [2.5, 1]})

        for ax in axes.flat:
            sns.histplot(lf_df[lf_df.platform == p], x='ts0_common_norm', bins=NBINS[p], color='r', ax=ax)
            sns.histplot(lf_df[lf_df.platform == p], x='ts1_common_norm', bins=NBINS[p], color='g', ax=ax)
            sns.histplot(lf_df[lf_df.platform == p], x='ts2_common_norm', bins=NBINS[p], color='b', ax=ax)

        if p == 'nrf52':
            print(lf_df[lf_df.platform == 'nrf52'].ts0)
            print(lf_df[lf_df.platform == 'nrf52'].ts2)

        ((ax_top_left, ax_top_right), (ax_btm_left, ax_btm_right)) = axes

        tscombined = combine_ts(lf_df[lf_df.platform == p])
        minval = min(tscombined)
        maxval = max(tscombined)

        minval_ts1 = min(lf_df[lf_df.platform == p].ts1.to_list())
        maxval_ts1 = max(lf_df[lf_df.platform == p].ts1.to_list())

        maxval_ts0 = max(lf_df[lf_df.platform == p].ts0.to_list())

        ########################################################################
        # Create vertical and horizontal breaks
        ########################################################################
        BREAK_YLIM_UPPER = {
            'FlexPRET': 500,
            'RP2040': 500,
            'nrf52': 500,
            'RPi': 400,
        }
        BREAK_YLIM_LOWER = {
            'FlexPRET': 200,
            'RP2040': 200,
            'nrf52': 150,
            'RPi': 200,
        }
        BREAK_XLIM_RIGHT = {
            'FlexPRET': .9,
            'RP2040': .7,
            'nrf52': .7,
            'RPi': .85,
        }
        BREAK_XLIM_LEFT = normalize(maxval_ts1, minval, maxval)

        # Set vertical limits, making the vertical break
        ax_top_left.set_ylim(bottom=BREAK_YLIM_UPPER[p])
        ax_top_right.set_ylim(bottom=BREAK_YLIM_UPPER[p])
        ax_btm_left.set_ylim(0, BREAK_YLIM_LOWER[p])
        ax_btm_right.set_ylim(0, BREAK_YLIM_LOWER[p])

        # Set horizontal limits, making the horizontal break
        ax_btm_left.set_xlim(right=BREAK_XLIM_LEFT)
        ax_top_left.set_xlim(right=BREAK_XLIM_LEFT)
        ax_btm_right.set_xlim(BREAK_XLIM_RIGHT[p], 1)
        ax_top_right.set_xlim(BREAK_XLIM_RIGHT[p], 1)

        ########################################################################
        # Draw diagonal lines in axes
        ########################################################################

        d = .025  # how big to make the diagonal lines in axes coordinates
        # arguments to pass to plot, just so we don't keep repeating them
        kwargs = dict(transform=ax_top_left.transAxes, color='k', clip_on=False)
        ax_top_left.plot((-d, +d), (-4*d, +4*d), **kwargs)        # vertical top diagonal

        kwargs.update(transform=ax_btm_left.transAxes)
        ax_btm_left.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # vertical btm diagonal

        kwargs.update(transform=ax_btm_right.transAxes)
        ax_btm_right.plot((-d, +d), (-d, +d), **kwargs)  # horizontal right diagonal
        
        ########################################################################
        # Remove redundant lines and labels
        ########################################################################

        # Configure plot
        sns.despine(ax=ax_btm_left)
        sns.despine(ax=ax_btm_right, left=True)
        sns.despine(ax=ax_top_left, bottom=True)
        sns.despine(ax=ax_top_right, bottom=True, left=True)

        ax_top_right.set_xticks([])
        ax_top_right.set_yticks([])
        ax_btm_right.set_yticks([])
        
        for ax in axes.flat:
            ax.set_xlabel('')
            ax.set_ylabel('')
            ax.set_xticks([])

        ax_top_left.tick_params(axis='y', labelsize=.75*FONTSIZE)
        ax_btm_left.tick_params(axis='y', labelsize=.75*FONTSIZE)
        
        ########################################################################
        # Annotate key points
        ########################################################################

        def annotate(x, ax, down=True, color='black'):
            height = -VERTIVAL_TEXT_HEIGHT[p] if down else VERTIVAL_TEXT_HEIGHT[p]
            f = round(unnormalize(x, minval, maxval) / 1000.0, 2)
            ax.annotate(f'{f:.0f} us', xy=(x, height), annotation_clip=False, fontsize=FONTSIZE, horizontalalignment='center', verticalalignment='center')
            ax.scatter(x, 0, color=color, s=MARKER_SIZE, clip_on=False, marker='X')

        annotate(normalize(maxval_ts0, minval, maxval), ax_btm_left)
        if p == 'RPi':
            annotate(BREAK_XLIM_LEFT, ax_btm_left, down=False)
        else:
            annotate(BREAK_XLIM_LEFT, ax_btm_left, down=True)
        annotate(1, ax_btm_right)

        TXTPOS_X = {
            'FlexPRET': .3,
            'RP2040': .25,
            'nrf52': .3,
            'RPi': .3,
        }
        
        if p == 'nrf52':
            ax_top_left.text(TXTPOS_X[p], .6*args.iterations, 'nRF52', fontsize=1.2*FONTSIZE, horizontalalignment='center', verticalalignment='center')
        else:
            ax_top_left.text(TXTPOS_X[p], .6*args.iterations, p, fontsize=1.2*FONTSIZE, horizontalalignment='center', verticalalignment='center')

        plt.show()
        f.savefig(f'figs/lf_{p}.png')
