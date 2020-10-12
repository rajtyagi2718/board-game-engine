import logging
import unittest

from board_games.tictactoe.game import TicTacToeGame
from board_games.base_class.agent import HeuristicAgent, RandomAgent
from logs.log import get_logger

LOGGER = get_logger(__name__, logging.DEBUG)

GAMES = [TicTacToeGame]

class AgentTestCase(unittest.TestCase):

    def test_heuristic_agent(self):
        for Game in GAMES:
            with self.subTest(game=Game.__name__):
                game = Game(HeuristicAgent('minimax'), RandomAgent('random2'))
                game.compete(10)
                self.assertEqual(game._agent1._record['losses'], 0)
                
                game = Game(HeuristicAgent('minimax1'), 
                            HeuristicAgent('minimax2'))
                game.compete(10)
                self.assertEqual(game._agent1._record['wins'], 0)
                self.assertEqual(game._agent1._record['losses'], 0)
                self.assertEqual(game._agent2._record['wins'], 0)
                self.assertEqual(game._agent2._record['losses'], 0)
