
from game import Game

# Decorator Pattern

class GameComponent:
    def play(self): 
        raise NotImplementedError
    
    def print_board(self): 
        raise NotImplementedError


class BaseGame(Game, GameComponent):
    """Class to initiate the base game mode"""
    def __init__(self, player1, player2, current=0, use_history=True, verbose=True):
        super().__init__(player1, player2, current, use_history, verbose)


class PlayDecorator(GameComponent):
    """p
    Use decorator pattern to add game playing mode and potential redo and undo functionality
    """
    def __init__(self, game: GameComponent):
        self._game = game
    

    def play(self):
        """
        Main play loop
        """
        while True:
            self._game.print_board()
            if self._game.display_eval:
                self._game.current_player().display_eval(self._game)
            if self._game.is_winning_move(self._game.current_player()):
                print(f"{self._game.get_opponent().color} has won")
                if input("Play again? (yes/no): ").strip().lower() == 'yes':
                    player1 = type(self._game.players[0])(self._game.players[0].color)
                    player2 = type(self._game.players[1])(self._game.players[1].color)
                    self._game.__init__(player1, player2, self._game.current, self._game.caretaker is not None, self._game.display_eval)
                    continue
                else:
                    break
            if self._game.caretaker:
                cmd = input("undo, redo, or next\n").strip()
                if cmd == 'undo':
                    self._game.caretaker.undo()
                    continue
                elif cmd == 'redo':
                    self._game.caretaker.redo()
                    continue
                elif cmd != "next":
                    continue
            self._game.save_state()
            player = self._game.current_player()
            move = player.select_move(self._game)
            if move:
                move.apply(self._game)
                self._game.turn += 1
                self._game.current = 1 - self._game.current
    
    def print_board(self): 
        self._game.print_board()