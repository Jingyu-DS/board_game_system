"""
Design some variables that are needed across the program:
DIRECTIONS: key is the possible directions, value defines how the coordinates would change for the required directions
"n" -> north, move up on the board
"s" -> south, move down on the board
"e" -> east, move left on the board
"w" -> west, move right on the board

TIMESHIFT: key is the time travel direction, value defines how the current board index would change based on the movements
"f" -> foward (from past to present, from present to future)
"b" -> backward (from future to present, from present to past)

ERAS: In total, there are three eras in the game

weights: they are used for some player type to evaluate their potential moves with the most gains
based on several criterion
The weights can be changed here
"""


DIRECTIONS = {'n': (-1, 0), 's': (1, 0), 'e': (0, 1), 'w': (0, -1)}
TIMESHIFT = {'f': 1, 'b': -1}
ERAS = ['past', 'present', 'future']
w1, w2, w3, w4, w5 = 3, 2, 1, 1, 1