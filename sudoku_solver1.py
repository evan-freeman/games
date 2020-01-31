"""
Sudoku Solver by Evan Freeman
Brute force-ish


Input must be a string of 81 characters
Blank cells may be filled with anything for the input.



For example:
    .94...13..............76..2.8..1.....32.........2...6.....5.4.......8..7..63.4..8
    
Which solves to:
    794582136268931745315476982689715324432869571157243869821657493943128657576394218


Here's the coordinates of every cell in the grid:

(0,0) (0,1) (0,2) (0,3) (0,4) (0,5) (0,6) (0,7) (0,8)
(1,0) (1,1) (1,2) (1,3) (1,4) (1,5) (1,6) (1,7) (1,8)
(2,0) (2,1) (2,2) (2,3) (2,4) (2,5) (2,6) (2,7) (2,8)
(3,0) (3,1) (3,2) (3,3) (3,4) (3,5) (3,6) (3,7) (3,8)
(4,0) (4,1) (4,2) (4,3) (4,4) (4,5) (4,6) (4,7) (4,8)
(5,0) (5,1) (5,2) (5,3) (5,4) (5,5) (5,6) (5,7) (5,8)
(6,0) (6,1) (6,2) (6,3) (6,4) (6,5) (6,6) (6,7) (6,8)
(7,0) (7,1) (7,2) (7,3) (7,4) (7,5) (7,6) (7,7) (7,8)
(8,0) (8,1) (8,2) (8,3) (8,4) (8,5) (8,6) (8,7) (8,8)


Big picture:
1) start filling in blanks, going from left to right, with 1s
    -so, make a list of coordinates that are not yet filled
    -traverse back and forth along this list, filling in, until we get to the end!
2) keep track of each step we take, both the value we gave it and the index of that step
3) check for consistency after each addition
    - better to just check the relevant row, column, and box, but we could check the whole thing in a pinch
4) If there is a contradiction, step backwards once an increment that guess. If that guess is at 9, step back again and increment that guess.
    -continue stepping back until we reach a step which was not 9, then continue from there.
5) keep going until we don't have a contradiction!!
    -Well, also check that we're full somehow
    -This must be A solution
    -My method won't check if there's multiple solutions, though it could...

To do:
    1) Accept more input types
    2) Check for multiple solutions
    3) Implement sudoku strategies to speed up solve time:
        -Could still finish off with brute force, even if I just put in a few basic strategies
        -Do the 'little numbers' technique, where I keep track of the possibilites associated with each cell
    4) Make it display as it goes?
        -That means showing MILLIONS of iterations. Would have to animate SUPER FAST.
        -Or collect all those images and make a gif of it, after the fact.
            - Pre-complile??? I don't know what I'm talking about
    5) Just how brute force is my algorithm? I think it's slightly faster than just populating every blank with a guess,
        checking the whole puzzle, then updating the whole puzzle and checking again (or even just checking the parts effected
        by the update).
        -After all, my algorithm cuts off certian possibility spaces as it goes
        -Still pretty brute force

"""

class Grid:

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
                                    
          
    # This function outputs the contents of the box containing the cell with coordinates i, j
    def box(self, i, j):
        #let's find the coordinate of the upper left cell in the box
        #We'll calculate the rest of the cell from there
        
        #box x coordinate
        x = i // 3 * 3
        #box y coordinate
        y = j // 3 * 3
        
        box = [self.cells[a][b] for a in [x, x+1, x+2] for b in [y, y+1, y+2]]
        return box
        
    
    #This function outputs the contents of the row containing the cell with coordinates i, j
    def row(self, i, j):
        row = [self.cells[i][y] for y in range(9)]
        return row
    
    
    #This function outputs the contents of the column containing the cell with coordinates i, j
    def column(self, i, j):
        column = [self.cells[x][j] for x in range(9)]
        return column
    
    
    #Displays the puzzle, as a single block of strings
    def display(self):
        print('')
        for x in self.cells:
            print(''.join(x))
        print('')
    
    
    #Displays the puzzle, broken up into lists
    def display_grid(self):
        print('')
        for x in self.cells:
            print(x)
        print('')
     
        
        
#Checks a given input (box, row, or column) for duplicates
#Could be any list really, but will only check for duplicates in 1-9 (As strings)
#Should this be part of the sudoku object? Doesn't act on the object, so I don't think so
def check(thing):
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

#Here is the solution function. Takes us from the original puzzle to the solution.
def solve(puzzle):
    sudoku = Grid(puzzle)

    sudoku.display()      

    
    #Step 1: #First, generate a list of all blank spaces, along with their coordinates, in the format of ['.', i, j]
    b = []
    for i in range(9):
        for j in range(9):
            if sudoku.cells[i][j] not in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                #so keep track of the cell we are going to fill, and it's coordinates
                b.append([sudoku.cells[i][j], i, j])

    #Initialize some variables
    i = 0    
    count = 0 

    #This is the engine that drives the solution 
    #In each scenario, we update both the list of blanks, and the sudoku grid itself
    #Keep going until our index hits the length of blanks (Which is to say, we're one step beyond)
    while i != len(b):
        count += 1
        
        #Scenario 1: blank number i is still blank. Start with 1
        if b[i][0] not in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            b[i][0] = '1'
            sudoku.cells[b[i][1]][b[i][2]] = b[i][0]
        
        #Scenario 2: blank number i is at 9. So we've already tried all the options
        #So we need to clear it out and step back.
        #Also we skip the rest of the loop, becacuse we don't need to check for consistency
        #In fact, it would be bad to check for consistency, as we are guarenteed to trivially be consistent
        #This would lead to stepping forward, canceling out our step back, and ending up in an infinite loop
        elif b[i][0] == '9':
            b[i][0] = '.'
            sudoku.cells[b[i][1]][b[i][2]] = b[i][0]
            i -= 1
            continue
        
        #Scenario 3: There's some number 1-8 already plugged in. So we step forward by one.
        else:
            b[i][0] = str(int(b[i][0]) + 1)
            sudoku.cells[b[i][1]][b[i][2]] = b[i][0]
        
        #Now we check for consistency. If we are consistent, we'll step forward.
        #If not, we'll run through this same spot again.
        consistent = check(sudoku.row(b[i][1], b[i][2])) and check(sudoku.column(b[i][1], b[i][2])) and check(sudoku.box(b[i][1], b[i][2]))
        if consistent:
            i += 1

    #Format the solution as a string of 81 characters, like the input
    solution = ''.join([''.join(x) for x in sudoku.cells])

    sudoku.display()
    print(solution)
    print('\n')
    print(f'This sudoku was solved in {count} loops.')

    return solution


# I've added a particular puzzle for it to solve. You can uncomment the lines below to make it ask for an input, 
# Or just plug in your own puzzle below.

# puzzle = input('Please input your sudoku puzzle as a string of 81 characters. ')      
#solve(puzzle)

solve('.94...13..............76..2.8..1.....32.........2...6.....5.4.......8..7..63.4..8')    