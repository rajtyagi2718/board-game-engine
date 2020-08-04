import unittest
from board_games.tictactoe.board import TicTacToeBoard

class TicTacToeBoardTestCase(unittest.TestCase):

    def setUp(self):
        board = TicTacToeBoard()
    
    def tearDown(self): 
        del board
