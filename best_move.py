import random

# Iterator Pattern 

class HighestScoreMoveIterator:
    """
    This class is designed to iterate all the potential moves and 
    return an iterator that can gives a random move with the highest score,
    specifically design for Heuristic AI player
    """

    def __init__(self, game, player):
        """Initiate the process to create the best move iterator"""
        self.game = game
        self.player = player
        self.current_max_score = -float('inf')
        self.best_moves = []
        self._evaluated = False
        self._index = 0
        
    def _evaluate_moves(self):
        """Get all the potential moves, iterate to get the best moves with highest scores, shuffle them to break the ties"""
        if not self._evaluated:
            for move in self.game.enumerate_all_moves(self.player):
                _, _, _, _, score = move
                
                if score > self.current_max_score:
                    self.current_max_score = score
                    self.best_moves = [move]
                elif score == self.current_max_score:
                    self.best_moves.append(move)
            random.shuffle(self.best_moves)
            self._evaluated = True
    
    def __iter__(self):
        """iterator protocol: define __iter__"""
        self._evaluate_moves()
        self._index = 0  
        return self
    
    def __next__(self):
        """iterator protocol: define __next__"""
        self._evaluate_moves()
        if self._index < len(self.best_moves):
            result = self.best_moves[self._index]
            self._index += 1
            return result
        raise StopIteration