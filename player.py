
from abc import ABC, abstractmethod
from move import Move
import copy
import random
from piece import Piece
from constants import DIRECTIONS, TIMESHIFT, ERAS
from best_move import HighestScoreMoveIterator

# Template Pattern

class Player(ABC):
    """
    Template class for different player types, including starter, game evaluation
    """
    def __init__(self, color, supply = 7):
        """
        Initiate the player including the color of pieces they will play, all pieces supplied based on the color
        """
        self.color = color
        self.pieces = []
        self.supply = supply
        if self.color == "white":
            self.symbols = [chr(65 + i) for i in range(self.supply)]
        else:
            self.symbols = [str(i + 1) for i in range(self.supply)]
    
    def start(self):
        """
        Place the pieces at the start of the game required
        """
        for era in ERAS:
            symbol = self.symbols.pop(0)
            if self.color == "white":
                x, y = 3, 3
            else:
                x, y = 0, 0
            self.supply -= 1 
            self.pieces.append(Piece(symbol, self.color, era, x, y))
    
    def _check_era(self, game):
        """
        Check whether the current board has an active piece or not
        """
        current_era = game.focus[self.color]
        count = 0
        for piece in self.pieces:
            if piece.era == current_era:
                count += 1
        return count == 0
    
    def eval(self, game):
        """
        Criterion to evaluate the current state:
        era presence, piece advantage, supply, centrality, focus
        """
        c1 = len(set(p.era for p in self.pieces))
        opponent = game.players[1 - game.players.index(self)]
        c2 = len(self.pieces) - len(opponent.pieces)
        c3 = self.supply
        c4 = sum(1 for p in self.pieces if 1 <= p.x <= 2 and 1 <= p.y <= 2)
        c5 = sum(1 for p in self.pieces if p.era == game.focus[self.color])
        return c1, c2, c3, c4, c5
    
    def display_eval(self, game):
        """
        Show the scores of each criterion
        """
        opponent = game.get_opponent()
        cur_c1, cur_c2, cur_c3, cur_c4, cur_c5 = self.eval(game)
        op_c1, op_c2, op_c3, op_c4, op_c5 = opponent.eval(game)
        if self.color == "white":
            print(f"{self.color}'s score: {cur_c1} eras, {cur_c2} advantage, {cur_c3} supply, {cur_c4} centrality, {cur_c5} in focus")
            print(f"{opponent.color}'s score: {op_c1} eras, {op_c2} advantage, {op_c3} supply, {op_c4} centrality, {op_c5} in focus")
        else:
            print(f"{opponent.color}'s score: {op_c1} eras, {op_c2} advantage, {op_c3} supply, {op_c4} centrality, {op_c5} in focus")
            print(f"{self.color}'s score: {cur_c1} eras, {cur_c2} advantage, {cur_c3} supply, {cur_c4} centrality, {cur_c5} in focus")

    @abstractmethod
    def score_system(self):
        """Score the movement based on the criterions"""
        pass

    def select_move(self, game):
        """Strategy to select moves based on the player type"""
        if self._check_era(game):
            return self._handle_no_pieces_move(game)
        else:
            return self._handle_normal_move(game)

    @abstractmethod
    def _handle_normal_move(self, game):
        """Handle situation when there is an active piece in the current era"""
        pass
    
    @abstractmethod
    def _handle_no_pieces_move(self, game):
        """Handle situation when there is no active pieces in the current era"""
        pass
    
    def _print_move(self, piece, dir1, dir2, next_focus):
        """Print out the selected moves and focus era coming next"""
        symbol = piece.symbol if piece else None
        print(f"Selected move: {symbol},{dir1},{dir2},{next_focus}")
        return Move(piece, dir1, dir2, next_focus)
    

    def _select_piece(self):
        """Action might be implemented in some subclasses"""
        pass

    def _select_direction(self):
        """Action might be implemented in some subclasses"""
        pass

    def _select_focus(self):
        """Action might be implemented in some subclasses"""
        pass




