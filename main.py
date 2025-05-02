import sys
from play_game import BaseGame, PlayDecorator
from player import HumanPlayer, HeuristicAI, RandomAI

class Main:
    """
    Main function to start playing the game
    """
    @staticmethod
    def create_player(color, ptype):
        """
        Create players based on the input type
        """
        if ptype == 'human': 
            return HumanPlayer(color)
        if ptype == 'random': 
            return RandomAI(color)
        if ptype == 'heuristic': 
            return HeuristicAI(color)
        raise ValueError("Unknown player type")

    @staticmethod
    def run():
        """
        Main runner
        """
        args = sys.argv[1:]
        defaults = ['human', 'human', 'off', 'off']
        for i, arg in enumerate(args):
            if i < len(defaults):
                defaults[i] = arg.lower()

        p1_type, p2_type = defaults[0], defaults[1]
        use_history = defaults[2].lower() == 'on'
        verbose = defaults[3].lower() == 'on'

        p1 = Main.create_player("white", p1_type)
        p2 = Main.create_player("black", p2_type)
        game = BaseGame(p1, p2, current=0, use_history=use_history, verbose=verbose)
        game = PlayDecorator(game)
        game.play()

if __name__ == '__main__':
    Main.run()
