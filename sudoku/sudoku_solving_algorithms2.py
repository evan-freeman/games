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
        except TypeError:
            return 0

    def generate_region_list(self, region: str) -> list:
        """This function generates a list of lists containing the cell objects that belong to a given region.
        We'll use this in our __init__, which is why we've defined it here.

        Args:
            region: A string that denotes the desired region - column, row or box

        Returns:
            list: This is a list of 9 lists, each of which contains the 9 cells that belong to a particular region.
        """

        return [[cell for cell in self.cells.values() if getattr(cell, region) == i]
                for i in range(self.n)]

    def generate_blank_region_list(self, region: str) -> list:
        """This function generates a list of lists containing the BLANK cell objects that belong to a given region.
        We'll use this in our __init__, which is why we've defined it here.

        Args:
            region: A string that denotes the desired region - column, row or box

        Returns:
            list: This is a list of 9 lists, each of which contains the BLANK cells that belong to a particular region.
                    The lists may be empty.
        """

        return [[cell for cell in self.cells.values() if getattr(cell, region) == i and cell.value == 0]
                for i in range(self.n)]


    def __init__(self, puzzle):
        """

        """

        self.input = puzzle
        self.list = [self.int_except(x) for x in puzzle]
        self.length = len(puzzle)
        self.n = int(self.length ** .5)
        self.arr = np.array(self.list).reshape((self.n, self.n))
        self.cells = {(x, y): Cell(x, y, self.arr[x, y], self.n) for x in range(self.n) for y in range(self.n)}
        self.columns = self.generate_region_list('column')
        self.rows = self.generate_region_list('row')
        self.boxes = self.generate_region_list('box')
        self.blanks = [cell for cell in self.cells.values() if cell.value == 0]
        self.column_blanks = self.generate_blank_region_list('column')
        self.row_blanks = self.generate_blank_region_list('row')
        self.box_blanks = self.generate_blank_region_list('box')
        self.region_list = ['column', 'row', 'box']

    # =============================================================================
    # DISPLAY FUNCTIONS
    # =============================================================================

    def stringify(self):
        """This function takes the puzzle in it's current state and converts it back into an 81 character string."""

        output = [self.cells[(i, j)].value for i in range(self.n) for j in range(self.n)]
        self.as_string = ''.join(str(x) for x in output)

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

    def update_region_blanks(self):
        """ Updates self.column_blanks, self.row_blanks, and self.box_blanks by removing any cells which are
        no longer blank."""
        for region in self.region_list:
            for element in getattr(self, region):
                for cell in element[:]:  # Here we iterate over a copy, so we don't have issues with modifying inplace.
                    if cell.value != 0:
                        element.remove(cell)

    @staticmethod
    def same_region(cell1, cell2, region):
        """ Returns a boolean for whether two cells are in the same region given, i.e. same column, row, or box."""
        return getattr(cell1, region) == getattr(cell2, region)

    def intersecting_blank_cells(self, cell, region):
        """ Returns a list of cells with intersect the given cell, in the given region, OTHER THAN the given cell.
        i.e. They are in the same row, column, or box."""

        return [other_cell for other_cell in self.blanks if other_cell != cell and self.same_region(cell, other_cell)]

    def generate_other_blanks(self, cell):
        """Returns blanks in OTHER cells in the same column, row, and box, as a list of lists."""

        return [self.intersecting_blank_cells(cell, region) for region in self.region_list]

    @staticmethod
    def check_no_dupes(region, i):
        """
        Returns true if the ith region (column, row, or box) has no duplicate values, else false.
        """

        # First, remove any 0s, which are placeholders for unknowns
        clean_region = [cell.value for cell in region[i] if cell.value != 0]

        # Now check for duplicates. Return True if there were no duplicates, else False.
        return len(clean_region) == len(set(clean_region))

    @staticmethod
    def extract_possibilities(list_of_cells):
        """ Returns a set of all possibilities on a given iterable of cells."""
        return set(poss for cell in list_of_cells for poss in cell.poss)

    # =============================================================================
    # STRATEGY FUNCTIONS
    # =============================================================================

    def naked_single(self):
        """
        Fill in a blank if there is only a single possibility.
        """

        for i, cell in enumerate(self.blanks):
            if len(cell.poss) == 1:  # Check whether there is a single possibility in a given blank cell
                cell.value = cell.poss[0]  # If so, update the puzzle
                del self.blanks[i]  # Delete that entry in the blanks
                return True  # Note that progress has been made this loop
        return False

    def hidden_single(self):
        """
        Fill in when there is only one remaining place for a number in a row,
        column, or box.
        """

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
                    self.blanks.remove(cell)
                    return True
        return False