class HumanPlayer(Player):
    """
    Human Player Implementation with conversations to ask for user inputs
    """
    def score_system(self):
        """Human Player -> No automatic scoring system"""
        return 0  
    
    def _handle_normal_move(self, game):
        """Human player handles the stiuation when there is an active piece in the current era"""
        game_copy = copy.deepcopy(game)
        piece = self._select_piece(game)
        piece_copy = next((p for p in game_copy.current_player().pieces if p.symbol == piece.symbol), None)
        dir1 = self._select_direction(game_copy, piece_copy, "first")
        game_copy.move_piece(piece_copy, dir1)
        dir2 = self._select_direction(game_copy, piece_copy, "second")
        next_focus = self._select_focus(game)
        return self._print_move(piece, dir1, dir2, next_focus)
    
    def _handle_no_pieces_move(self, game):
        """Human player handles the situation when there is no active pieces in the current era"""
        print("No copies to move")
        next_focus = self._select_focus(game)
        return self._print_move(None, None, None, next_focus)
    
    def _select_piece(self, game):
        """Human player -> conversations to ask human player to choose the piece they want to move"""
        while True:
            print("Select a copy to move")
            symbol = input().strip()
            piece = game.find_piece(symbol)
            if not piece:
                print("Not a valid copy")
                continue
            if piece.color != self.color:
                print("That is not your copy")
                continue
            if piece.era != game.focus[self.color]:
                print("Cannot select a copy from an inactive era")
                continue
            return piece
    
    def _select_direction(self, game_copy, piece, move_number):
        """Human player -> conversations to ask human player to select direction they want to move the piece"""
        valid_dirs = list(DIRECTIONS.keys()) + list(TIMESHIFT.keys())
        while True:
            direction = input(f"Select the {move_number} direction to move ['n', 'e', 's', 'w', 'f', 'b']\n").strip()
            if direction not in valid_dirs:
                print("Not a valid direction")
                continue
            if not game_copy.can_move(piece, direction):
                print(f"Cannot move {direction}")
                continue
            return direction
    
    def _select_focus(self, game):
        """Human player -> conversations to ask human player to select their next focus era"""
        while True:
            next_focus = input("Select the next era to focus on ['past', 'present', 'future']\n").strip()
            if next_focus not in ERAS:
                print("Not a valid era")
                continue
            if next_focus == game.focus[self.color]:
                print("Cannot select the current era")
                continue
            return next_focus


class RandomAI(Player):
    """
    Random AI Implementation
    """
    def score_system(self, game, w1, w2, w3, w4, w5):
        """Random AI Player does not need a score system"""
        return 0  
    
    def _handle_normal_move(self, game):
        """Random AI player handles the stiuation when there is an active piece in the current era"""
        all_moves = game.enumerate_all_moves(self)
        piece, dir1, dir2, next_focus, _ = random.choice(list(all_moves))
        return self._print_move(piece, dir1, dir2, next_focus)
    
    def _handle_no_pieces_move(self, game):
        """Random AI player handles the situation when there is no active pieces in the current era"""
        all_moves = game.enumerate_all_moves(self)
        piece, dir1, dir2, next_focus, _ = random.choice(list(all_moves))
        return self._print_move(piece, dir1, dir2, next_focus)

class HeuristicAI(Player):
    """
    Heuristic AI Implementation
    """
    def score_system(self, game, w1, w2, w3, w4, w5):
        """Heuristic AI Player evaluate the movement based on the weights on each criteria"""
        c1, c2, c3, c4, c5 = self.eval(game)
        score = w1 * c1 + w2 * c2 + w3 * c3 + w4 * c4 + w5 * c5
        return score  
    
    def _handle_normal_move(self, game):
        """Heuristic AI player handles the stiuation when there is an active piece in the current era"""
        best_moves_iter = HighestScoreMoveIterator(game, self)
        best_piece, best_dir1, best_dir2, next_focus, _ = next(best_moves_iter)
        return self._print_move(best_piece, best_dir1, best_dir2, next_focus)
    
    def _handle_no_pieces_move(self, game):
        """Heuristic AI player handles the stiuation when there is no active piece in the current era"""
        best_moves_iter = HighestScoreMoveIterator(game, self)
        best_piece, best_dir1, best_dir2, next_focus, _ = next(best_moves_iter)
        return self._print_move(best_piece, best_dir1, best_dir2, next_focus)
