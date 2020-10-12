import numpy as np
from pathlib import Path
from operator import lt, gt

from logs.log import get_logger
from board_games.tictactoe.board import TicTacToeBoard
from board_games.connectfour.board import ConnectFourBoard
from board_games.checkers.board import CheckersBoard
from board_games.go.board import GoBoard

LOGGER = get_logger(__name__)

BOARDS = dict(zip('tictactoe connectfour checkers go'.split(' '),
                  (TicTacToeBoard, ConnectFourBoard, CheckersBoard, GoBoard)))

WEIGHTS_PATHS = {name : Path('models/weights/' + name + '.txt')
                 for name in BOARDS}

class TreeStrapMinimax:
    """Learn board state values by minimax search with self-play TD updates."""

    def __init__(self, name, depth, alpha):
        self._name = name
        self._board = BOARDS[name]
        self._weights = self._get_weights(name)
        self._depth = depth
        self._alpha = alpha
        self._tree = set()
        self._delta = np.zeros(self._weights.shape, dtype=np.float64)

    def _get_weights(name): 
        path = WEIGHTS_PATHS[name]
        try:
            result = np.genfromtxt(path, delimiter='\n', dtype=np.float64)
        except IOError:
            result = np.empty(self._board.heuristic().shape, dtype=np.float64)
            rng = np.random.default_rng()
            # random small floats
            result[:] = self.rng.random(size) * self.rng.choice((-1e-5, 1e-5))
        return result 

    def _evaluate_board(self):
        if self._board:
            return self._board.heuristic() @ self._weights
        return self._board.utility()

    def _update_delta(self, value):
        heuristic = self._board.heuristic() @ self._weights
        delta = value - heuristic 

    def _explore(self, depth):
        if self._cutoff_test(depth):
            return None, self._evaluate_board()

        best_action = None

        if self._board.turn() == 1:
            comp = gt
            best_value = -1.1
        else:
            comp = lt
            best_value = 1.1

        for action in self._board.legal_actions():
            self._board.append(action)
            _, child_value = self._explore(depth-1)
            if comp(child_value, best_value):
                best_action = action
                best_value = child_value
            self._board.pop()

        self._update_delta(best_value)

        return best_action, best_value

    def _cutoff_test(self, depth):
        return not depth or not self._board or hash(self._board) in self._tree

    def _step(self):
        self._tree.clear()
        self._delta[:] = 0
        action, _ = self._explore(self._depth)
        self._board.append(action)

    def _run(self):
        while self._board:
            self._step()  
        return self._board.winner
