import unittest
from board_games.tictactoe.game import TicTacToeGame
from board_games.connectfour.game import ConnectFourGame
from board_games.checkers.game import CheckersGame
from board_games.base_class.agent import RandomAgent

GAMES = [TicTacToeGame, ConnectFourGame, CheckersGame]
GAMES = [CheckersGame]

class GameTestCase(unittest.TestCase):

    def test_compete(self):
        for Game in GAMES:
            with self.subTest(game=Game.__name__):
                game = Game(RandomAgent('random1'), RandomAgent('random2'))
                game.compete(1000)
                self.assertEqual(game._agent1._record['wins'], 
                                 game._agent2._record['losses'])
                self.assertEqual(game._agent1._record['losses'], 
                                 game._agent2._record['wins'])
                self.assertEqual(game._agent1._record['draws'], 
                                 game._agent2._record['draws'])
