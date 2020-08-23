from board_games.base_class.game import Game
from board_games.checkers.board import CheckersBoard

class CheckersGame(Game):

    def __init__(self, agent1, agent2):
        super().__init__('checkers', CheckersBoard(), agent1, agent2)

