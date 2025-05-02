from board import Board
from state import Caretaker
from constants import DIRECTIONS, TIMESHIFT, ERAS, w1, w2, w3, w4, w5
from piece import Piece
import copy

class Game:
    """
    Main game class. It is used for illustrating the game contains three boards,
    two players, black and white, their intial focus, game setup, game state change.
    Some movement rules and restrictions are included as well, for example, squeeze, paradox.
    Potential movements based on the current game, enumerating them for potential use.
    """

    def __init__(self, player1, player2, current = 0, use_history = True, verbose = True):
        """
        Initiate a game with required components: two players, three boards for three eras, whether redo/undo is applicable
        whether there is evaluation display, current first starter
        """
        self.boards = {era: Board(era) for era in ERAS}
        self.players = [player1, player2]
        self.turn = 1
        self.current = current
        self.focus = {'white': 'past', 'black': 'future'}
        self.caretaker = Caretaker(self) if use_history else None
        self.display_eval = verbose
        self.setup()

    def setup(self):
        """
        Set up the game initiation state as required
        """
        self.players[0].start()
        self.players[1].start()
        for player in self.players:
            for piece in player.pieces:
                self.boards[piece.era].place_piece(piece)
    

    def save_state(self):
        """
        Save the current state of the game, if redo/undo functionality is on
        """
        if self.caretaker:
            self.caretaker.backup()

    def restore_state(self, memento):
        """
        Restore state from history, if undo is called
        """
        if memento:
            memento.restore(self)
    
    def find_player(self, color):
        """
        Helper function to find a player based on whether they play black or white pieces
        """
        for player in self.players:
            if player.color == color:
                return player

    def current_player(self):
        """
        Get the current player
        """
        return self.players[self.current]
    

    def get_opponent(self):
        """
        Get the opponent of the current player
        """
        return self.players[1 - self.current]

    def find_piece(self, symbol):
        """
        Find the piece that matches the input indicating the symbol of piece 
        """
        for player in self.players:
            for piece in player.pieces:
                if piece.symbol == symbol:
                    return piece
        return None
  

    def _move_temporal(self, piece, direction):
        """
        Complete the time travel of piece indicated by the input direction
        """
        current_player = self.current_player()
        dz = TIMESHIFT[direction]
        new_era_idx = ERAS.index(piece.era) + dz
        new_era = ERAS[new_era_idx]
        cur_board = self.boards[piece.era]
        new_board = self.boards[new_era]
        cur_board.remove_piece(piece.x, piece.y)
        new_board.place_piece(piece)
        if dz == -1:
            current_player.supply -= 1
            new_symbol = current_player.symbols.pop(0)
            new_piece = Piece(new_symbol, piece.color, piece.era, piece.x, piece.y)
            current_player.pieces.append(new_piece)
            cur_board.place_piece(new_piece)
        piece.era = new_era
        return
    
    def _move_current_board(self, piece, direction):
        """
        Complete the movement in the current board indicated by the input direction
        Considering any squeeze of pieces, any paradox of pieces
        """
        dx, dy = DIRECTIONS[direction]
        nx, ny = piece.x + dx, piece.y + dy
        cur_board = self.boards[piece.era]
        if not cur_board.is_within_bounds(piece.x, piece.y):
            return
        
        cur_board = self.boards[piece.era]
        if not cur_board.get_piece(nx, ny):
            cur_board.remove_piece(piece.x, piece.y)
            piece.x = nx
            piece.y = ny
            cur_board.place_piece(piece)
            return 
        
        if cur_board.get_piece(nx, ny):
            if self._squeeze_effect(cur_board, nx + dx, ny + dy):
                squeezed_piece = cur_board.get_piece(nx, ny)
                effected_player = self.find_player(squeezed_piece.color)
                effected_player.pieces.remove(squeezed_piece)
                cur_board.remove_piece(nx, ny)
                cur_board.remove_piece(piece.x, piece.y)
                piece.x = nx
                piece.y = ny
                cur_board.place_piece(piece)
                return
            if self._paradox_effect(cur_board, nx, ny, dx, dy):
                paradox_piece1 = cur_board.get_piece(nx, ny)
                paradox_piece2 = cur_board.get_piece(nx + dx, ny + dy)
                effected_player = self.find_player(paradox_piece1.color)
                effected_player.pieces.remove(paradox_piece1)
                effected_player.pieces.remove(paradox_piece2)
                cur_board.remove_piece(paradox_piece2.x, paradox_piece2.y)
                cur_board.remove_piece(piece.x, piece.y)
                piece.x = nx
                piece.y = ny
                cur_board.place_piece(piece)
                return
            nxt_piece = cur_board.get_piece(nx, ny)
            self._move_current_board(nxt_piece, direction)
            cur_board.remove_piece(piece.x, piece.y)
            piece.x = nx
            piece.y = ny
            cur_board.place_piece(piece)
        return

    def move_piece(self, piece, direction):
        """
        Complete the movement chosen
        """
        if direction in DIRECTIONS:
            self._move_current_board(piece, direction)
        elif direction in TIMESHIFT:
            self._move_temporal(piece, direction)

    def _squeeze_effect(self, board, x, y):
        """
        Game rule -> squeeze the piece and the piece is out
        """
        return not board.is_within_bounds(x, y)
    
    def _paradox_effect(self, board, x, y, dx, dy):
        """
        Game rule -> push a piece to another piece with the same color. Both are out
        """
        piece1 = board.get_piece(x, y)
        piece2 = board.get_piece(x + dx, y + dy)
        if piece1 and piece2 and piece1.color == piece2.color:
            return True
        return False

    def _can_time_travel(self, piece, direction):
        """
        Game rule -> based on the game rule, whether the piece can do the time travel
        """
        current_player = self.current_player()
        dz = TIMESHIFT[direction]
        new_era_idx = ERAS.index(piece.era) + dz
        if new_era_idx < 0 or new_era_idx > 2:
            return False
        if dz == -1 and current_player.supply <= 0:
            return False
        target_era = ERAS[new_era_idx]
        target_board = self.boards[target_era]
        if target_board.get_piece(piece.x, piece.y) is not None:
            return False
        return True
    
    def _can_current_era_move(self, piece, direction):
        """
        Game rule -> based on the game rule, whether the piece can move in the current board
        """
        current_board = self.boards[piece.era]
        dx, dy = DIRECTIONS[direction]
        nx, ny = piece.x + dx, piece.y + dy
        if not current_board.is_within_bounds(nx, ny):
            return False
        if self._paradox_effect(current_board, piece.x, piece.y, dx, dy): # self paradox
            return False
        return True
    
    def can_move(self, piece, direction):
        """
        Check whether the piece can make the desired movement based on the current state of game
        """
        if direction in DIRECTIONS:
            return self._can_current_era_move(piece, direction)
        if direction in TIMESHIFT:
            return self._can_time_travel(piece, direction)

    def _enumerate_moves(self, piece):
        """
        Enumerate all possible moves of the piece indicated
        """
        moves = set()
        dirs = list(DIRECTIONS.keys()) + list(TIMESHIFT.keys())
        if not piece:
            dir1, dir2 = None, None
            for era in ERAS:
                game_copy = copy.deepcopy(self)
                if era != self.focus[game_copy.current_player().color]:
                    game_copy.focus[game_copy.current_player().color] = era
                    if game_copy.is_winning_move(game_copy.get_opponent()):
                        score = 9999
                    else:
                        score = game_copy.current_player().score_system(game_copy, 3, 2, 1, 1, 1)
                    moves.add((piece, dir1, dir2, era, score))
            return moves

        for dir1 in dirs:
            for dir2 in dirs:
                game_copy = copy.deepcopy(self)
                piece_copy = next((p for p in game_copy.current_player().pieces if p.symbol == piece.symbol), None)
                if not piece_copy:
                    continue
                if not game_copy.can_move(piece_copy, dir1):
                    dir1, dir2 =  None, None
                    continue
                if dir1:
                    game_copy.move_piece(piece_copy, dir1)
                if dir1 and not game_copy.can_move(piece_copy, dir2):
                    dir1, dir2 =  None, None
                    continue
                if dir2:
                    game_copy.move_piece(piece_copy, dir2)
                for era in ERAS:
                    if era != piece.era:
                        game_copy.focus[piece_copy.color] = era
                        if game_copy.is_winning_move(game_copy.get_opponent()):
                            score = 9999
                        else:
                            score = game_copy.current_player().score_system(game_copy, w1, w2, w3, w4, w5)
                        if dir1 and dir2:
                            moves.add((piece, dir1, dir2, era, score))
        return moves

    def enumerate_all_moves(self, player):
        """
        Enumerate all moves for all potential pieces that can be moved
        """
        focus_board = self.focus[player.color]
        piece_options = []
        all_moves = []
        for piece in player.pieces:
            if piece.era == focus_board:
                piece_options.append(piece)
        if piece_options:
            for piece in piece_options:
                all_moves.extend(self._enumerate_moves(piece))
        else:
            all_moves.extend(self._enumerate_moves(None))
        return all_moves
  
    def is_winning_move(self, player):
        """
        Check whether the move can make the player win
        """
        presence = set(p.era for p in player.pieces)
        return len(presence) <= 1
           
    def print_board(self):
        """
        Print out the current boards based on the current state
        """
        print("-" * 33)
        def get_focus_line(color):
            idx = ERAS.index(self.focus[color])
            return " " * (12 * idx) + f"  {color}  "

        print(get_focus_line('black'))
        print(self._display_boards())
        print(get_focus_line('white'))
        print(f"Turn: {self.turn}, Current player: {self.current_player().color}")

    
    def _display_boards(self):
        """
        Helper function for print boards
        """
        lines = ["" for _ in range(9)]
        for era in ERAS:
            board_str = self.boards[era].display().splitlines()
            for i in range(9):
                lines[i] += board_str[i].ljust(9) + "   " 
        return "\n".join(line.rstrip() for line in lines)
    


              