# TODO: All these functions

    def region_blanks(self, region):
        """ Returns a list of lists of all blank cells in a given region (column, row, or box)."""

        return []

    def remove_from_other_cells(self, list_of_cells, region, i):
        """ This function removes a set of numbers from the possibilities of cells in a given region
        at a given index i OTHER than the given cells.

        """
        for cell in self.blanks:
            pass

    def reduce_cells():
        """ This function reduces a set of cells to only the possibilities they contain from a given set of numbers.


        Returns:

        """
        for blank in column:
            if blank not in subset_quad:
                for poss in blank[3][:]:
                    if poss in quad:
                        blank[3].remove(poss)
                        return True
        pass





    def check_for_naked_set(self, region_blanks, n):
        """Returns whether there is a naked set of size n in a given region, and if so, that set of numbers"""
        for region in region_blanks:
            all_poss = self.extract_possibilities(region)
            for comb in it.combinations(all_poss, n):
                potential_naked_set = [cell for cell in region if set(cell.poss).issubset(set(comb))]
                if len(potential_naked_set) == n:
                    return True, potential_naked_set
        return False, []




    def general_naked(n: int, region_blanks: list) -> bool:
        """ Performs the logic of naked single, double, or triple for a given region.

        Logic - Check whether there is a set of n numbers that are the only

        Args:
            n (int):
            region_blanks:

        Returns:
            bool: True if this technique yielded progress in the puzzle, else false.
        """
        for region in self.region_list:
            success, naked_set = self.check_for_naked_set(region, n):
            if success:
                reduce_cells(naked_set, stuff)
                return True
            return False

    def general_hidden():
        """This will execute a hidden pair, triple, or quad for a given region"""
        pass



# =============================================================================
# STRATEGIES    
# =============================================================================







def naked_double(blanks):
    """
    If there are a pair of numbers in the same region, remove those numbers from the rest of the region
    """
    for blank in blanks:
        # generate the subset of blanks that are in the same column, row, 
        # or box as our current blank
        blank_column, blank_row, blank_box = generate_other_blanks(blank, blanks)

        # See if any other blank in the row, column, or box 
        # has identical possibilities, and is length 2.
        # If so, remove from that column, row, or box.
        for other_blank in blank_column:
            if other_blank[3] == blank[3] and len(blank[3]) == 2:
                for other_other_blank in blank_column:
                    if other_other_blank != other_blank:
                        for poss in blank[3]:
                            if poss in other_other_blank[3]:
                                other_other_blank[3].remove(poss)
                                return True

        for other_blank in blank_row:
            if other_blank[3] == blank[3] and len(blank[3]) == 2:
                for other_other_blank in blank_row:
                    if other_other_blank != other_blank:
                        for poss in blank[3]:
                            if poss in other_other_blank[3]:
                                other_other_blank[3].remove(poss)
                                return True

        for other_blank in blank_box:
            if other_blank[3] == blank[3] and len(blank[3]) == 2:
                for other_other_blank in blank_box:
                    if other_other_blank != other_blank:
                        for poss in blank[3]:
                            if poss in other_other_blank[3]:
                                other_other_blank[3].remove(poss)
                                return True
    return False


