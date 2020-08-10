from board_games.base_class.game import Game
from board_games.connectfour.board import ConnectFourBoard

class ConnectFourGame(Game):

    def __init__(self, agent1, agent2):
        super().__init__('connect-four', ConnectFourBoard(), agent1, agent2)

