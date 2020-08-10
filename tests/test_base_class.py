import unittest
from board_games.base_class.board import get_hashes
from board_games.base_class.agent import RandomAgent
from board_games.base_class.game import Game

class BoardTestCase(unittest.TestCase):

    def test_get_hashes(self):
        num_pieces_ = [3, 3, 7]
        sizes = [9, 42, 64]
        for num_pieces, size in zip(num_pieces_, sizes):
            with self.subTest(num_pieces=num_pieces, size=size):
                hashes = get_hashes(num_pieces, size)
                for piece in range(num_pieces):
                    for position in range(size):
                        with self.subTest(piece=piece, position=position):
                            s = str(piece) + '0'*position
                            self.assertEqual(int(s, num_pieces), 
                                             piece * hashes[position])                

class RandomAgentTestCase(unittest.TestCase):

    def test_init(self):
        agent = RandomAgent()

class GameTestCase(unittest.TestCase):

    def test_init(self):
        game = Game('', None, None, None) 
