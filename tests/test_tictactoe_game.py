import unittest
import random
from board_games.tictactoe.game import TicTacToeGame
from board_games.base_class.agent import RandomAgent

class TicTacToeGameTestCase(unittest.TestCase):

    def setUp(self):
        self.game = TicTacToeGame(RandomAgent('random1'), RandomAgent('random2'))

    def tearDown(self):
        del self.game

    def test_compete(self):
        self.game.compete(10)
        self.assertEqual(self.game._agent1._record['wins'], 
                         self.game._agent2._record['losses'])
        self.assertEqual(self.game._agent1._record['losses'], 
                         self.game._agent2._record['wins'])
        self.assertEqual(self.game._agent1._record['draws'], 
                         self.game._agent2._record['draws'])
