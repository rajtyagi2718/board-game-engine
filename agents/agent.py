from abc import ABC, abstractmethod

class Agent(ABC):
    """Player acts in games. Finds next best move on board. Keeps record."""

    def __init__(self, name):
        self._name = name
        self._record = dict.fromkeys('wins losses draws'.split(), 0)

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
        elif utility > 0:
            self._record['wins'] += 1 
        else:
            self._record['draws'] += 1

    def clear(self):
        """Zero record."""
        self._record = dict.fromkeys(self._record, 0)

    def __repr__(self):
        """Return name - search - (record).

        Return
        ------
        str

        """
        return self._name + ' ' + repr(self._record)
    
    def __str__(self):
        return self._name

    def debug(self, action):
        return 'AGENT {} : ACTION {}'.format(self, action)
