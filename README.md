## Board Game Implementation with Interactive GUI

Main Components of my design contain Board, Piece and Player are the main components of the game. State, states of the game, and Move, the chosen movements of the player, represent
the actions and changes ongoing in the game. Game itself contains implementations of game rules, such as squishing, paradox, and feasibility of piece travel within/across boards.

I implement three different player types, human, random AI and Heuristic AI. There are also scenarios when different players might behave differently, such as how to react when a
piece is in the current board (prompt or random).

All the snapshots of the game are recorded within the CareTaker for the game to restore the previous/next state: the undo action gets a memento from the history and saves the current state to the future while the redo action gets a memento from the future and moves it to the history. When the player chooses to move to the next, the snapshot of the current state is saved to the history and the future will be cleared at that time.
