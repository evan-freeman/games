# %%
import sudoku_solving_algorithms as solvers
import pandas as pd

""" 
Here we'll run several benchmarks and save the results as csv files for data analysis purposes.

Here's the source of our benchmarks:

https://github.com/t-dillon/tdoku/tree/master/benchmarks

"""

filepath = r'D:/code/github/games/sudoku/benchmarks/'


def benchmark(benchmark_set, output_filename, description_set=()):
    """
    This function will take a benchmark set and solve it with my three methods.
    It will also give some statistics.
    It will save this as a csv with the given name.
    """

    benchmark_result_df = pd.DataFrame(columns=[
        'description',
        'input',
        'output',
        'bf_time',
        'lbf_time',
        'strat_time',
        'bf_loops',
        'lbf_loops',
        'strat_lbf_loops',
        'ns_count',
        'hs_count',
        'nd_count',
        'hd_count',
        'nt_count',
        'ht_count',
        'nq_count',
        'hq_count',
        'r_count'])

    for i, puzzle in enumerate(benchmark_set, 1):
        try:
            if description_set.any():
                output = solvers.analyse(puzzle, description_set[i - 1])
        except:
            output = solvers.analyse(puzzle)

        benchmark_result_df = benchmark_result_df.append(
            pd.Series(output, index=benchmark_result_df.columns), ignore_index=True)

        print(
            f'''{output_filename}: puzzle #{i}: time = {output['bf_time']}, {output['lbf_time']}, {output['strat_time']}''')

    benchmark_result_df.to_csv(f'{filepath}{output_filename}.csv', index=False)


# Benchmark 0: Freeman custom benchmark, shows off various strats

freeman = pd.read_csv(f'{filepath}freeman_benchmark_set.txt', header=1)
freeman_benchmark_set = freeman.iloc[:, 0]
freeman_description_set = freeman.iloc[:, 1]

# Benchmark 1: Kaggle (1 Million, Very Easy)
kaggle_benchmark_set = pd.read_csv(f'{filepath}kaggle_benchmark_set.csv').iloc[:, 0]
kaggle_description_set = ()

# Benchmark 2: Minimum Clues (49158 , Easy)
minclue_benchmark_set = pd.read_csv(f'{filepath}sudoku17.txt').iloc[:, 0]
minclue_description_set = ()

# Benchmark 3: magictour_top1465 (1465, moderately hard)
magictour_benchmark_set = pd.read_csv(f'{filepath}top1465.txt').iloc[:, 0]
magictour_description_set = ()

# Benchmark 4: forum_hardest_1910 (375, possibly hardest ever)
hardest_benchmark_set = pd.read_csv(f'{filepath}HardestDatabase110626.txt')
hardest_benchmark_set = hardest_benchmark_set['sudoku']
hardest_description_set = ()

# %%

benchmarks = [
    # (freeman_benchmark_set, 'freeman_results', freeman_description_set),
    # (kaggle_benchmark_set, 'kaggle_results', kaggle_description_set),
    # (minclue_benchmark_set, 'minclue_results_50', minclue_description_set),
    # (magictour_benchmark_set, 'magictour_results', magictour_description_set),
    (hardest_benchmark_set, 'hardest_results', hardest_description_set)
]


for bench_set, filename, desc_set in benchmarks:
    benchmark(bench_set, filename, desc_set)
    print(f'{filename} complete')
