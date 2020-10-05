from board_games.tictactoe.game import TicTacToeGame
from board_games.connectfour.game import ConnectFourGame
from board_games.checkers.game import CheckersGame
from board_games.go.game import GoGame
from board_games.base_class.agent import RandomAgent
from logs.log import get_logger

import logging
import unittest
import random
import copy
import numpy as np
from pathlib import Path
from collections import deque

LOGGER = get_logger(__name__, logging.DEBUG)

GAMES = [TicTacToeGame, ConnectFourGame, CheckersGame, GoGame]

class GameTestCase(unittest.TestCase):

    def test_compete(self):
        for Game in GAMES:
            with self.subTest(game=Game.__name__):
                game = Game(RandomAgent('random1'), RandomAgent('random2'))
                game.compete(10)
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
                game = GameUndo(self,
                                RandomAgent('random1'), RandomAgent('random2'))
                game.runs(10, step_prob=.7, cache_size=10)

def GameUndoFactory(Game):
    """Return extension of Game class with undo step method, testcase ref."""

    class GameUndo(Game):

        def __init__(self, test_case, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._test_case = test_case
            self._board_cache = deque()

        def undo(self):
            """Undo last action."""
            self._board.pop() 

        def _eq_attr(cls, attr1, attr2):
            """Generalize == operator to all operator for numpy arrays."""
            try:
                return bool(attr1 == attr2)
            except ValueError:
                return (attr1 == attr2).all()
            
        def _board_eq_attrs(cls, board1, board2):
            """Compare equality by instance attributes. Assume same keys."""
            return all(cls._eq_attr(getattr(board1, attr), 
                                    getattr(board2, attr))
                       for attr in board1.__dict__)

        def runs(self, num_runs, step_prob, cache_size):
            msg='STEP PROB: {}\tCACHE SIZE: {}'.format(step_prob, cache_size)
            LOGGER.debug(self._debug() + '\n' + msg)
            for r in range(num_runs):
                with self._test_case.subTest(game_num=r):
                    LOGGER.info('GAMES: {}'.format(r))
                    self.clear()
                    self.run(step_prob, cache_size)

        def run(self, step_prob, cache_size):
            self._board_cache.clear()
            while self._board:
                with self._test_case.subTest(move_num=len(self._board)):
                    LOGGER.info('MOVES: {}'.format(len(self._board)))
                    if random.random() < step_prob or not len(self._board):
                        self._board_cache.append(copy.deepcopy(self._board))
                        if len(self._board_cache) > cache_size:
                            self._board_cache.popleft() 
                        self.step()
                        continue

                    last_action = self._board[-1] 
                    last_hash = hash(self._board)
                    self.undo()
                    if not self._board_cache:
                        continue

                    cached = self._board_cache.pop()
                    if not self._board_eq_attrs(cached, self._board):
                        LOGGER.debug(self._debug_failed_undo_step(
                            last_action, last_hash))
                        self._test_case.assertTrue(False,'undo failed')
                        break
                        
            self._update_records() 
            return self._board.winner

        def _debug_failed_undo_step(last_action, last_hash):
            """Return debug message with board cache details."""
            msg = '\n\n' + self._debug()
            msg += '\nFAILED UNDO'
            actions = list(self._board) + [last_action]
            actions = '\n'.join('%d: %s' % (i, x) 
                for i, x in enumerate(actions))
            msg += '\nACTIONS:\n{!s}'.format(actions)
            msg += '\nBOARD CACHE:'
            self._board_cache.append(cached)
            for board in self._board_cache:
                msg += '\n\n{!s}'.format(board._debug())
            msg += '\n\nBOARD UNDO:\n{!s}'.format(self._board._debug())
            hashes = [hash(board) 
                      for board in self._board_cache]
            hashes.append(last_hash)
            msg += '\n\nBOARD HASHES:\n{!s}'.format(
                '\n'.join(str(x) for x in hashes))
            msg += '\n\nHASH ARRAY:\n{!s}'.format(self._board._hashes)
            return msg

        def _debug(self):
            return 'GAME UNDO: {!r}'.format(self)

    return GameUndo
