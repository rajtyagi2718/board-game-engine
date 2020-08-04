import unittest
from board_games.base_class.board import Board
from board_games.base_class.agent import Agent
from board_games.base_class.game import Game

class BoardTestCase(unittest.TestCase):

    def test_init(self):
        board = Board((3, 3))
        self.assertEqual(0, len(board))
        self.assertEqual(0, hash(board))
        self.assertEqual(1, board.turn()) 
        self.assertEqual(2, board.other()) 

class AgentTestCase(unittest.TestCase):

    def test_init(self):
        agent = Agent('testagent', None)
        print(agent)

class GameTestCase(unittest.TestCase):

    def test_init(self):
        game = Game('', None, None, None) 
        print(game)
