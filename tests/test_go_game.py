import unittest
import random
from collections import namedtuple

from logs.log import get_logger
from games.games import GAMES['go'] as GoGame
from agents.random import RandomAgent
from tests.agent import TestAgent

LOGGER = get_logger(__name__)

class GoGameTestCase(unittest.TestCase):

    def test_capture(self):
        CaptureSequence = namedtuple('capture_sequence', 
                                     'name actions1 actions2')
        capture_sequences = []
        capseq = CaptureSequence('corner single',
                                 (0, 8, 17), 
                                 (1, 9))
        capture_sequences.append(capseq)
        capseq = CaptureSequence('edge single',
                                 (4, 8, 17, 26),
                                 (3, 5, 13))
        capture_sequences.append(capseq)
        capseq = CaptureSequence('middle single',
                                 (22, 8, 17, 26, 35),
                                 (21, 23, 13, 31))
        capture_sequences.append(capseq)
        capseq = CaptureSequence('corner double',
                                 (0, 1, 8, 17), 
                                 (2, 9, 10))
        capture_sequences.append(capseq)
        capseq = CaptureSequence('edge double',
                                 (3, 4, 8, 17, 26),
                                 (2, 5, 12, 13))
        capture_sequences.append(capseq)
        capseq = CaptureSequence('middle double',
                                 (22, 31, 8, 17, 26, 35, 44),
                                 (21, 23, 13, 30, 32, 40))
        capture_sequences.append(capseq)

        for name, actions1, actions2 in capture_sequences:
            with self.subTest(capture_name=name):
                game = GoGame(TestAgent('test1', actions1), 
                              TestAgent('test2', actions2))
                LOGGER.debug('CAPTURE SEQUENCE {}'.format(name))
                game.clear()
                for m in range(1, len(actions1) + len(actions2) + 1):
                    with self.subTest(move_num=m):
                        game.step() 
                        self._test_legal_state(game)

    def test_compete_legal_state(self):
        game = GoGame(RandomAgent('random1'), RandomAgent('random2'))
        for game_num in range(1, 11):
            with self.subTest(game_num=game_num):
                LOGGER.debug('GAME {}'.format(game_num))
                game.clear()
                while game._board:
                    with self.subTest(move_num=len(game._board)):
                        game.step()
                        self._test_legal_state(game)

    def test_repeated_state(self):
        RepeatedSequence = namedtuple('repeated_sequence', 
                                      'name actions1 actions2 illegal')
        repeated_sequences = []
        repseq = RepeatedSequence('ko 1-1',
                                  (1, 9, 19, 11, 11),
                                  (2, 12, 20, 10),
                                  True)
        repeated_sequences.append(repseq)
        repseq = RepeatedSequence('ko 1-1-2',
                                  (1, 9, 19, 11, 80, 11),
                                  (2, 12, 20, 10, 79),
                                  False)
        repeated_sequences.append(repseq)
        repseq = RepeatedSequence('ko 1-2',
                                  (80, 2, 12, 20, 10),
                                  (1, 9, 19, 11, 11),
                                  True)
        repeated_sequences.append(repseq)
        repseq = RepeatedSequence('ko 2-1',
                                  (9, 1, 11, 19, 19),
                                  (18, 28, 20, 10),
                                  True)
        repeated_sequences.append(repseq)
        repseq = RepeatedSequence('ko 2-1-2',
                                  (9, 1, 11, 19, 80, 19),
                                  (18, 28, 20, 10, 79),
                                  False)
        repeated_sequences.append(repseq)
        repseq = RepeatedSequence('ko 2-2',
                                  (80, 18, 28, 20, 10),
                                  (9, 1, 11, 19, 19),
                                  True)
        repeated_sequences.append(repseq)

        for name, actions1, actions2, illegal in repeated_sequences:
            with self.subTest(repeated_name=name):
                LOGGER.debug('REPEATED SEQUENCE {}'.format(name))
                game = GoGame(TestAgent('test1', actions1), 
                              TestAgent('test2', actions2))
                game.clear()
                for _ in range(len(actions1) + len(actions2) - 1):
                    game.step() 
                if illegal:
                    try:
                        game.step()
                    except AssertionError:
                        continue    
                    LOGGER.debug('ILLEGAL REPEATED STATE\n{}'.format(
                                 game._board.debug())
                    self.assertTrue(False, 'illegal repeated state')
                    break 
                else:
                    try:
                        game.step()
                    except AssertionError:
                        with self.logger_file_path.open('a') as f:
                            LOGGER.debug('LEGAL REPEATED STATE\n' +
                                         game._board.debug())
                        self.assertTrue(False, 'legal repeated state')
                        break 
        
                
    def _test_legal_state(self, game):
        """Check game board components in legal state. Log, assert if not."""
        for (dfs, grp) in zip(
            self._dfs_components(game), self._board_components(game)):
            # components same
            if dfs != grp:
                msg = 'ILLEGAL STATE'
                msg += '\nACTIONS {!s}'.format(list(game._board))
                msg += '\nDFS INDEX %s\nCOMPONENT %s \nLIBERTIES %s' % dfs
                msg += '\nGRP INDEX %s\nCOMPONENT %s \nLIBERTIES %s' % grp
                LOGGER.debug(msg)
                self.assertTrue(False, 'different components')

            # component left uncaptured
            component, liberties = dfs[-2:]
            if not liberties and game._board._board[next(iter(component))]:
                with self.logger_file_path.open('a') as f:
                    msg = 'ILLEGAL STATE'
                    msg += '\nDFS INDEX %s\nCOMPONENT %s \nLIBERTIES %s'%dfs
                    msg += '\nGRP INDEX %s\nCOMPONENT %s \nLIBERTIES %s'%grp
                    LOGGER.debug(msg)
                self.assertTrue(False, 'captured component')

    def _dfs_components(self, game):
        """Return lists of components, liberties. Depth first search."""
        visited = [False]*81 

        for i in range(81):
            if visited[i]:
                continue
            piece = game._board._board[i]
            if not piece:
                yield (i, {i}, set(adj for adj in game._board._adjs[i]
                                      if not game._board._board[adj]))
                continue

            stack = [i]
            component = set()
            liberties = set()
            # threats = set()

            while stack:
                j = stack.pop()
                if visited[j]:
                    continue
                visited[j] = True
                component.add(j)
                for adj in game._board._adjs[j]:
                    if not game._board._board[adj]:
                        liberties.add(adj)
                    elif game._board._board[adj] == piece:
                        stack.append(adj)
                    # else:
                    #     threats.add(adj)
            
            yield (i, component, liberties)

    def _board_components(self, game):
        """Return lists of components, liberties. From groups data."""
        visited = [False]*81 
        groups = game._board._groups

        for i in range(81):
            if visited[i]:
                continue

            component = set(game._board._components[groups.root(i)])
            for j in component:
                visited[j] = True
            liberties = set(game._board._liberties[groups.root(i)])

            yield (i, component, liberties)
