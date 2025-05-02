class Board:
    """This class is designed to create a board that is needed in the board game"""

    def __init__(self, era):
        """Attributes like ara is used to initiate the current board and the board contains grid which is represent by list"""
        self.era = era
        self.grid = [[None for _ in range(4)] for _ in range(4)]

    def place_piece(self, piece):
        """Place a piece on the board based on the piece's coordinates"""
        self.grid[piece.x][piece.y] = piece

    def remove_piece(self, x, y):
        """Remove the piece from its current position on the board"""
        self.grid[x][y] = None

    def move_piece(self, piece, x, y):
        """Move a piece from one coordinate to another coordinate on the board"""
        self.remove_piece(piece.x, piece.y)
        piece.x, piece.y = x, y
        self.place_piece(piece)

    def get_piece(self, x, y):
        """Get the piece based on the required coordinates. If not piece there, just return None"""
        if 0 <= x < 4 and 0 <= y < 4:
            return self.grid[x][y]
        return None

    def is_within_bounds(self, x, y):
        """Check the input coordinates are in the board or not -> Used for detecting squeezing a piece or checking available moves"""
        return 0 <= x < 4 and 0 <= y < 4
    
    def display(self):
        """Display the board in CLI to show how the board is currently like"""
        result = ""
        for row in self.grid:
            result += "+-+-+-+-+\n"
            result += "|" + "|".join(f"{p.symbol if p else ' '}" for p in row) + "|\n"
        result += "+-+-+-+-+"
        return result