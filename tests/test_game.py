import unittest
import random
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
                game.compete(100)
                self.assertEqual(game._agent1._record['wins'], 
                                 game._agent2._record['losses'])
                self.assertEqual(game._agent1._record['losses'], 
                                 game._agent2._record['wins'])
                self.assertEqual(game._agent1._record['draws'], 
                                 game._agent2._record['draws'])

    def test_undo(self):
        for Game in GAMES:
            with self.subTest(game=Game.__name__):
                GameUndo = GameUndoFactory(Game)
                game_undo = GameUndo(RandomAgent('random1'),
                                     RandomAgent('random2'))
                game_undo.compete(100)
             


def GameUndoFactory(Game):
    """Return extension of Game class with undo step method."""

    class GameUndo(Game):

        def undo(self):
            """Undo last action."""
            print('Undo')
            self._board.pop() 

        def run(self):
            """Take steps or undo until board is terminal. Return winner."""
            while self._board:
                print(self._board)
                if random.random() < .5 or not len(self._board):
                    self.step()
                else:
                    self.undo()
            print(self)
            self._update_records() 
            return self._board.winner

    return GameUndo
