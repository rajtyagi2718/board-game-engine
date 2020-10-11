from board_games.base_class.game import Game
from board_games.tictactoe.board import TicTacToeBoard

class TicTacToeGame(Game):

    def __init__(self, agent1, agent2):
        super().__init__('tictactoe', TicTacToeBoard(), agent1, agent2)