def hidden_double(blanks):
    """
    If a pair of numbers only appears in 2 cells for a given region,
    we should update those cells to only that pair
    """

    column_blanks = [[blank for blank in blanks if blank[2] == i] for
                     i in range(9)]
    row_blanks = [[blank for blank in blanks if blank[1] == i] for
                  i in range(9)]
    box_blanks = [[blank for blank in blanks if blank[1] // 3 == i and
                   blank[2] // 3 == j] for i in range(3) for j in range(3)]

    for column in column_blanks:
        all_poss = {x for blank in column for x in blank[3]}
        for double_unsorted in it.combinations(all_poss, 2):
            double = sorted(list(double_unsorted))
            contain_double = [blank for blank in column if
                              any([x in blank[3] for x in double])]
            if len(contain_double) == 2:
                for blank in contain_double:
                    if len(blank[3]) > 2:
                        blank[3] = double
                        return True
    for row in row_blanks:
        all_poss = {x for blank in row for x in blank[3]}
        for double_unsorted in it.combinations(all_poss, 2):
            double = sorted(list(double_unsorted))
            contain_double = [blank for blank in row if
                              any([x in blank[3] for x in double])]
            if len(contain_double) == 2:
                for blank in contain_double:
                    if len(blank[3]) > 2:
                        blank[3] = double
                        return True
    for box in box_blanks:
        all_poss = {x for blank in box for x in blank[3]}
        for double_unsorted in it.combinations(all_poss, 2):
            double = sorted(list(double_unsorted))
            contain_double = [blank for blank in box if
                              any([x in blank[3] for x in double])]
            if len(contain_double) == 2:
                for blank in contain_double:
                    if len(blank[3]) > 2:
                        blank[3] = double
                        return True

    return False


def naked_triple(blanks):
    """
    If a set of 3 numbers are the only candidates in 3 cells in a region,
    remove those 3 numbers from the rest of the region.
    """

    column_blanks = [[blank for blank in blanks if blank[2] == i] for
                     i in range(9)]
    row_blanks = [[blank for blank in blanks if blank[1] == i] for
                  i in range(9)]
    box_blanks = [[blank for blank in blanks if blank[1] // 3 == i and
                   blank[2] // 3 == j] for i in range(3) for j in range(3)]

    for column in column_blanks:
        for blank1 in column:
            if 2 <= len(blank1[3]) <= 3:
                for blank2 in column:
                    triple = set(blank1[3] + blank2[3])
                    if blank2 != blank1 and len(triple) == 3:
                        for blank3 in column:
                            if (blank3 != blank1 and blank3 != blank2 and
                                    set(blank3[3]).issubset(triple)):
                                for blank4 in column:
                                    if (blank4 != blank1 and
                                            blank4 != blank2 and
                                            blank4 != blank3):
                                        for poss in triple:
                                            if poss in blank4[3]:
                                                blank4[3].remove(poss)
                                                return True
    for row in row_blanks:
        for blank1 in row:
            if 2 <= len(blank1[3]) <= 3:
                for blank2 in row:
                    triple = set(blank1[3] + blank2[3])
                    if blank2 != blank1 and len(triple) == 3:
                        for blank3 in row:
                            if (blank3 != blank1 and blank3 != blank2 and
                                    set(blank3[3]).issubset(triple)):
                                for blank4 in row:
                                    if (blank4 != blank1 and
                                            blank4 != blank2 and
                                            blank4 != blank3):
                                        for poss in triple:
                                            if poss in blank4[3]:
                                                blank4[3].remove(poss)
                                                return True
    for box in box_blanks:
        for blank1 in box:
            if 2 <= len(blank1[3]) <= 3:
                for blank2 in box:
                    triple = set(blank1[3] + blank2[3])
                    if blank2 != blank1 and len(triple) == 3:
                        for blank3 in box:
                            if (blank3 != blank1 and blank3 != blank2 and
                                    set(blank3[3]).issubset(triple)):
                                for blank4 in box:
                                    if (blank4 != blank1 and
                                            blank4 != blank2 and
                                            blank4 != blank3):
                                        for poss in triple:
                                            if poss in blank4[3]:
                                                blank4[3].remove(poss)
                                                return True
    return False


def hidden_triple(blanks):
    """
    If there's a set of 3 numbers that appear in exactly 3 cells in a given space,
    reduce the possibilities of those cells to exactly those 3 numbers
    """
    column_blanks = [[blank for blank in blanks if blank[2] == i] for
                     i in range(9)]
    row_blanks = [[blank for blank in blanks if blank[1] == i] for
                  i in range(9)]
    box_blanks = [[blank for blank in blanks if blank[1] // 3 == i and
                   blank[2] // 3 == j] for i in range(3) for j in range(3)]

    for column in column_blanks:
        all_poss = {x for blank in column for x in blank[3]}
        for triple in it.combinations(all_poss, 3):
            contain_triple = [blank for blank in column if
                              any([x in blank[3] for x in triple])]
            if len(contain_triple) == 3:
                for blank in contain_triple:
                    for poss in blank[3][:]:
                        if not poss in triple:
                            blank[3].remove(poss)
                            return True
    for row in row_blanks:
        all_poss = {x for blank in row for x in blank[3]}
        for triple in it.combinations(all_poss, 3):
            contain_triple = [blank for blank in row if
                              any([x in blank[3] for x in triple])]
            if len(contain_triple) == 3:
                for blank in contain_triple:
                    for poss in blank[3][:]:
                        if not poss in triple:
                            blank[3].remove(poss)
                            return True
    for box in box_blanks:
        all_poss = {x for blank in box for x in blank[3]}
        for triple in it.combinations(all_poss, 3):
            contain_triple = [blank for blank in box if
                              any([x in blank[3] for x in triple])]
            if len(contain_triple) == 3:
                for blank in contain_triple:
                    for poss in blank[3][:]:
                        if not poss in triple:
                            blank[3].remove(poss)
                            return True
    return False


def naked_quad(blanks):
    """
    If a set of 4 numbers are the only candidates among 4 cells in a region,
    remove those 4 numbers from the rest of the region.
    Very rare
    """
    column_blanks = [[blank for blank in blanks if blank[2] == i] for
                     i in range(9)]
    row_blanks = [[blank for blank in blanks if blank[1] == i] for
                  i in range(9)]
    box_blanks = [[blank for blank in blanks if blank[1] // 3 == i and
                   blank[2] // 3 == j] for i in range(3) for j in range(3)]

    for column in column_blanks:
        all_poss = {x for blank in column for x in blank[3]}
        for quad in it.combinations(all_poss, 4):
            subset_quad = [blank for blank in column if
                           set(blank[3]).issubset(set(quad))]
            if len(subset_quad) == 4:
                for blank in column:
                    if not blank in subset_quad:
                        for poss in blank[3][:]:
                            if poss in quad:
                                blank[3].remove(poss)
                                return True
    for row in row_blanks:
        all_poss = {x for blank in row for x in blank[3]}
        for quad in it.combinations(all_poss, 4):
            subset_quad = [blank for blank in row if
                           set(blank[3]).issubset(set(quad))]
            if len(subset_quad) == 4:
                for blank in row:
                    if not blank in subset_quad:
                        for poss in blank[3][:]:
                            if poss in quad:
                                blank[3].remove(poss)
                                return True
    for box in box_blanks:
        all_poss = {x for blank in box for x in blank[3]}
        for quad in it.combinations(all_poss, 4):
            subset_quad = [blank for blank in box if
                           set(blank[3]).issubset(set(quad))]
            if len(subset_quad) == 4:
                for blank in box:
                    if not blank in subset_quad:
                        for poss in blank[3][:]:
                            if poss in quad:
                                blank[3].remove(poss)
                                return True
    return False


def hidden_quad(blanks):
    """
    If a set of 4 numbers only appear in 4 cells in a region,
    update those cells candidates to just those 4 numbers.
    Very rare
    """
    column_blanks = [[blank for blank in blanks if blank[2] == i] for
                     i in range(9)]
    row_blanks = [[blank for blank in blanks if blank[1] == i] for
                  i in range(9)]
    box_blanks = [[blank for blank in blanks if blank[1] // 3 == i and
                   blank[2] // 3 == j] for i in range(3) for j in range(3)]

    for column in column_blanks:
        all_poss = {x for blank in column for x in blank[3]}
        for quad in it.combinations(all_poss, 4):
            contain_quad = [blank for blank in column if
                            any([x in blank[3] for x in quad])]
            if len(contain_quad) == 4:
                for blank in contain_quad:
                    for poss in blank[3][:]:
                        if not poss in quad:
                            blank[3].remove(poss)
                            return True
    for row in row_blanks:
        all_poss = {x for blank in row for x in blank[3]}
        for quad in it.combinations(all_poss, 4):
            contain_quad = [blank for blank in row if
                            any([x in blank[3] for x in quad])]
            if len(contain_quad) == 4:
                for blank in contain_quad:
                    for poss in blank[3][:]:
                        if not poss in quad:
                            blank[3].remove(poss)
                            return True
    for box in box_blanks:
        all_poss = {x for blank in box for x in blank[3]}
        for quad in it.combinations(all_poss, 4):
            contain_quad = [blank for blank in box if
                            any([x in blank[3] for x in quad])]
            if len(contain_quad) == 4:
                for blank in contain_quad:
                    for poss in blank[3][:]:
                        if not poss in quad:
                            blank[3].remove(poss)
                            return True
    return False


def reduction(blanks):
    """
    If all occurrences of a number in one region intersect with another region ,
    then remove that number from the second region
    I believe there is a way to use the same code for each, 
    but for now I'll hand code each of 4 cases:
        1 - Box gives info about row
        2 - Box gives info about column
        3 - Column gives info about box
        4 - Row gives info about box
    """

    column_blanks = [[blank for blank in blanks if blank[2] == i] for
                     i in range(9)]
    row_blanks = [[blank for blank in blanks if blank[1] == i] for
                  i in range(9)]
    box_blanks = [[blank for blank in blanks if blank[1] // 3 == i and
                   blank[2] // 3 == j] for i in range(3) for j in range(3)]

    # Scenario 1 and 2
    for box in box_blanks:
        all_poss = {x for blank in box for x in blank[3]}
        for poss in all_poss:
            blank_containing_poss = [blank for blank in box if
                                     poss in blank[3]]
            rows_of_these_blanks = {blank[1] for blank in
                                    blank_containing_poss}
            columns_of_these_blanks = {blank[2] for blank in
                                       blank_containing_poss}
            if len(rows_of_these_blanks) == 1:
                row_num = list(rows_of_these_blanks)[0]
                for blank in row_blanks[row_num]:
                    if not blank in box and poss in blank[3]:
                        blank[3].remove(poss)
                        return True

            if len(columns_of_these_blanks) == 1:
                column_num = list(columns_of_these_blanks)[0]
                for blank in column_blanks[column_num]:
                    if not blank in box and poss in blank[3]:
                        blank[3].remove(poss)
                        return True

    # Scenario 3
    for column in column_blanks:
        all_poss = {x for blank in column for x in blank[3]}
        for poss in all_poss:
            blank_containing_poss = [blank for blank in column if
                                     poss in blank[3]]
            box_of_these_blanks = {box_num(blank[1], blank[2]) for
                                   blank in blank_containing_poss}
            if len(box_of_these_blanks) == 1:
                this_box_num = list(box_of_these_blanks)[0]
                for blank in box_blanks[this_box_num]:
                    if not blank in column and poss in blank[3]:
                        blank[3].remove(poss)
                        return True

    # Scenario 4
    for row in row_blanks:
        all_poss = {x for blank in row for x in blank[3]}
        for poss in all_poss:
            blank_containing_poss = [blank for blank in row if
                                     poss in blank[3]]
            box_of_these_blanks = {box_num(blank[1], blank[2]) for
                                   blank in blank_containing_poss}
            if len(box_of_these_blanks) == 1:
                this_box_num = list(box_of_these_blanks)[0]
                for blank in box_blanks[this_box_num]:
                    if not blank in row and poss in blank[3]:
                        blank[3].remove(poss)
                        return True

    return False


# =============================================================================
# SOLVERS
# =============================================================================

class Solver:
    """ This is a class of general attributes and methods for my 3 Sudoku Solvers"""

    def __init__(self, puzzle):
        self.start_time = time.time()
        self.unsolved = puzzle
        self.sudoku = Grid(puzzle)
        self.i = 0
        self.count = 0
        self.type = 'None'
        self.puzzle = puzzle

    def begin_puzzle(self):
        print(f'Here is the {self.type} solution result:')
        print(self.unsolved)
        self.sudoku.display()

    def finish_puzzle(self):
        # Format the solution as a string of 81 characters, like the input
        self.solution = ''.join([''.join(x) for x in self.sudoku.cells])
        self.total_time = time.time() - self.start_time
        return self.solution

    def display_all(self):
        pass


class BruteForce(Solver):
    """
    Here is a class of solver that uses full brute force. So we don't even limit our candidates for brute force,
    we just go numerically through them all.
    """

    def __init__(self, puzzle):
        super().__init__(puzzle)
        self.type = 'BruteForce'
        self.blanks = []
        for i in range(9):
            for j in range(9):
                if self.sudoku.cells[i][j] not in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    # so keep track of the cell we are going to fill, and it's coordinates
                    self.blanks.append([self.sudoku.cells[i][j], i, j])

    def solve_bf(self):
        # This is the engine that drives the solution 
        # In each scenario, we update both the list of blanks,
        # and the sudoku grid itself
        # Keep going until our index hits the length of blanks
        # (Which is to say, we're one step beyond)

        while self.i != len(self.blanks):
            self.count += 1

            # Scenario 1: blank number i is still blank. Start with 1
            if self.blanks[self.i][0] not in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                self.blanks[self.i][0] = '1'
                self.sudoku.cells[self.blanks[self.i][1]][self.blanks[self.i][2]] = self.blanks[self.i][0]

            # Scenario 2: blank number i is at 9. 
            # So we've already tried all the options
            # So we need to clear it out and step back.
            # Also we skip the rest of the loop,
            # because we don't need to check for consistency
            # In fact, it would be bad to check for consistency,
            # as we are guaranteed to trivially be consistent
            # This would lead to stepping forward, canceling out our step back,
            # and ending up in an infinite loop  
            elif self.blanks[self.i][0] == '9':
                self.blanks[self.i][0] = '.'
                self.sudoku.cells[self.blanks[self.i][1]][self.blanks[self.i][2]] = self.blanks[self.i][0]
                self.i -= 1
                continue

            # Scenario 3: There's some number 1-8 already plugged in.
            # So we step forward by one.
            else:
                self.blanks[self.i][0] = str(int(self.blanks[self.i][0]) + 1)
                self.sudoku.cells[self.blanks[self.i][1]][self.blanks[self.i][2]] = self.blanks[self.i][0]

            # TODO I've changed the check function to check_dupes, and made other changes. So fix this.
            # Now we check for consistency.
            # If we are consistent, we'll step forward.
            # If not, we'll run through this same spot again.
            self.consistent = (check(self.sudoku.row(self.blanks[self.i][1], self.blanks[self.i][2])) and
                               check(self.sudoku.column(self.blanks[self.i][1], self.blanks[self.i][2])) and
                               check(self.sudoku.box(self.blanks[self.i][1], self.blanks[self.i][2])))
            if self.consistent:
                self.i += 1

        self.finish_puzzle()


class LimitedBruteForce(BruteForce):
    """This class uses the same logic as brute force, but first reduces the possible candidate to brute force over"""

    def __init__(self, puzzle):
        super().__init__(puzzle)
        self.type = 'LimitedBruteForce'
        self.blanks = generate_blanks(self.sudoku)

    def solve_lbf(self):
        # Step 2: Use (limited) brute force.
        #     Only brute force through the possibilities.
        #     3 Possibilities, just like the other one.
        #         1) Nothing filled in yet -> Use the first possibility
        #         2) The last possibility filled in -> step back to previous blank
        #         3) Else -> try the next possibility
        #     Note that we are guaranteed to have at least 2 possibilities,
        #     as the previous code would have filled
        #     In the solution if there were only one possibility

        while self.i != len(self.blanks):
            self.count += 1

            # Scenario 1: blank number i is still blank.
            # Start with the first possibility
            if self.blanks[self.i][0] == '.':
                self.blanks[self.i][0] = self.blanks[self.i][3][0]
                self.sudoku.cells[self.blanks[self.i][1]][self.blanks[self.i][2]] = self.blanks[self.i][0]

            # Scenario 2: blank number i is at the last possibility.
            # So we've already tried all the options
            # So we need to clear it out and step back.
            # Also we skip the rest of the loop,
            # because we don't need to check for consistency
            # In fact, it would be bad to check for consistency,
            # as we are guaranteed to trivially be consistent
            # This would lead to stepping forward, canceling out our step back,
            # and ending up in an infinite loop
            elif self.blanks[self.i][0] == self.blanks[self.i][3][-1]:
                self.blanks[self.i][0] = '.'
                self.sudoku.cells[self.blanks[self.i][1]][self.blanks[self.i][2]] = self.blanks[self.i][0]
                self.i -= 1
                continue

            # Scenario 3: There's some non last possibility already plugged in.
            # So we step forward by one.
            else:
                self.blanks[self.i][0] = self.blanks[self.i][3][
                    self.blanks[self.i][3].index(self.blanks[self.i][0]) + 1]
                # The above code is inefficient, I should store which poss I'm on
                self.sudoku.cells[self.blanks[self.i][1]][self.blanks[self.i][2]] = self.blanks[self.i][0]

            # Now we check for consistency.
            # If we are consistent, we'll step forward.
            # If not, we'll run through this same spot again.
            self.consistent = (check(self.sudoku.row(self.blanks[self.i][1], self.blanks[self.i][2])) and
                               check(self.sudoku.column(self.blanks[self.i][1], self.blanks[self.i][2])) and
                               check(self.sudoku.box(self.blanks[self.i][1], self.blanks[self.i][2])))
            if self.consistent:
                self.i += 1

        self.finish_puzzle()


class StrategySolve(LimitedBruteForce):
    """This solver applies the 9 strategies I've programmed above,
    then finishes with limited brute force if necessary"""

    def __init__(self, puzzle):
        super().__init__(puzzle)
        self.ns_count = 0
        self.hs_count = 0
        self.nd_count = 0
        self.hd_count = 0
        self.nt_count = 0
        self.ht_count = 0
        self.nq_count = 0
        self.hq_count = 0
        self.r_count = 0
        self.type = 'Solve'

    def solve(self):
        """
        Here is my updated solver

        Current Techniques:

    1. Naked Singles
    2. Hidden Singles
    3. Naked Doubles
    4. Hidden Doubles
    5. Naked Triples
    6. Naked Quads
    7. Hidden Quads
    8. Pointing Pairs and Box Line Reduction.
        I've grouped these together into 'reduction' so it'll be a bit faster.
        but I'd like to split them out later
    9. Finish with limited brute force if necessary
        """

        self.progress = True
        while self.progress:

            self.prog1 = naked_single(self.blanks, self.sudoku)
            update_poss(self.blanks, self.sudoku)
            update_region_blanks
            self.progress = self.prog1
            self.ns_count += self.prog1

            if self.progress == False:
                self.prog2 = hidden_single(self.blanks, self.sudoku)
                update_blanks(self.blanks, self.sudoku)
                self.progress = self.progress or self.prog2
                self.hs_count += self.prog2

                if self.progress == False:
                    self.prog3 = naked_double(self.blanks)
                    update_blanks(self.blanks, self.sudoku)
                    self.progress = self.progress or self.prog3
                    self.nd_count += self.prog3

                    if self.progress == False:
                        self.prog4 = hidden_double(self.blanks)
                        update_blanks(self.blanks, self.sudoku)
                        progress = self.progress or self.prog4
                        self.hd_count += self.prog4

                        if self.progress == False:
                            self.prog5 = naked_triple(self.blanks)
                            update_blanks(self.blanks, self.sudoku)
                            self.progress = self.progress or self.prog5
                            self.nt_count += self.prog5

                            if self.progress == False:
                                self.prog6 = hidden_triple(self.blanks)
                                update_blanks(self.blanks, self.sudoku)
                                self.progress = self.progress or self.prog6
                                self.ht_count += self.prog6

                                if self.progress == False:
                                    self.prog7 = naked_quad(self.blanks)
                                    update_blanks(self.blanks, self.sudoku)
                                    self.progress = self.progress or self.prog7
                                    self.nq_count += self.prog7

                                    if self.progress == False:
                                        self.prog8 = hidden_quad(self.blanks)
                                        update_blanks(self.blanks, self.sudoku)
                                        self.progress = self.progress or self.prog8
                                        self.hq_count += self.prog8

                                        if self.progress == False:
                                            self.prog9 = reduction(self.blanks)
                                            update_blanks(self.blanks, self.sudoku)
                                            self.progress = self.progress or self.prog9
                                            self.r_count += self.prog9

        self.solve_lbf()


def full_solve(puzzle):
    """
     Here's a shortcut to solving with all 3 methods, so I don't have to keep typing it out
    """

    return [BruteForce(puzzle).solve_bf(), LimitedBruteForce(puzzle).solve_lbf(), StrategySolve(puzzle).solve()]


# Demo

def dump(obj):
    for attr in obj.__dict__:
        print(f'obj.{attr} = {getattr(obj, attr)}')


if __name__ == '__main__':
    puzzle = '900050000200630005006002000003100070000020900080005000000800100500010004000060008'
    sudoku = Grid(puzzle)

    # dump(object1)
    #
    # for i, box in enumerate(object1.boxes):
    #
    #     print(f'\n\nBox Number {i}\n\n')
    #     for cell in box:
    #         dump(cell)
    #         print('')
    #
    # print(object1.stringify())

    sudoku.display()
    sudoku.display_grid()

    print(sudoku.cells[(0, 0)].poss)
    sudoku.update_poss()
    print(sudoku.cells[(0, 0)].poss)
