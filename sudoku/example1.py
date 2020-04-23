import solvers
from solvers import *

puzzle = '...1.5...14....67..8...24...63.7..1.9.......3.1..9.52...72...8..26....35...4.9...'

BruteForce(puzzle).solve_bf()
LimitedBruteForce(puzzle).solve_lbf()

# print(BruteForce(puzzle).blanks)
# print(LimitedBruteForce(puzzle).blanks)