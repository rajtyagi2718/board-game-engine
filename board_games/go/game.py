from board_games.base_class.game import Game
from board_games.go.board import GoBoard

class GoGame(Game):

    def __init__(self, agent1, agent2):
        super().__init__('go', GoBoard(), agent1, agent2)

