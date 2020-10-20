import unittest

from games.games import GAMES
from agents.random import RandomAgent
from agents.heuristic import HeuristicAgent

class AgentTestCase(unittest.TestCase):

    def test_random_agent(self):
        for Game in GAMES.values():
            with self.subTest(game=Game.__name__):
                game = Game(RandomAgent('random1'), RandomAgent('random2'))
                game.runs(10)

    def test_heuristic_agent(self):
        for Game in GAMES.values():
            with self.subTest(game=Game.__name__):
                game = Game(HeuristicAgent('minimax'), RandomAgent('random'))
                game.compete(10)
                self.assertEqual(game._agent1._record['losses'], 0)
                
                game = Game(HeuristicAgent('minimax1'), 
                            HeuristicAgent('minimax2'))
                game.compete(10)
                self.assertEqual(game._agent1._record['wins'], 0)
                self.assertEqual(game._agent1._record['losses'], 0)
                self.assertEqual(game._agent2._record['wins'], 0)
                self.assertEqual(game._agent2._record['losses'], 0)
