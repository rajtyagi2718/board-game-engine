import unittest
import random
import copy
from pathlib import Path
from collections import deque
from board_games.tictactoe.game import TicTacToeGame
from board_games.connectfour.game import ConnectFourGame
from board_games.checkers.game import CheckersGame
from board_games.go.game import GoGame
from board_games.base_class.agent import RandomAgent

GAMES = [TicTacToeGame, ConnectFourGame, CheckersGame, GoGame]

class GameTestCase(unittest.TestCase):

    def setUp(self):
        dirpath = Path('data/')
        dirpath.mkdir(parents=True, exist_ok=True)
        self.logger = dirpath / 'game_test_log.txt' 
        with self.logger.open('w') as f:
            f.write('GAME TEST CASES')

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
                for game_num in range(10):
                    with self.subTest(game_num=game_num):
                        game.clear()
                        game.test_run(step_prob=.7, cache_size=10)

def GameUndoFactory(Game):
    """Return extension of Game class with undo step method, testcase ref."""

    class GameUndo(Game):

        def __init__(self, test_case, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._test_case = test_case

        def undo(self):
            """Undo last action."""
            self._board.pop() 

        def test_run(self, step_prob, cache_size):
            """Take steps or undo until board is terminal. Return winner."""
            board_cache = deque() 

            while self._board:
                with self._test_case.subTest(move_num=len(self._board)):
                    if random.random() < step_prob or not len(self._board):
                        board_cache.append(copy.deepcopy(self._board))
                        if len(board_cache) > cache_size:
                            board_cache.popleft() 
                        self.step()

                    else:
                        last_action = self._board[-1] 
                        self.undo()
                        if board_cache:
                            cached = board_cache.pop()
                            if cached != self._board:
                                with self._test_case.logger.open('a') as f:
                                    f.write('\n\nFAILED UNDO')
                                    f.write('\nGAME NAME: %s' % self._name)
                                    actions = list(self._board) + [last_action]
                                    actions = '\n'.join('%d: %s' % (i, x) 
                                        for i, x in enumerate(actions))
                                    f.write('\nACTIONS:\n%s' % actions)
                                    f.write('\nBOARD CACHE:')
                                    board_cache.append(cached)
                                    for board in board_cache:
                                        f.write('\n\n%s' % board._state())

                                    f.write('\n\nBOARD UNDO:\n%s' % 
                                        self._board._state()) 
                                    
                                self._test_case.assertTrue(False,'undo failed')
                                print('failed undo step', len(self._board))
                                break
                        
            self._update_records() 
            return self._board.winner

    return GameUndo
