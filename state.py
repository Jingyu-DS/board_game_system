import copy

# Memento Pattern

class GameState:  
    """
    Game state class to save the current state of the board game
    Each state is saved as an instance of the class, if redo/undo is applicable
    """
    def __init__(self, game):
        """
        Initiate an instance with the deep copy of current game in order to save the current game state
        """
        self.boards = copy.deepcopy(game.boards)
        self.players = copy.deepcopy(game.players)
        self.turn = game.turn
        self.current = game.current
        self.focus = copy.deepcopy(game.focus)
    
    def restore(self, game):
        """
        Restore a game state 
        """
        game.boards = copy.deepcopy(self.boards)
        game.players = copy.deepcopy(self.players)
        game.turn = self.turn
        game.current = self.current
        game.focus = copy.deepcopy(self.focus)
    

class Caretaker:
    """
    The class is designed to save the history of game states in order to faciliate undo functionality
    and the future of game states in order to faciliate the redo functionality
    """
    def __init__(self, originator):
        """
        Initiate hitory and future records of game states
        """
        self._originator = originator
        self._history = []  
        self._future = []   
    
    def backup(self):
        """
        Save the game state
        """
        state = GameState(self._originator)
        self._history.append(state)
        self._future.clear()  
    
    def undo(self):
        """
        Complete the undo
        """
        if len(self._history) < 1:
            return None
        
        memento = copy.deepcopy(self._history.pop())
        self._future.append(GameState(self._originator))
        self._originator.restore_state(memento)
        return memento
    
    def redo(self):
        """
        Complete the redo
        """
        if len(self._future) < 1:
            return None
        
        memento = copy.deepcopy(self._future.pop())
        self._history.append(GameState(self._originator))
        self._originator.restore_state(memento)
        return memento
    

