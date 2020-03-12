"""
Here are all my sudoku solving algorithms.

Working on refactoring them for maintainability and readablilty.
Also, want to add some more features, like contradiction depth checker,
and something about how far we are from the correct answer when we start
(like if we have to start with a 1, but the correct first cell is a 9)
"""

import time
import itertools as it

"""
To do:
    1. Add in the code for investigating difficulty.
    2. REFACTOR. So much repetition...
    3. Rewrite Solve as a class, which can do different things:
        probably have "solver" as a class, with different particular types of
        solver

        then i can update universal things in the superclass
        also do each strategy as a class? maybe

        solve, with each strategy
        print original as string
        print original as grid
        print solution as string
        print solution as grid
        time to solve
        strageties used
        how many times each strategy was used
        how much progress is made from each application of a strategy
        complexity information
        compare human vs computer complexity

        have a method which does EVERYTHING, for simplicity / ease of use
        but also be able to do certian things selectively
"""


class Grid:
    """This is the grid object we will use to represent the Sudoku."""

    def __init__(self, string):
        self.cells = [[x for x in string[0:9]],
                      [x for x in string[9:18]],
                      [x for x in string[18:27]],
                      [x for x in string[27:36]],
                      [x for x in string[36:45]],
                      [x for x in string[45:54]],
                      [x for x in string[54:63]],
                      [x for x in string[63:72]],
                      [x for x in string[72:81]]]

    def box(self, i, j):
        """
        This function outputs the contents of the box containing the cell
        with coordinates i, j.

        Parameters
        ----------
        i : TYPE
            DESCRIPTION.
        j : TYPE
            DESCRIPTION.

        Returns
        -------
        box : TYPE
            DESCRIPTION.

        """
        # let's find the coordinate of the upper left cell in the box
        # We'll calculate the rest of the cell from there

        # box x coordinate
        x = i // 3 * 3
        # box y coordinate
        y = j // 3 * 3

        box = [self.cells[a][b] for a in [x, x+1, x+2] for b in [y, y+1, y+2]]
        return box

    def row(self, i, j):
        """
        This function outputs the contents of the row containing the cell with
        coordinates i, j.

        Parameters
        ----------
        i : TYPE
            DESCRIPTION.
        j : TYPE
            DESCRIPTION.

        Returns
        -------
        row : TYPE
            DESCRIPTION.

        """
        row = [self.cells[i][y] for y in range(9)]
        return row

    def column(self, i, j):
        """
        This function outputs the contents of the column containing
        the cell with coordinates i, j.

        Parameters
        ----------
        i : TYPE
            DESCRIPTION.
        j : TYPE
            DESCRIPTION.

        Returns
        -------
        column : TYPE
            DESCRIPTION.

        """
        column = [self.cells[x][j] for x in range(9)]
        return column

    def display(self):
        """
        Displays the puzzle, as a single block of strings

        Returns
        -------
        None.

        """
        print('')
        for x in self.cells:
            print(''.join(x))
        print('')

    def display_grid(self):
        """
        Displays the puzzle, broken up into lists

        Returns
        -------
        None.

        """
        print('')
        for x in self.cells:
            print(x)
        print('')

# =============================================================================
# GENERAL FUNCTIONS
# =============================================================================

def check(thing):
    """ 
    Checks a given input (box, row, or column) for duplicates
    Could be any list really, but will only check for duplicates in 1-9 (As strings)
    """

    #First, remove any empty spaces
    clean_thing = []
    for x in thing:
        if x in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            clean_thing.append(x)
    
    #Now check for duplicates
    if len(clean_thing) == len(set(clean_thing)):
        return True
    else:
        return False

