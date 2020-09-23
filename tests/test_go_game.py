import unittest
import random
from collections import namedtuple
from pathlib import Path
from board_games.go.game import GoGame
from board_games.base_class.agent import RandomAgent, TestAgent

class GoGameTestCase(unittest.TestCase):

    def setUp(self):
        dirpath = Path('data/')
        dirpath.mkdir(parents=True, exist_ok=True)
        self.logger_file_path = dirpath / 'go_game_test_log.txt' 
        with self.logger_file_path.open('w') as f:
            f.write('GO GAME TEST CASES')

    def _test_capture(self):
        with self.logger_file_path.open('a') as f:
            f.write('\n\nCAPTURE TEST CASES')
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

        capseq = CaptureSequence('failed previously',
                                 (40, 23, 55, 13, 45, 6, 50, 37, 3, 70, 54, 77, 57, 22, 67, 19, 60, 72, 34, 42, 79, 51, 52, 43, 10, 58, 71, 56, 12, 4, 61, 38, 2, 44, 78, 69, 1, 38, 6, 30, 18, 53, 40, 33, 72, 2, 18, 38, 23, 12, 64, 18, 1, 3, 68, 2, 12, 66),
                                 (76, 68, 14, 5, 36, 35, 39, 80, 49, 69, 75, 59, 53, 74, 15, 17, 11, 27, 46, 25, 24, 21, 20, 32, 31, 66, 8, 7, 29, 48, 80, 26, 47, 41, 28, 63, 64, 59, 9, 65, 62, 16, 73, 37, 0, 13, 76, 19, 75, 65, 4, 73, 74, 10, 3, 1, 59)) 
        capture_sequences.append(capseq)

        for name, actions1, actions2 in capture_sequences:
            with self.subTest(capture_name=name):
                game = GoGame(TestAgent('test1', actions1), 
                              TestAgent('test2', actions2))
                with self.logger_file_path.open('a') as f:
                    f.write('\n\nCAPTURE SEQUENCE: %s' % (name))
                game.clear()
                for _ in range(len(actions1) + len(actions2)):
                    with self.subTest(move_num=len(game._board)+1):
                        game.step() 
                        with self.logger_file_path.open('a') as f:
                            f.write('\n\n')
                            f.write(game._board._state())
                        self._legal_state(game)

    def test_compete(self):
        game = GoGame(RandomAgent('random1'), RandomAgent('random2'))
        with self.logger_file_path.open('a') as f:
            f.write('\n\nCOMPETE TEST CASES')
        for game_num in range(100):
            with self.logger_file_path.open('a') as f:
                f.write('\n\nGAME: %d' % (game_num))
                
            with self.subTest(game_num=game_num):
                game.clear()
                while game._board:
                    with self.subTest(move_num=len(game._board)):
                        game.step()
                        with self.logger_file_path.open('a') as f:
                            f.write('\n\n')
                            f.write(game._board._state())
                        self._legal_state(game)

    def _legal_state(self, game):
        """Check game board components in legal state. Log, assert if not."""
        for (dfs, grp) in zip(
            self._dfs_components(game), self._board_components(game)):
            # components same
            if dfs != grp:
                with self.logger_file_path.open('a') as f:
                    f.write('\nILLEGAL STATE' + '*'*66)
                    # f.write('\nACTIONS: %s' % list(game._board))
                    f.write('\nDFS INDEX: %s\nCOMPONENT: %s \nLIBERTIES: %s'
                            % dfs)
                    f.write('\nGRP INDEX: %s\nCOMPONENT: %s \nLIBERTIES: %s'
                            % grp)
                self.assertTrue(False, 'different components')

            # component left uncaptured
            component, liberties = dfs[-2:]
            if not liberties and game._board._board[next(iter(component))]:
                with self.logger_file_path.open('a') as f:
                    f.write('\nILLEGAL STATE' + '*'*66)
                    f.write('\nDFS INDEX: %s\nCOMPONENT: %s \nLIBERTIES: %s'
                            % dfs)
                    f.write('\nGRP INDEX: %s\nCOMPONENT: %s \nLIBERTIES: %s'
                            % grp)
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
