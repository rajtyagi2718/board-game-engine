from abc import ABC, abstractmethod
from pathlib import Path
import random 
import numpy as np

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
