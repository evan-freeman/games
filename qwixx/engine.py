"""
Qwixx Game Engine
by Evan Freeman

Hi. My name is Evan Freeman. My friends taught me this fun little game called Qwixx. I want to crush them at it,
so I'm going to simulate it, then use various techniques to find the optimal strategy(ies?).

This is the game engine.

I'm coming for you, Megan...

strategies to use?
- minimax
- NN


Note: I'm enforcing strict turn order. Technically all white's are taken first, beginning with the active player,
    THEN a colored pair may be taken by the active player.


"""

import numpy as np
import pandas as pd

""""
Stuff I need
1) dice objects
2) dice bag? to hold / reference the dice
3) players / scoreboards
4) rules
5) game engine (while game isn't over, take a turn)
6) Optional stuff: the engine can roll, or the human can. etc
7) display this stuff? with pygame? maybe someday
"""

color_list = ('red', 'yellow', 'green', 'blue')


class Die:
    def __init__(self, color: str, num: int = 0):
        self.color = color
        self.num = num
        self.value = 0

    def roll(self):
        self.value = np.random.randint(1, 7)

    def display(self):
        print()
        print(f'Die {self.color} {self.num}: {self.num}')
        print()


class Scoreboard:
    def __init__(self, name: str):
        self.name = name
        self.range = range(1, 13)
        self.colors = {color: {num: 'b' for num in self.range} for color in color_list}
        self.penalties = 0
        self.score_conversion = {x: x * (x + 1) // 2 for x in range(13)}

    def display(self):
        print()
        for color in self.colors:
            print(f'{color}:\t{self.colors[color]}')
        print(f'penalties: {self.penalties}')
        print()

    def total_in_color(self, color):
        return list(self.colors[color].values()).count('x')

    @property
    def color_scores(self):
        return {color: self.score_conversion[self.total_in_color(color)] for color in color_list}

    @property
    def score(self):
        return sum(self.color_scores.values()) - 5 * self.penalties


class Qwixx:
    def __init__(self, names: list):
        self.dice_list = [('white', 0)] + [('white', 1)] + list((color, 0) for color in color_list)
        self.dice = {die: Die(*die) for die in self.dice_list}
        self.players = {name: Scoreboard(name) for name in names}
        self.turn_order = names
        self.locked = {color: False for color in color_list}
        self.last_move = None

    def roll_dice(self):
        for die in self.dice.values():
            die.roll()

    def poss_with_white(self, color):
        return (self.dice[(color, 0)].value + self.dice[('white', 0)].value,
                self.dice[(color, 0)].value + self.dice[('white', 1)].value)

    @property
    def poss(self):
        return {
            **{'white': (self.dice[('white', 0)].value + self.dice[('white', 0)].value)},
            **{color: self.poss_with_white(color) for color in color_list}
        }

    @property
    def total_penalties(self):
        return sum(scoreboard.penalties for scoreboard in self.players.values())

    @property
    def total_locked(self):
        return sum(self.locked.values())

    @property
    def game_over(self):
        return np.any([self.players[player].penalties >= 4 for player in self.players]) or self.total_locked >= 2

    def move(self, name, color, num):
        """ This is how a player takes their move. """
        if self.players[name].colors[color][num] == 'x':
            print('Illegal move: Square is already marked!')
            return False
        elif self.players[name].colors[color][num] == '-':
            print('Illegal move: Square is blocked by an x!')
            return False
        elif self.players[name].colors[color][num] == 'b':
            self.players[name].colors[color][num] = 'x'
            for other_num in self.players[name].colors[color]:
                other_num_is_below_num = other_num < num if color in ('red', 'yellow') else other_num > num
                other_num_square_is_blank = (self.players[name].colors[color][other_num] == 'b')
                if other_num_square_is_blank and other_num_is_below_num:
                    self.players[name].colors[color][other_num] = '-'
            return True
    
## TODO: Finish prompt all players.

    def prompt_all_players(self, active_player):
        done = False
        while not done:
            for player in self.turn_order:
                color = input(f'{player}, please select a color: ')
                num = input(f'{player}, please select a number: ')
                done = self.move(player, color, num)

    def determine_starting_player(self):
        pass

    # DISPLAY FUNCTIONS

    def display_dice(self):
        print()
        print('DICE')
        for die in self.dice.values():
            if die.color == 'white':
                print(f'{die.color}{" " + str(die.num)}:\t{die.value}')
            else:
                print(f'{die.color}:\t\t{die.value}')
        print()

    def display_boards(self, name):
        print()
        print(name)
        self.players[name].display()
        print()

    def display_all_boards(self):
        print()
        print('SCORES')
        for name in self.players:
            self.display_boards(name)

    def display_poss(self):
        print()
        print('POSSIBILITIES')
        for key, value in self.poss.items():
            print(f'{key}: {value}', end=' | ')
        print()

    def display_starting_player(self):
        pass

    def display_active_player(self):
        pass

    def display_scores(self):
        for name in self.players:
            print(f'{name}:\t{self.players[name].color_scores} total_score: {self.players[name].score}')

    # THIS IS THE GAME ENGINE
    def begin_game(self):
        print('THE GAME HAS BEGUN!')
        self.determine_starting_player()
        while not self.game_over:
            self.roll_dice()
            self.display_dice()
            self.display_poss()
            self.display_all_boards()
            for name in self.turn_order:
                self.prompt_all_players(name)

        print('THE GAME IS OVER!')
        self.display_scores()



if __name__ == '__main__':
    def dump(obj):
        for attr in dir(obj):
            if not attr.startswith('_'):
                print(f'obj.{attr} = {getattr(obj, attr)}')


    game = Qwixx(['Evan', 'Megan'])
    game.begin_game()



    # game.display_scores()
    # game.display_all_boards()
    # game.move('Evan', 'red', 5)
    # game.display_all_boards()
    # game.move('Evan', 'red', 6)
    # game.display_all_boards()
    # game.display_scores()
