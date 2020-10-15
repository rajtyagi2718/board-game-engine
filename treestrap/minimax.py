import numpy as np
from pathlib import Path
from operator import lt, gt
import sys

from logs.log import get_logger
from board_games.tictactoe.board import TicTacToeBoard
from board_games.connectfour.board import ConnectFourBoard
from board_games.checkers.board import CheckersBoard
from board_games.go.board import GoBoard

np.set_printoptions(threshold=sys.maxsize)

LOGGER = get_logger(__name__)

BOARDS = dict(zip('tictactoe connectfour checkers go'.split(' '),
                  (TicTacToeBoard, ConnectFourBoard, CheckersBoard, GoBoard)))

WEIGHTS_PATHS = {name : Path('models/weights/' + name + '.txt')
                 for name in BOARDS}

class TreeStrapMinimax:
    """Learn board state values by minimax search with self-play TD updates."""

    def __init__(self, name, depth, alpha):
        self._name = name
        self._board = BOARDS[name]()
        self._weights = self._get_weights()
        self._depth = depth
        self._alpha = alpha
        self._tree = set()
        self._delta = np.zeros(self._weights.shape, dtype=np.float64)
        self._max_delta = 0

    def _info(self):
        return 'GAME: {}\tDEPTH: {}\tALPHA: {}\tMAX DELTA: {}'.format(
                self._name, self._depth, self._alpha, self._max_delta)

    def runs(self, num_runs):
        self._max_delta = 0
        LOGGER.info(self._info() + '\nNUM RUNS: {}'.format(num_runs))
        for r in range(num_runs):
            self._board.clear()
            self._run()
            LOGGER.info(self._info() + '\nRUNS: {}'.format(r))
            print('runs: {}'.format(r))
        self._save_weights()

    def _run(self):
        self._max_delta = 0
        while self._board:
            self._step()  
        return self._board.winner

    def _step(self):
        self._tree.clear()
        self._delta[:] = 0
        action, _ = self._explore(self._depth)
        self._weights += self._delta  
        self._max_delta = max(self._max_delta, np.linalg.norm(self._delta))
        print('STEP DELTA: {}'.format(np.linalg.norm(self._delta)))
        LOGGER.info(self._info() + '\nACTION: {!s}'.format(action))
        self._board.append(action)
        LOGGER.info(self._info() + '\nBOARD:\n{!s}'.format(self._board))

    def _explore(self, depth):
        if self._cutoff_test(depth):
            return None, self._evaluate_board()

        best_action = None

        if self._board.turn() == 1:
            better = gt
            best_value = -float('inf')
        else:
            better = lt
            best_value = float('inf')

        for action in self._board.legal_actions():
            self._board.append(action)
            _, child_value = self._explore(depth-1)
            if better(child_value, best_value):
                best_action = action
                best_value = child_value
            self._board.pop()

        self._update_delta(best_value)
        self._tree.add(hash(self._board))

        return best_action, best_value

    def _cutoff_test(self, depth):
        """Return bool to end explore recursion.

        Return True if depth from initial state reached, board is terminal,
        or board is a transposition i.e. already explored.

        """
        return not depth or not self._board or hash(self._board) in self._tree

    def _evaluate_board(self):
        """Return board state value by linear approx or terminal utility."""
        if self._board:
            return self._board.heuristic() @ self._weights
        return self._board.utility()

    def _update_delta(self, value):
        """Accumulate delta gradient. Step weights towards search value."""
        heuristic = self._board.heuristic() @ self._weights
        delta = value - heuristic 
        self._delta += self._alpha * delta * self._weights

    def _get_weights(self): 
        """Return weights from file or randomize with small values."""
        path = WEIGHTS_PATHS[self._name]
        try:
            result = np.loadtxt(path, delimiter='\n', dtype=np.float64)
        except IOError:
            shape = self._board.heuristic().shape
            result = np.empty(shape, dtype=np.float64)
            rng = np.random.default_rng()
            # random small floats
            result[:] = rng.random(shape) * rng.choice((-1e-5, 1e-5))
        return result 

    def _save_weights(self):
        """Save weights to file."""
        path = WEIGHTS_PATHS[self._name]
        np.savetxt(path, self._weights, delimiter='\n') 
        LOGGER.info(self._info())
