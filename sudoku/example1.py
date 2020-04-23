import solvers
from solvers import *
import pandas as pd

# puzzle = '...1.5...14....67..8...24...63.7..1.9.......3.1..9.52...72...8..26....35...4.9...'
puzzle = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'

BruteForce(puzzle).solve_bf()
LimitedBruteForce(puzzle).solve_lbf()
Solve(puzzle).solve()


# sudoku_df = pd.DataFrame
#
# sudoku