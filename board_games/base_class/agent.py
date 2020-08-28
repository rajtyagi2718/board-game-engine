from abc import ABC, abstractmethod
import random 

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
        elif utility > 0:
            self._record['wins'] += 1 
        else:
            self._record['draws'] += 1

    def clear(self):
        """Reset to initial state."""
        self._search.clear()
        self._record = dict.fromkeys(self._record, 0)

class RandomAgent(Agent):

    def __init__(self, name='random'):
        super().__init__(name, None) 

    def act(self, game):
        actions = game.legal_actions()
        print('Actions:', *actions, sep='\n')
        return random.choice(actions)
        return random.choice(game.legal_actions()) 

    def clear(self):
        self._record = dict.fromkeys(self._record, 0)
