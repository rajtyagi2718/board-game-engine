import unittest
from board_games.base_class.board import Board
from board_games.base_class.agent import Agent

class BoardTestCase(unittest.TestCase):

   def test_run(self):
       board = Board((3, 3))
       self.assertEqual(0, len(board))
       self.assertEqual(0, hash(board))
       self.assertEqual(1, board.turn()) 
       self.assertEqual(2, board.other()) 

class AgentTestCase(unittest.TestCase):

   def test_run(self):
        agent = Agent('testagent', None)
        print(agent)
