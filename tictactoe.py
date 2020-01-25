import sys

"""
Created on Fri Jan 24 18:47:33 2020

@author: evant
"""

'''Let's make tic tac toe!!

Some Goals:
    1) object oriented
    2) visual interface? (maybe later, for now, just get it running)
    3) basic ai (probably just takes a random legal move)
    


'''

#Game Board Class
class Board:
    
    def __init__(self):
        self.cells = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

    def display(self):
        print('')
        print(f' {self.cells[0]} | {self.cells[1]} | {self.cells[2]} ')
        print(f'-----------')
        print(f' {self.cells[3]} | {self.cells[4]} | {self.cells[5]} ')
        print(f'-----------')
        print(f' {self.cells[6]} | {self.cells[7]} | {self.cells[8]} ')
        print('')

    def update_cell(self, cell_number, player):
        self.cells[cell_number]=player

#Prints a greeting to the user.
def print_header():
    print('\nWelcome to Tic-Tac-Toe! Prepare to lose!!!!')

#Gets the X move from the player, sanitizes input
def get_x_move():
    while True:
        x_move = input('Where would you like to place an X?\n\n')
        try:
            x_move = int(x_move)
        except:
            print('That is not a valid input!')
            continue
        if x_move in remaining_spaces:
            return x_move
        else:
            print('That space is already occupied!')
        
#Gets the O move from the player, sanitizes input
def get_o_move():
    while True:
        o_move = input('Where would you like to place an O?\n\n')
        try:
            o_move = int(o_move)
        except:
            print('\nThat is not a valid input!\n')
            board.display()
            continue
        if o_move in remaining_spaces:
            return o_move
        else:
            print('\nThat space is already occupied!\n')
            board.display()
       
#8 winning combinations, per player
def check_winner():
    if (board.cells[0] == 'X' and board.cells[1] == 'X' and board.cells[2] == 'X' or
        board.cells[3] == 'X' and board.cells[4] == 'X' and board.cells[5] == 'X' or
        board.cells[6] == 'X' and board.cells[7] == 'X' and board.cells[8] == 'X' or
        board.cells[0] == 'X' and board.cells[3] == 'X' and board.cells[6] == 'X' or
        board.cells[1] == 'X' and board.cells[4] == 'X' and board.cells[7] == 'X' or
        board.cells[2] == 'X' and board.cells[5] == 'X' and board.cells[8] == 'X' or
        board.cells[0] == 'X' and board.cells[4] == 'X' and board.cells[8] == 'X' or
        board.cells[2] == 'X' and board.cells[4] == 'X' and board.cells[6] == 'X'):
        board.display()
        print('\nX wins!\n')
        sys.exit()
            
    elif (board.cells[0] == 'O' and board.cells[1] == 'O' and board.cells[2] == 'O' or
        board.cells[3] == 'O' and board.cells[4] == 'O' and board.cells[5] == 'O' or
        board.cells[6] == 'O' and board.cells[7] == 'O' and board.cells[8] == 'O' or
        board.cells[0] == 'O' and board.cells[3] == 'O' and board.cells[6] == 'O' or
        board.cells[1] == 'O' and board.cells[4] == 'O' and board.cells[7] == 'O' or
        board.cells[2] == 'O' and board.cells[5] == 'O' and board.cells[8] == 'O' or
        board.cells[0] == 'O' and board.cells[4] == 'O' and board.cells[8] == 'O' or
        board.cells[2] == 'O' and board.cells[4] == 'O' and board.cells[6] == 'O'):
        board.display()
        print('\nO wins!\n')
        sys.exit()
    
    elif len(remaining_spaces) == 0:
        board.display()
        print("\nIt's a Cat's game. Better luck next time.\n")
        sys.exit()
    
    
#Greet the user, and initialize the board
print_header()
board=Board()
remaining_spaces=[1, 2, 3, 4, 5, 6, 7, 8, 9]
turn_tracker='X'

#Display the board
board.display()


#I can refactor this to not need the if clause, later...
while len(remaining_spaces)>0:
    if turn_tracker == 'X':
        x_move = get_x_move()
        board.update_cell(x_move - 1, turn_tracker)
        turn_tracker='O'
        remaining_spaces.remove(x_move)
    elif turn_tracker == 'O':
        o_move = get_o_move()
        board.update_cell(o_move - 1,turn_tracker)
        turn_tracker='X'
        remaining_spaces.remove(o_move)
    check_winner()
    board.display()
