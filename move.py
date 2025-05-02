# Command Pattern 


class Move:
    """
    Move class to define each move chosen by players containing the first direction, second direction
    and the new focus
    """
    def __init__(self, piece, dir1, dir2, focus_next):
        """
        Save the movements with piece to be moved, direction 1 and 2, next focus
        """
        self.piece = piece
        self.dir1 = dir1
        self.dir2 = dir2
        self.focus_next = focus_next

    def apply(self, game):
        """
        Officially complete the movements
        """
        if self.piece:
            game.move_piece(self.piece, self.dir1)
            game.move_piece(self.piece, self.dir2)
        game.focus[game.current_player().color] = self.focus_next
