'''
Let's make a Klondike solitaire game 
We'll do the easy mode where you only flip over 1 card from stock to wastes at a time
We could do more, but 


Needed operations:
1. begin the game
2. display the game board
3. display possible moves (help)


Card Object
Each of the 52 cards in the deck will be represented as an object
    -probably use itertools.combinations to generate these, once i've defined the card class'


Stack Object
There are 13 stacks in the game:
    1. tableau 1
    2. tableau 2
    3. tableau 3
    4. tableau 4
    5. tableau 5
    6. tableau 6
    7. tableau 7
    8. stock (the deck)
    9. wastes (the discard)
    10. foundation_hearts
    11. foundation_diamonds
    12. foundation_club
    13. foundation_spades
    
    
Rules:
    
1. Lay out the cards
2. a card may be placed on a tablea if it is a different color, and one rank less
3. a card may be placed on a blank foundation if it is 
4. 
    




Some day, when we build a ML model for this game, we should give points for cards placed into the foundation, but also penalty based on how many moves are taken


'''

import pygame
import itertools as iter



# =============================================================================
# Card Class
# =============================================================================

# Info: rank, suit, color, rank value (1-13)
# Operations



# =============================================================================
# Pile Class
# =============================================================================





    