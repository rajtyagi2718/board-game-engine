import unittest

from games.games import GAMES
from agents.random import RandomAgent
from agents.heuristic import HeuristicAgent

class AgentTestCase(unittest.TestCase):

    def test_random_agent(self):
        for Game in GAMES.values():
            with self.subTest(game=Game.__name__):
                game = Game(RandomAgent('random1'), RandomAgent('random2'))
                game.compete(3)

    def test_heuristic_agent(self):
        for Game in GAMES.values():
            with self.subTest(game=Game.__name__):
                game = Game(HeuristicAgent('heuristic1'), RandomAgent('heuristic2'))
                game.compete(3)
