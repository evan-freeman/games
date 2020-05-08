"""
Here are all my Sudoku solving algorithms.
"""

import time
import itertools as it
import numpy as np


class Cell:
    """ This is the Cell object we will use to represent a given cell, with all of the information about it.

    TODO Find a mathematical solution to identifying the box number of a given cell, not a handcrafted dict.

    """

    def __init__(self, x, y, value=0, n=9):
        self.x = x
        self.y = y
        self.value = value
        if self.value == 0:
            self.poss = list(range(1, n + 1))
        else:
            self.poss = []
        self.column = self.x
        self.row = self.y

        box_dict = {(0, 0): 0, (0, 3): 1, (0, 6): 2,
                    (3, 0): 3, (3, 3): 4, (3, 6): 5,
                    (6, 0): 6, (6, 3): 7, (6, 6): 8}
        self.box = box_dict[self.x // 3 * 3, self.y // 3 * 3]


# =============================================================================
# STATIC STRATEGY HELPER FUNCTIONS
# =============================================================================


class Grid:
    """This is the Grid object we will use to represent a Sudoku.
    It has a lot of attributes and methods. It basically stores all information about the Sudoku,
    along with all the techniques needed to solve and analyze it."""

    @staticmethod
    def int_except(x: str) -> int:
        """ Returns x as an int if possible, else returns 0. Used for parsing the input puzzle.

        Args:
            x (str): One element of the input, presumably a string,
                        but it could also be an 81 character int that represents the puzzle.

        Returns:
            int: The value of that cell as an int, or 0, which represents unknown.
        """
        try:
            return int(x)
        except:
            return 0

    def generate_region_list(self, region: str) -> list:
        """This function generates a list of elements containing the cell objects that belong to a given region
        (column, row, or box). We'll use this in our __init__, which is why we've defined it here.

        Args:
            region: A string that denotes the desired region - columns, rows or boxes

        Returns:
            list: This is a list of 9 elements, each of which contains the 9 cells that belong to a particular element.
        """

        return [[cell for cell in self.cells.values() if getattr(cell, region) == i]
                for i in range(self.n)]

    def generate_blank_region_list(self, region: str) -> list:
        """This function generates a list of elements containing the BLANK cell objects that belong to a given region.
        We'll use this in our __init__, which is why we've defined it here.

        Args:
            region: A string that denotes the desired region - columns, rows or boxes

        Returns:
            list: This is a list of 9 elements,
            each of which contains the BLANK cells that belong to a particular region. The lists may be empty.
        """

        return [[cell for cell in self.cells.values() if getattr(cell, region) == i and
                 cell.value == 0] for i in range(self.n)]

    def __init__(self, puzzle, description='N/A'):
        """

        """

        self.description = description
        self.list = [self.int_except(x) for x in puzzle]
        self.input = ''.join(str(x) for x in self.list)
        self.length = len(puzzle)
        self.n = int(self.length ** .5)
        self.arr = np.array(self.list).reshape((self.n, self.n))
        # Note that we must reverse the order of the coordinates in the array, because it uses matrix coordinates
        self.cells = {(x, y): Cell(x, y, self.arr[y, x], self.n) for y in range(self.n) for x in range(self.n)}
        self.columns = self.generate_region_list('column')
        self.rows = self.generate_region_list('row')
        self.boxes = self.generate_region_list('box')
        self.blanks = [cell for cell in self.cells.values() if cell.value == 0]
        self.column_blanks = self.generate_blank_region_list('column')
        self.row_blanks = self.generate_blank_region_list('row')
        self.box_blanks = self.generate_blank_region_list('box')
        self.region_list = ['column', 'row', 'box']
        self.strategy_counts = {
            'ns': 0,
            'hs': 0,
            'nd': 0,
            'hd': 0,
            'nt': 0,
            'ht': 0,
            'nq': 0,
            'hq': 0,
            'r': 0
        }
        self.as_string = ''
        self.as_string_list = []

    @property
    def total_strategy_count(self):
        return sum(count for count in self.strategy_counts.values())

    # =============================================================================
    # DISPLAY FUNCTIONS
    # =============================================================================

    def stringify(self):
        """This function takes the puzzle in it's current state and converts it back into an 81 character string."""

        output = [self.cells[(i, j)].value for j in range(self.n) for i in range(self.n)]
        self.as_string = ''.join(str(x) for x in output)
        return self.as_string

    def display(self):
        """
        Displays the puzzle as a single 81 character string.
        Currently I'm working with the display as a string because I don't know efficient ways to concatenate ints.
        """

        self.stringify()
        print(self.as_string)

    def display_grid(self):
        """
        Displays the puzzle as a 9x9 grid of strings.

        It would be nice to use numpy reshape functionality, but then I'd have to concatenate, which
        I think would require going back and forth between strings and ints, as I don't know a way to
        concat ints. But I might be wrong about that.
        """

        self.stringify()
        self.as_string_list = [self.as_string[i:i + self.n] for i in range(0, self.length, self.n)]
        for row in self.as_string_list:
            print(row)

    @property
    def output(self):
        return self.stringify()

    # =============================================================================
    # STRATEGY HELPER FUNCTIONS
    # =============================================================================

    @staticmethod
    def intersect(cell1, cell2):
        """ Returns a boolean for whether two cells intersect,
        i.e. they are in the same row, column, or box."""

        return cell1.column == cell2.column or cell1.row == cell2.row or cell1.box == cell2.box

    def intersecting_values(self, cell):
        """ Returns a list of values that intersect a given cell,
        i.e. the values that appear in the same column, row or box.
        """

        return [other_cell.value for other_cell in self.cells.values() if self.intersect(cell, other_cell)]

    def update_poss(self):
        """
        Updates all lists of possibilities for blank cells with new information in the sudoku.
        """

        for cell in self.blanks:
            for poss in cell.poss[:]:  # Here we iterate over a copy, so we don't have issues with modifying inplace.
                if poss in self.intersecting_values(cell):
                    cell.poss.remove(poss)

    @staticmethod
    def same_region(cell1, cell2, region):
        """ Returns a boolean for whether two cells are in the same element of the region given,
        i.e. same column, row, or box."""
        return getattr(cell1, region) == getattr(cell2, region)

    def intersecting_blank_cells(self, cell, region):
        """ Returns a list of cells which intersect the given cell, in the given region, OTHER THAN the given cell.
        i.e. They are in the same row, column, or box."""

        return [other_cell for other_cell in self.blanks if
                other_cell != cell and self.same_region(cell, other_cell, region)]

    def generate_other_blanks(self, cell):
        """Returns blanks in OTHER cells in the same column, row, and box, as a list of lists."""

        return [self.intersecting_blank_cells(cell, region) for region in self.region_list]

    @staticmethod
    def check_no_dupes(list_of_cells):
        """
        Returns true if a given list of cells has no duplicate values, else false.
        """

        # First, remove any 0s, which are placeholders for unknowns
        clean_list = [cell.value for cell in list_of_cells if cell.value != 0]

        # Now check for duplicates. Return True if there were no duplicates, else False.
        return len(clean_list) == len(set(clean_list))

    def check_consistency(self, cell):
        """ Checks whether a cell is a member of a contradictory column, row, or box. i.e there is a repeated digit."""
        return (
                self.check_no_dupes(self.columns[cell.column]) and
                self.check_no_dupes(self.rows[cell.row]) and
                self.check_no_dupes(self.boxes[cell.box])
        )

    @staticmethod
    def extract_possibilities(list_of_cells):
        """ Returns a set of all possibilities on a given list of cells."""
        return set(poss for cell in list_of_cells for poss in cell.poss)

    def check_for_naked_set(self, element, n):
        """Returns a naked set of size n in a given region, if one exists.
        If not, returns an empty list, which evaluates to False in Python.
        Also return the """
        all_poss = self.extract_possibilities(element)
        for potential_naked_set in it.combinations(all_poss, n):
            potential_naked_cells = [cell for cell in element if set(cell.poss).issubset(set(potential_naked_set))]
            if len(potential_naked_cells) == n:
                return potential_naked_set, potential_naked_cells
        return [], []

    def remove_from_other_cells(self, unchanged_cells, set_to_remove, element, n):
        """ This function removes a set of numbers from the possibilities of cells in a given element.
        It also counts any progress that is made.

        """
        naked_count_dict = {2: 'nd', 3: 'nt', 4: 'nq', 5: 'r'}

        to_check = [cell for cell in element if
                    cell not in unchanged_cells]  # Only check the OTHER members of the element
        for cell in to_check:
            for i, poss in enumerate(cell.poss):  # We're modifying inplace, but it's ok because if that happens we
                if poss in set_to_remove:  # return right away.
                    del cell.poss[i]
                    self.strategy_counts[naked_count_dict[n]] += 1
                    return True
        return False

    def check_for_hidden_set(self, element, n):
        all_poss = self.extract_possibilities(element)
        for potential_hidden_set in it.combinations(all_poss, n):
            potential_hidden_cells = [cell for cell in element if
                                      any([poss in cell.poss for poss in potential_hidden_set])]
            if len(potential_hidden_cells) == n:
                return potential_hidden_cells, potential_hidden_set
        return [], []

    def reduce_cells(self, hidden_cells, hidden_set, n):
        """ This function reduces a set of cells to only the possibilities they contain from a given set of numbers.


        Returns:

        """

        hidden_count_dict = {2: 'hd', 3: 'ht', 4: 'hq'}

        for cell in hidden_cells:
            for poss in cell.poss:
                if poss not in hidden_set:
                    cell.poss.remove(poss)
                    self.strategy_counts[hidden_count_dict[n]] += 1
                    return True
        return False

    @staticmethod
    def extract_region_numbers(cells, region):
        """ Extracts the region (either column, row, or box) numbers that appear among a list of cells."""

        return set(getattr(cell, region) for cell in cells)

    def remove_from_blank_lists_and_clear_possibilities(self, cell: object):
        """ Takes in a cell who's value has just been set because of naked or hidden single, and
        removes it from the following lists: self.blanks, self.column_blanks, self.row_blanks, self.box_blanks.
        Then clears the possibilities of that cell.

        Args:
            cell: Cell object that has just had it's value set, and needs to be cleaned up."""
        self.blanks.remove(cell)
        self.column_blanks[cell.column].remove(cell)
        self.row_blanks[cell.row].remove(cell)
        self.box_blanks[cell.box].remove(cell)
        cell.poss = []

    # =============================================================================
    # STRATEGY FUNCTIONS
    # =============================================================================

    def naked_single(self):
        """
        Fill in a blank if there is only a single possibility.
        """
        self.update_poss()
        for cell in self.blanks:
            if len(cell.poss) == 1:  # Check whether there is a single possibility in a given blank cell
                cell.value = cell.poss[0]  # If so, update that cell.
                self.remove_from_blank_lists_and_clear_possibilities(cell)
                self.strategy_counts['ns'] += 1
                return True  # Note that progress has been made this loop
        return False

    def hidden_single(self):
        """
        Fill in when there is only one remaining place for a number in a row, column, or box.
        # TODO rewrite this strategy to iterate over each number 1-9 instead of each cell???
        # Possible speed / readability improvements
        """

        self.update_poss()
        for cell in self.blanks:
            # Generate the subset of blanks that are in the same column, row, or box as our current blank
            blank_column, blank_row, blank_box = self.generate_other_blanks(cell)

            # Extract the possible numbers from the intersecting regions
            other_column_poss = self.extract_possibilities(blank_column)
            other_row_poss = self.extract_possibilities(blank_row)
            other_box_poss = self.extract_possibilities(blank_box)

            # If one of the possibilities is the only occurrence in a given region, fill it in,
            # and remove that cell from blanks list
            for poss in cell.poss:
                if poss not in other_column_poss or poss not in other_row_poss or poss not in other_box_poss:
                    cell.value = poss
                    self.remove_from_blank_lists_and_clear_possibilities(cell)
                    self.strategy_counts['hs'] += 1
                    return True
        return False

    def general_naked(self, n: int) -> bool:
        """ Performs the logic of naked double, or triple, or quad for a given region.

        Logic - Check whether there is a set of n numbers that are the only

        Args:
            n (int): Size of naked set to search for (either 2, 3, or 4).

        Returns:
            bool: True if this technique yielded progress in the puzzle, else false.
        """
        for region in ('column_blanks', 'row_blanks', 'box_blanks'):
            for element in getattr(self, region):
                naked_set, naked_cells = self.check_for_naked_set(element, n)
                if naked_cells:
                    if self.remove_from_other_cells(naked_cells, naked_set, element, n):
                        return True
        return False

    def general_hidden(self, n):
        """This will execute a hidden pair, triple, or quad for a given region"""
        for region in ('column_blanks', 'row_blanks', 'box_blanks'):
            for element in getattr(self, region):
                hidden_cells, hidden_set = self.check_for_hidden_set(element, n)
                if hidden_cells:
                    if self.reduce_cells(hidden_cells, hidden_set, n):
                        return True
        return False

    def naked_double(self):
        return self.general_naked(2)

    def naked_triple(self):
        return self.general_naked(3)

    def naked_quad(self):
        return self.general_naked(4)

    def hidden_double(self):
        return self.general_hidden(2)

    def hidden_triple(self):
        return self.general_hidden(3)

    def hidden_quad(self):
        return self.general_hidden(4)

    def check_for_intersection(self, element, region, region_blanks):
        """ Checks whether there is a possible number in a given element, such that all occurrences of that number
        intersect another element"""

        other_regions = [reg for reg in ('column', 'row', 'box') if reg != region]

        for poss in range(1, 10):
            cells_with_poss = [cell for cell in element if poss in cell.poss]
            region_nums = {reg: self.extract_region_numbers(cells_with_poss, reg) for
                           reg in other_regions}
            for reg in region_nums:
                if len(region_nums[reg]) == 1:
                    return cells_with_poss, [poss], getattr(self, region_blanks)[list(region_nums[reg])[0]]
        return [], [], []

    # TODO Fix Reduction!!!!
    def reduction(self):
        for region_blanks, region in (('column_blanks', 'column'), ('row_blanks', 'row'), ('box_blanks', 'box')):
            for element in getattr(self, region_blanks):
                intersecting_cells, intersecting_set, intersecting_element = self.check_for_intersection(element, region, region_blanks)
                if intersecting_cells:
                    if self.remove_from_other_cells(intersecting_cells, intersecting_set, intersecting_element, 5):
                        return True
        return False


# =============================================================================
# SOLVERS
# =============================================================================


class Solver:
    """ This is a class of general attributes and methods for my 3 Sudoku Solvers"""

    def __init__(self, puzzle):
        self.sudoku = Grid(puzzle)
        self.count = 0
        self.type = 'None'
        self.start_time = 0
        self.total_time = 0

    def begin_timing(self):
        self.start_time = time.time()

    def end_timing(self):
        self.total_time = time.time() - self.start_time

    def display_all(self):
        pass

    def general_brute_force(self, use_poss: bool = True):
        """
        This is the general brute force function, which will iterate back and forth through the blanks
            in the puzzle until it finds a non-contradictory set of values.

        The use_poss parameter decides whether we will brute force over 1-9 in each blank, or just over the
            possibilities in that cell. This will be set to False for BruteForce, but True for LimitedBruteForce and
            StrategySolve.
        """

        # If we're going to use information about possibilities, let's first update that information.
        if use_poss:
            self.sudoku.update_poss()

        i = 0
        while i != len(self.sudoku.blanks):
            self.count += 1
            blank = self.sudoku.blanks[i]

            # Scenario 1: The blank's value is 0. That means we should try the first possibility.
            if blank.value == 0:
                blank.value = blank.poss[0]

            # Scenario 2: The blank's value is the final possibility. So we've already tried all the possibilities.
            # So we need to clear it out and step back. Also we skip the rest of the loop,
            # because we don't need to check for consistency. In fact, it would be bad to check for consistency,
            # as we are guaranteed to trivially be consistent. This would lead to stepping forward,
            # canceling out our step back, and ending up in an infinite loop.
            elif blank.value == blank.poss[-1]:
                blank.value = 0
                i -= 1
                continue

            # Scenario 3: The blank's value is some other non-last possibility. So we step forward by one.
            else:
                blank.value = blank.poss[blank.poss.index(blank.value) + 1]

            # Now we check for consistency. If consistent, step forward. Else run through this same spot again.
            if self.sudoku.check_consistency(blank):
                i += 1


class BruteForce(Solver):
    """
    Here is a class of solver that uses full brute force. So we don't even limit our candidates for brute force,
    we just go numerically through them all.
    """

    def __init__(self, puzzle):
        super().__init__(puzzle)
        self.type = 'BruteForce'

    def solve(self):
        self.begin_timing()
        self.general_brute_force(False)
        self.end_timing()


class LimitedBruteForce(Solver):
    """This class uses the same logic as brute force, but first reduces the possible candidates to brute force over."""

    def __init__(self, puzzle):
        super().__init__(puzzle)
        self.type = 'LimitedBruteForce'

    def solve(self):
        self.begin_timing()
        self.general_brute_force()
        self.end_timing()


class StrategySolve(Solver):
    """This solver applies the 9 strategies I've programmed above,
    then finishes with limited brute force if necessary"""

    def __init__(self, puzzle):
        super().__init__(puzzle)
        self.type = 'Solve'

    def solve(self):
        self.begin_timing()

        strategy_list = [
            self.sudoku.naked_single,
            self.sudoku.hidden_single,
            self.sudoku.naked_double,
            self.sudoku.hidden_double,
            self.sudoku.naked_triple,
            self.sudoku.hidden_triple,
            self.sudoku.naked_quad,
            self.sudoku.hidden_quad,
            # self.sudoku.reduction
        ]

        progress = True
        while progress:
            for strategy in strategy_list:
                progress = strategy()
                if progress:
                    break
        self.general_brute_force()
        self.end_timing()


# Demo

def dump(obj):
    for attr in obj.__dict__:
        print(f'obj.{attr} = {getattr(obj, attr)}')


if __name__ == '__main__':
    puzzle1 = '000500000425090001800010020500000000019000460000000002090040003200060807000001600'

    strat = StrategySolve(puzzle1)
    strat.solve()
    print(strat.sudoku.input)
    print(strat.sudoku.output)
    print(strat.sudoku.strategy_counts)
    print(strat.count)
    print(strat.sudoku.output == '971582346425693781863714529542136978319278465687459132196847253234965817758321694')