def box_num(i, j):
    """
    # Find what number box a cell is in (0 - 8)

    Parameters
    ----------
    i : TYPE
        DESCRIPTION.
    j : TYPE
        DESCRIPTION.

    Returns
    -------
    int
        DESCRIPTION.

    """
    
    #box x coordinate
    x = i // 3 * 3
    #box y coordinate
    y = j // 3 * 3
    
    if (x, y) == (0, 0):
        return 0
    elif (x, y) == (0, 3):
        return 1
    elif (x, y) == (0, 6):
        return 2
    elif (x, y) == (3, 0):
        return 3
    elif (x, y) == (3, 3):
        return 4
    elif (x, y) == (3, 6):
        return 5
    elif (x, y) == (6, 0):
        return 6
    elif (x, y) == (6, 3):
        return 7
    elif (x, y) == (6, 6):
        return 8

def update_blanks(blanks, sudoku):
    """
    Updates all blanks with new information in the sudoku

    Parameters
    ----------
    blanks : TYPE
        DESCRIPTION.
    sudoku : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    
    for blank in blanks:
        for poss in blank[3][:]:
            if poss in sudoku.column(blank[1], blank[2]) or poss in sudoku.row(blank[1], blank[2]) or poss in sudoku.box(blank[1], blank[2]):
                blank[3].remove(poss)
   
def generate_blanks(sudoku):
    
    #Step 1: #First, generate a list of all blank spaces, along with their 
    # coordinates, and possibilities, in the format of 
    # ['.', i, j, [possible numbers]]
    blanks = []
    for i in range(9):
        for j in range(9):
            if sudoku.cells[i][j] not in (
                    ['1', '2', '3', '4', '5', '6', '7', '8', '9']):
                                
                poss = ['1', '2', '3', '4', '5', '6', '7', '8','9']
                real_poss = []
                
                for x in poss:
                    if not (x in sudoku.column(i, j) or x in sudoku.row(i, j) 
                            or x in sudoku.box(i, j)):
                        real_poss.append(x)
                
                blanks.append([sudoku.cells[i][j], i, j, real_poss])
    return blanks

    
# =============================================================================
# STRATEGIES    
# =============================================================================

def naked_single(blanks, sudoku):
    """
    Fill in a blank if there is only a single possibility

    Parameters
    ----------
    blanks : TYPE
        DESCRIPTION.
    sudoku : TYPE
        DESCRIPTION.

    Returns
    -------
    bool
        DESCRIPTION.

    """
    
    for i in range(len(blanks)):
        if len(blanks[i][3]) == 1:
            # Update the puzzle
            sudoku.cells[blanks[i][1]][blanks[i][2]] = blanks[i][3][0]
            # Delete that entry in the blanks
            del blanks[i]
            # Note that progress has been made this loop
            return True
    return False
   
def hidden_single(blanks, sudoku):
    """
    Fill in when there is only one remaining place for a number in a row, 
    column, or box. For each blank, see if it is the only number in it's row, 
    column, or box that could contain a given number. Nuts, maybe I should 
    have attached the possibilites to each cell..., some sort of object
    Parameters
    ----------
    blanks : TYPE
        DESCRIPTION.
    sudoku : TYPE
        DESCRIPTION.

    Returns
    -------
    bool
        DESCRIPTION.

    """
    
    
    
    #For each blank:
        #1) for each possiblity
        #2) look in it's row. Is there any other cell which is blank and 
            # has that possibility? If not, fill it in
        #3) Look in it's column. Is there any other cell which is blank and 
            # has that possibility? If not, fill it in
        #4) Look in it's box. Is there any other cell which is blank and 
            # has that possibility? If not, fill it in
    for blank in blanks:
        # generate the subset of blanks that are in the same column, row, 
        # or box as our current blank
        
        # These have the same second coordinate
        blank_column = [other_blank for other_blank in blanks if 
                        other_blank[2] == blank[2] and other_blank != blank]
        
        # These have the same first coordinate
        blank_row = [other_blank for other_blank in blanks if 
                     other_blank[1] == blank[1] and other_blank != blank]
        
        # These have the same whole number when divided by 3
        blank_box = [other_blank for other_blank in blanks if 
                     int(other_blank[1])//3 == int(blank[1])//3 and 
                     int(other_blank[2])//3 == int(blank[2])//3 and 
                     other_blank != blank]
        
        # Iterate through each possibility. See if it is the only 
        other_column_poss = {num for other_poss in blank_column for 
                             num in other_poss[3]}
        other_row_poss = {num for other_poss in blank_row for 
                          num in other_poss[3]}
        other_box_poss = {num for other_poss in blank_box for 
                          num in other_poss[3]}
        
        for poss in blank[3]:
            if (not poss in other_column_poss or 
                not poss in other_row_poss or 
                not poss in other_box_poss):
                sudoku.cells[blank[1]][blank[2]] = poss
                blanks.remove(blank)
                return True
    return False

def naked_double(blanks):     
    
    """
    Just naked doubles
    THIS IS A BIT INEFFICIENT, I'M GENERATING THESE LISTS BOTH ABOVE AND HERE
    Probably not a big deal though, and makes the code more readable and 
    the logic easier to write for me

    Parameters
    ----------
    blanks : TYPE
        DESCRIPTION.

    Returns
    -------
    bool
        DESCRIPTION.

    """
    for blank in blanks:
        # generate the subset of blanks that are in the same column, row, 
        # or box as our current blank
        
        # These have the same second coordinate
        blank_column = [other_blank for other_blank in blanks if 
                        other_blank[2] == blank[2] and other_blank != blank]
        
        # These have the same first coordinate
        blank_row = [other_blank for other_blank in blanks if 
                     other_blank[1] == blank[1] and other_blank != blank]
        
        # These have the same whole number when divided by 3
        blank_box = [other_blank for other_blank in blanks if 
                     int(other_blank[1])//3 == int(blank[1])//3 and 
                     int(other_blank[2])//3 == int(blank[2])//3 and 
                     other_blank != blank]
    
        # See if any other blank in the row, column, or box 
        # has identical possiblities, and is length 2. 
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
    If a pair of numbers only appears in 2 cells for a given row, 
    column, or box, we should update those cells to only that pair
    For each row, column, or box, consider each pair of numbers from 
    among the possiblites in that space
    Yes, we're regenerating these lists of blanks. It's probably not a problem.
    Probably...

    Parameters
    ----------
    blanks : TYPE
        DESCRIPTION.

    Returns
    -------
    bool
        DESCRIPTION.

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
    Naked triples
    Recall that a naked triple means 3 in a subsection that all have 
    EXACTLY and only members of a len 3 subset of possibilities
    So {1, 2}, {1, 3}, and {2, 3} would form a naked triple
    I may assume that there are no naked singles or doubles 
    because of the previous code
    Instead of going through each blank and generating 
    THIS IS A BIT INEFFICIENT, I'M GENERATING THESE LISTS BOTH ABOVE AND HERE
    Probably not a big deal though, and makes the code more readable 
    and the logic easier to write for me
    Let's generate each column, row, and box, but only for blanks
    Remember, these are copies, so alter the original items in b???
    Just make a list, or maybe a dict

    Parameters
    ----------
    blanks : TYPE
        DESCRIPTION.

    Returns
    -------
    bool
        DESCRIPTION.

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
    If there's a set of 3 numbers that appear in exactly 3 cells in a 
    given space, reduce the possibilities of those cells to 
    exactly those 3 numbers      

    Parameters
    ----------
    blanks : TYPE
        DESCRIPTION.

    Returns
    -------
    bool
        DESCRIPTION.

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
    Same as naked triple, but with 4
    Cleaned up the code a bit by using .issubset
    Need to go back and clean up naked triple
    Very rare

    Parameters
    ----------
    blanks : TYPE
        DESCRIPTION.

    Returns
    -------
    bool
        DESCRIPTION.

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
    Same as hidden_triple, but with 4
    Very rare

    Parameters
    ----------
    blanks : TYPE
        DESCRIPTION.

    Returns
    -------
    bool
        DESCRIPTION.

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
    If all occurences of a number in one region (box, line, or row) 
    intersect with another region (box, line, or row),
    then remove that number from the second region
    I believe there is a way to use the same code for each, 
    but for now I'll hand code each of 4 cases:
        1 - Box gives info about row
        2 - Box gives info about column
        3 - Column gives info about box
        4 - Row gives info about box

    Parameters
    ----------
    blanks : TYPE
        DESCRIPTION.

    Returns
    -------
    bool
        DESCRIPTION.

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
    
    def __init__(self, puzzle):
        self.start_time = time.time()
        self.sudoku = Grid(puzzle)

        print('Here is the brute force solution result:')
        print(puzzle)
        sudoku.display()  

        self.blanks = generate_blanks(sudoku)
        
        self.i = 0    
        self.count = 0 
        
    def finish_puzzle():
        #Format the solution as a string of 81 characters, like the input
        solution = ''.join([''.join(x) for x in sudoku.cells])

        sudoku.display()
        print(solution)
        print('\n')
        print(f'This sudoku was solved in {count} loops.')
        print('\n')
        print(f'''--- This program took 
              {time.time() - start_time} seconds to run. ---''')
        print('\n')
        print('-'*200)
        print('\n')
        return solution
        


class BruteForce(Solver):
    """
    Here is my original, mostly brute force, solution

    Parameters
    ----------
    puzzle : string
        81 characters in length. The puzzle. Use periods to as blanks for now.

    Returns
    -------
    solution : string
        81 characters in length. The solved puzzle.

    """
    def solve_bf(puzzle):
        # This is the engine that drives the solution 
        # In each scenario, we update both the list of blanks,
        # and the sudoku grid itself
        # Keep going until our index hits the length of blanks
        # (Which is to say, we're one step beyond)
        while i != len(blanks):
            count += 1
            
            # Scenario 1: blank number i is still blank. Start with 1
            if blanks[i][0] not in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                blanks[i][0] = '1'
                sudoku.cells[blanks[i][1]][blanks[i][2]] = blanks[i][0]
            
            # Scenario 2: blank number i is at 9. 
            # So we've already tried all the options
            # So we need to clear it out and step back.
            # Also we skip the rest of the loop,
            # becacuse we don't need to check for consistency
            # In fact, it would be bad to check for consistency,
            # as we are guarenteed to trivially be consistent
            # This would lead to stepping forward, canceling out our step back,
            # and ending up in an infinite loop  
            elif blanks[i][0] == '9':
                blanks[i][0] = '.'
                sudoku.cells[blanks[i][1]][blanks[i][2]] = blanks[i][0]
                i -= 1
                continue
            
            # Scenario 3: There's some number 1-8 already plugged in.
            # So we step forward by one.
            else:
                blanks[i][0] = str(int(blanks[i][0]) + 1)
                sudoku.cells[blanks[i][1]][blanks[i][2]] = blanks[i][0]
            
            # Now we check for consistency.
            # If we are consistent, we'll step forward.
            # If not, we'll run through this same spot again.
            consistent = (check(sudoku.row(blanks[i][1], blanks[i][2])) and
                          check(sudoku.column(blanks[i][1], blanks[i][2])) and
                          check(sudoku.box(blanks[i][1], blanks[i][2])))
            if consistent:
                i += 1
                
        
    
def solve_bf(puzzle):
    """
    Here is my original, mostly brute force, solution

    Parameters
    ----------
    puzzle : string
        81 characters in length. The puzzle. Use periods to as blanks for now.

    Returns
    -------
    solution : string
        81 characters in length. The solved puzzle.

    """
    
    start_time = time.time()
    sudoku = Grid(puzzle)

    print('Here is the brute force solution result:')
    print(puzzle)
    sudoku.display()      

    # Here we use the same blanks list as the other methods,
    # but we ignore the possibilities information
    blanks = generate_blanks(sudoku)
    

    # Initialize some variables
    i = 0    
    count = 0 

    # This is the engine that drives the solution 
    # In each scenario, we update both the list of blanks,
    # and the sudoku grid itself
    # Keep going until our index hits the length of blanks
    # (Which is to say, we're one step beyond)
    while i != len(blanks):
        count += 1
        
        # Scenario 1: blank number i is still blank. Start with 1
        if blanks[i][0] not in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            blanks[i][0] = '1'
            sudoku.cells[blanks[i][1]][blanks[i][2]] = blanks[i][0]
        
        # Scenario 2: blank number i is at 9. 
        # So we've already tried all the options
        # So we need to clear it out and step back.
        # Also we skip the rest of the loop,
        # becacuse we don't need to check for consistency
        # In fact, it would be bad to check for consistency,
        # as we are guarenteed to trivially be consistent
        # This would lead to stepping forward, canceling out our step back,
        # and ending up in an infinite loop  
        elif blanks[i][0] == '9':
            blanks[i][0] = '.'
            sudoku.cells[blanks[i][1]][blanks[i][2]] = blanks[i][0]
            i -= 1
            continue
        
        # Scenario 3: There's some number 1-8 already plugged in.
        # So we step forward by one.
        else:
            blanks[i][0] = str(int(blanks[i][0]) + 1)
            sudoku.cells[blanks[i][1]][blanks[i][2]] = blanks[i][0]
        
        # Now we check for consistency.
        # If we are consistent, we'll step forward.
        # If not, we'll run through this same spot again.
        consistent = (check(sudoku.row(blanks[i][1], blanks[i][2])) and
                      check(sudoku.column(blanks[i][1], blanks[i][2])) and
                      check(sudoku.box(blanks[i][1], blanks[i][2])))
        if consistent:
            i += 1

    #Format the solution as a string of 81 characters, like the input
    solution = ''.join([''.join(x) for x in sudoku.cells])

    
    sudoku.display()
    print(solution)
    print('\n')
    print(f'This sudoku was solved in {count} loops.')
    print('\n')
    print(f'''--- This program took 
          {time.time() - start_time} seconds to run. ---''')
    print('\n')
    print('-'*200)
    print('\n')
    return solution







def solve_lbf(puzzle):
    """
    Here is my limited brute force solver, which only brute forces 
    over the possiblities for each cell, not all of 1-9
    It cuts the solve time roughly in half

    Parameters
    ----------
    puzzle : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    start_time = time.time()
    

    # Here is the solution function.
    # Takes us from the original puzzle to the solution.

    sudoku = Grid(puzzle)

    print('Here is the less brute force solution result:')
    print(puzzle)
    sudoku.display()      

    
    blanks = generate_blanks(sudoku)
    
    
    # Step 2: Finish with brute force, if needed.
    #     Only brute force through the possibilites, though.
    #     3 Possibilities, just like the other one.
    #         1) Nothing filled in yet -> Use the first possibility
    #         2) The last possibility filled in -> step back to previous blank
    #         3) Else -> try the next possibility
    #     Note that we are guarenteed to have at least 2 possibilities, 
    #     as the previous code would have filled
    #     In the solution if there were only one possibility
    
    
    i = 0
    count = 0
    
    while i != len(blanks):
        count += 1
        
        # Scenario 1: blank number i is still blank. 
        # Start with the first possibility
        if blanks[i][0] == '.':
            blanks[i][0] = blanks[i][3][0]
            sudoku.cells[blanks[i][1]][blanks[i][2]] = blanks[i][0]
        
        # Scenario 2: blank number i is at the last possibility.
        # So we've already tried all the options
        # So we need to clear it out and step back.
        # Also we skip the rest of the loop, 
        # becacuse we don't need to check for consistency
        # In fact, it would be bad to check for consistency, 
        # as we are guarenteed to trivially be consistent
        # This would lead to stepping forward, canceling out our step back, 
        # and ending up in an infinite loop
        elif blanks[i][0] == blanks[i][3][-1]:
            blanks[i][0] = '.'
            sudoku.cells[blanks[i][1]][blanks[i][2]] = blanks[i][0]
            i -= 1
            continue
        
        # Scenario 3: There's some non last possibility already plugged in. 
        # So we step forward by one.
        else:
            blanks[i][0] = blanks[i][3][blanks[i][3].index(blanks[i][0]) + 1] 
            # The above code is inefficient, I should store which poss I'm on
            sudoku.cells[blanks[i][1]][blanks[i][2]] = blanks[i][0]
        
        # Now we check for consistency. 
        # If we are consistent, we'll step forward.
        # If not, we'll run through this same spot again.
        consistent = (check(sudoku.row(blanks[i][1], blanks[i][2])) and 
                      check(sudoku.column(blanks[i][1], blanks[i][2])) and 
                      check(sudoku.box(blanks[i][1], blanks[i][2])))
        if consistent:
            i += 1
        
        
        
        
