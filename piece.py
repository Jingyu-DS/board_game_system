class Piece:
    """
    Piece class to define pieces in the board game
    """
    def __init__(self, symbol, color, era, x, y):
        """Each piece has attributes, including symbol, coordinates, color, era of its current board"""
        self.symbol = symbol
        self.color = color
        self.era = era
        self.x = x
        self.y = y

    def position(self):
        """Return the current position of piece"""
        return self.x, self.y

    def __str__(self):
        """Define the __str__ method -> might help for debugging or printing outputs"""
        return self.symbol