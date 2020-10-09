from abc import ABC, abstractmethod
import random 
from logs.log import get_logger

LOGGER = get_logger(__name__)

class Agent(ABC):

    def __init__(self, name, search):
        self._name = name
        self._search = search
        self._record = dict.fromkeys('wins losses draws'.split(), 0)

    def __repr__(self):
        """Return name - search - (record).

        Return
        ------
        str

        """
        return self._name + ' ' + repr(self._search) + ' ' + repr(self._record)

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
        """Reset to initial state."""
        self._search.clear()
        self._record = dict.fromkeys(self._record, 0)
        LOGGER.info('{!r}\tRECORD CLEARED'.format(self))

class RandomAgent(Agent):

    def __init__(self, name='random'):
        super().__init__(name, None) 

    def act(self, game):
        action = random.choice(game.legal_actions())
        LOGGER.info('{!r}\tACTION: {!s}'.format(self, action))
        return action

    def clear(self):
        self._record = dict.fromkeys(self._record, 0)
        LOGGER.info('{!r}\tRECORD CLEARED'.format(self))

class TestAgent(Agent):

    def __init__(self, name='test', actions=()):
        super().__init__(name, None) 
        self._actions = list(reversed(actions))

    def act(self, game):
        action = self._actions.pop()
        LOGGER.info('{!r}\tACTION: {!s}'.format(self, action))
        return action

    def clear(self):
        self._record = dict.fromkeys(self._record, 0)
        LOGGER.info('{!r}\tRECORD CLEARED'.format(self))