# Format the solution as a string of 81 characters, like the input
    solution = ''.join([''.join(x) for x in sudoku.cells])

    
    sudoku.display()
    print(solution)
    print('\n')
    print(f'This sudoku was solved in {count} loops.')
    print('\n')
    print(f'''--- This program took
           {time.time() - start_time} seconds to run. ---''')
    print('\n')
    print('-'*200)
    print('\n')
    return solution


def solve(puzzle):
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

    Parameters
    ----------
    puzzle : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    
    start_time = time.time()
    
        


# Here is the solution function.
# Takes us from the original puzzle to the solution.

    sudoku = Grid(puzzle)

    print('Here is the mostly not brute force solution result:')
    print(puzzle)
    sudoku.display()      

    blanks = generate_blanks(sudoku)

        
    #Step 2: Loop through basic strategies:
        # Hidden and Naked Singles
        # Now with naked doubles, triples, and quads!
        # Maybe even 
        # When a blank is solved in this way, remove it from the list of blanks
        # Make sure to update each cell's possibilities as you go
        # Don't do more advanced strategies if you don't have to
        # I can probably remove some of the update blanks steps
    
    ns_count = 0
    hs_count = 0
    nd_count = 0
    hd_count = 0
    nt_count = 0
    ht_count = 0
    nq_count = 0
    hq_count = 0
    r_count = 0
    
    progress = True
    while progress == True:
        
        prog1 = naked_single(blanks, sudoku)
        update_blanks(blanks, sudoku)        
        progress = prog1
        ns_count += prog1
        
        if progress == False:
            prog2 = hidden_single(blanks, sudoku)
            update_blanks(blanks, sudoku)    
            progress = progress or prog2
            hs_count += prog2

            if progress == False:
                prog3 = naked_double(blanks)
                update_blanks(blanks, sudoku) 
                progress = progress or prog3
                nd_count += prog3
                
                if progress == False:
                    prog4 = hidden_double(blanks)
                    update_blanks(blanks, sudoku) 
                    progress = progress or prog4
                    hd_count += prog4
                
                    if progress == False:
                        prog5 = naked_triple(blanks)
                        update_blanks(blanks, sudoku) 
                        progress = progress or prog5
                        nt_count += prog5
                        
                        if progress == False:
                            prog6 = hidden_triple(blanks)
                            update_blanks(blanks, sudoku) 
                            progress = progress or prog6
                            ht_count += prog6
                            
                            if progress == False:
                                prog7 = naked_quad(blanks)
                                update_blanks(blanks, sudoku) 
                                progress = progress or prog7
                                nq_count += prog7
                                
                                if progress == False:
                                    prog8 = hidden_quad(blanks)
                                    update_blanks(blanks, sudoku) 
                                    progress = progress or prog8
                                    hq_count += prog8
                                    
                                    if progress == False:
                                        prog9 = reduction(blanks)
                                        update_blanks(blanks, sudoku) 
                                        progress = progress or prog9
                                        r_count += prog9
            
        
        
        
        
            
    
    sudoku.display()
    print(f'We solved {ns_count} cells with naked singles.')
    print(f'We solved {hs_count} cells with hidden singles.')
    print(f'We helped {nd_count} times with naked doubles.')
    print(f'We helped {hd_count} times with hidden doubles.')
    print(f'We helped {nt_count} times with naked triples.')
    print(f'We helped {ht_count} times with hidden triples.')
    print(f'We helped {nq_count} times with naked quads.')
    print(f'We helped {hq_count} times with hidden quads.')
    print(f'We helped {r_count} times with reduction.')
    
    
    # Step 3: Finish with brute force, if needed.
        # Only brute force through the possibilites, though. (lbf)
        # 3 Possibilities, just like the other one.
            # 1) Nothing filled in yet -> Use the first possibility
            # 2) The last possibility filled in -> step back to previous blank
            # 3) Else -> try the next possibility
        # Note that we are guarenteed to have at least 2 possibilities, 
        # as the previous code would have filled
        # In the solution if there were only one possibility

    i = 0
    count = 0
    
    while i != len(blanks):
        count += 1
        
        # Scenario 1: blank number i is still blank. 
        # Start with the first possibility
        if blanks[i][0] == '.':
            blanks[i][0] = blanks[i][3][0]
            sudoku.cells[blanks[i][1]][blanks[i][2]] = blanks[i][0]
        
        # Scenario 2: blank number i is at the last possibility. 
        # So we've already tried all the options
        # So we need to clear it out and step back.
        # Also we skip the rest of the loop, 
        # becacuse we don't need to check for consistency
        # In fact, it would be bad to check for consistency, 
        # as we are guarenteed to trivially be consistent
        # This would lead to stepping forward, canceling out our step back, 
        # and ending up in an infinite loop
        elif blanks[i][0] == blanks[i][3][-1]:
            blanks[i][0] = '.'
            sudoku.cells[blanks[i][1]][blanks[i][2]] = blanks[i][0]
            i -= 1
            continue
        
        # Scenario 3: There's some non last possibility already plugged in. 
        # So we step forward by one.
        else:
            blanks[i][0] = blanks[i][3][blanks[i][3].index(blanks[i][0]) + 1] 
            #The above is inefficient, I should store which poss I'm on
            sudoku.cells[blanks[i][1]][blanks[i][2]] = blanks[i][0]
        
        # Now we check for consistency. 
        # If we are consistent, we'll step forward.
        # If not, we'll run through this same spot again.
        consistent = (check(sudoku.row(blanks[i][1], blanks[i][2])) and 
                      check(sudoku.column(blanks[i][1], blanks[i][2])) and 
                      check(sudoku.box(blanks[i][1], blanks[i][2])))
        if consistent:
            i += 1
        
        
        
        
# Format the solution as a string of 81 characters, like the input
    solution = ''.join([''.join(x) for x in sudoku.cells])

    
    sudoku.display()
    print(solution)
    print('\n')
    print(f'Brute force: {count} loops.')
    print('\n')
    print(f'''--- This program took 
          {time.time() - start_time} seconds to run. ---''')
    print('-'*200)
    print('\n')
    return solution

def full_solve(puzzle):
    """
     Here's a shortcut to solving with all 3 methods, 
     so I don't have to keep typing it out

    Parameters
    ----------
    puzzle : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    
    solve_bf(puzzle)
    solve_lbf(puzzle)
    solve(puzzle)



if __name__ == '__main__':
    # Easy Example
    # puzzle = '''...1.5...14....67..8...24...63.7..1.9....
    # ...3.1..9.52...72...8..26....35...4.9...'''
    
    # Trickier Example
    # full_solve(puzzle)
    puzzle = '900050000200630005006002000003100070000020900080005000000800100500010004000060008'.replace('0','.')
    BruteForce(puzzle).solve_bf()