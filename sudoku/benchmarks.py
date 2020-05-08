# %%
import sudoku_solving_algorithms as solvers
import pandas as pd

""" 
Here we'll run several benchmarks and save the results as csv files for data analysis purposes.

Here's the source of our benchmarks:

https://github.com/t-dillon/tdoku/tree/master/benchmarks

"""

filepath = r'D:/code/github/games/sudoku/benchmarks/'


def analyze(benchmark_set, output_filename):
    """
    This function will take a benchmark set and solve it with my three methods.
    It will also give some statistics.
    It will save this as a csv with the given name.
    """

    benchmark_result_df = pd.DataFrame(columns=[
        'description',
        'input',
        'output',
        # 'bf_time',
        # 'lbf_time',
        'solve_time',
        # 'bf_loops',
        # 'lbf_loops',
        'strat_loops',
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
        # bf = solvers.BruteForce(puzzle)
        # bf.solve()

        # lbf = solvers.LimitedBruteForce(puzzle)
        # lbf.solve()

        strat = solvers.StrategySolve(puzzle)
        strat.solve()

        benchmark_result_df = benchmark_result_df.append(pd.Series([
            strat.sudoku.description,
            strat.sudoku.input,
            strat.sudoku.output,
            # bf.total_time,
            # lbf.total_time,
            strat.total_time,
            # bf.count,
            # lbf.count,
            strat.count,
            strat.sudoku.strategy_counts['ns'],
            strat.sudoku.strategy_counts['hs'],
            strat.sudoku.strategy_counts['nd'],
            strat.sudoku.strategy_counts['hd'],
            strat.sudoku.strategy_counts['nt'],
            strat.sudoku.strategy_counts['ht'],
            strat.sudoku.strategy_counts['nq'],
            strat.sudoku.strategy_counts['hq'],
            strat.sudoku.strategy_counts['r']], index=benchmark_result_df.columns),
            ignore_index=True)

        print(f'''{output_filename}: puzzle #{i}: time = {strat.total_time}, {strat.total_time}, {strat.total_time}''')
    benchmark_result_df.to_csv(f'{filepath}{output_filename}.csv', index=False)


# Benchmark 0: Freeman custom benchmark, shows off various strats
# freeman_benchmark_set = pd.read_csv(f'{filepath}freeman_benchmark_set')

# Benchmark 1: Kaggle (1 Million, Very Easy)
kaggle_benchmark_set = pd.read_csv(f'{filepath}kaggle_benchmark_set.csv').iloc[:100, 0]

# Benchmark 2: Minimum Clues (49158 , Easy)
minclue_benchmark_set = pd.read_csv(f'{filepath}sudoku17.txt').iloc[:50, 0]

# Benchmark 3: magictour_top1465 (1465, moderately hard)
magictour_benchmark_set = pd.read_csv(f'{filepath}top1465.txt').iloc[:, 0]

# Benchmark 4: forum_hardest_1910 (375, possibly hardest ever)
hardest_benchmark_set = pd.read_csv(f'{filepath}HardestDatabase110626.txt')
hardest_benchmark_set = hardest_benchmark_set['sudoku']

# %%

benchmarks = [
    # (freeman_benchmark_set, 'freeman_results'),
    # (kaggle_benchmark_set, 'kaggle_results'),
    (minclue_benchmark_set, 'minclue_results_50'),
    # (magictour_benchmark_set, 'magictour_results'),
    # (hardest_benchmark_set, 'hardest_benchmark_results')
]

for bench_set, filename in benchmarks:
    analyze(bench_set, filename)
    print(f'{filename} complete')
