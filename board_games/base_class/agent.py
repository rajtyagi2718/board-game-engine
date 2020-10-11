from abc import ABC, abstractmethod
import random 
import numpy as np
from pathlib import Path

from logs.log import get_logger

LOGGER = get_logger(__name__)

class Agent(ABC):
    """Player acts in games. Finds next best move on board. Keeps record."""

    def __init__(self, name):
        self._name = name
        self._record = dict.fromkeys('wins losses draws'.split(), 0)

    def __repr__(self):
        """Return name - search - (record).

        Return
        ------
        str

        """
        return self._name + ' ' + repr(self._record)

    @abstractmethod
    def act(self, game):
        """Return action to take in game.

        Args
        ----
        game - Game

        Return
        ------
        action : tuple

        """

    def update_record(self, utility):
        """Increment win loss draw record with result of last game."""
        if utility < 0:
            self._record['losses'] += 1 
            result = 'LOSSED'
        elif utility > 0:
            self._record['wins'] += 1 
            result = 'WON'
        else:
            self._record['draws'] += 1
            result = 'DREW'
        LOGGER.info('{!r}\t{} GAME'.format(self, result))

    def clear(self):
        """Zero record."""
        self._record = dict.fromkeys(self._record, 0)
        LOGGER.info('{!r}\tRECORD CLEARED'.format(self))

class RandomAgent(Agent):

    def __init__(self, name='random'):
        super().__init__(name) 

    def act(self, game):
        action = random.choice(game.legal_actions())
        LOGGER.info('{!r}\tACTION: {!s}'.format(self, action))
        return action

    def clear(self):
        self._record = dict.fromkeys(self._record, 0)
        LOGGER.info('{!r}\tRECORD CLEARED'.format(self))

class TestAgent(Agent):

    def __init__(self, name='test', actions=()):
        super().__init__(name) 
        self._actions = list(reversed(actions))

    def act(self, game):
        action = self._actions.pop()
        LOGGER.info('{!r}\tACTION: {!s}'.format(self, action))
        return action

    def clear(self):
        self._record = dict.fromkeys(self._record, 0)
        LOGGER.info('{!r}\tRECORD CLEARED'.format(self))

WEIGHTS_PATH = Path('data/weights/')

class HeuristicAgent(Agent):

    def __init__(self, name):
        super().__init__(name)
        self._weights = {}

        for path in WEIGHTS_PATH.iterdir():
            # 'data/weights/tictactoe.txt' -> 'tictactoe'
            game_name = path.name[:-4]
            weights = np.genfromtxt(path, delimiter='\n', dtype=np.float64)
            self._weights[game_name] = weights

    def act(self, game):
        """Evaluate legal actions by linear approx of heuristic and weights."""
        board = game._board
        actions = game.legal_actions()
        weights = self._weights[game._name]
        values = np.zeros(len(actions))
        argext = np.argmax if board.turn() == 1 else np.argmin

        for i, action in enumerate(actions):
            board.append(action)
            values[i] = weights @ board.heuristic()
            board.pop()

        LOGGER.info('{}\tACTION-VALUES: {!s}'.format(self._name, 
            '\n'.join(str(av) for av in zip(actions, values))))
        action = actions[argext(values)]
        LOGGER.info('{}\tACTION: {!s}'.format(self._name, action))
        return action
