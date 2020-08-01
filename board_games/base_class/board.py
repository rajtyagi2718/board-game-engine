import numpy as np

class Board:

    def __init__(self, shape):
        self._board = np.zeros(shape, dtype=int)
        self._actions = []
        self._winner = None
        self._hash_value = 0

    def __len__(self):
        """Return number of moves played.

        Return
        ------
        int

        """
        return len(self._actions)

    def __hash__(self):
        """Return (nearly) unique value identifying board state.

        Return 
        ------
        int

        """
        return self._hash_value

    def legal(self, action):
        """Assess if current agent can take action.

        Args
        ----
        action : tuple

        Return
        ------
        bool

        """

    def push(self, action):
        """Have current agent take action.

        Args
        ----
        action : tuple

        """

    def pop(self):
        """Undo last action. Return the action.

        Return
        ------
        tuple
        
        """

    def turn(self):
        """Return current agent's turn. Game awaits their action.

        Return
        ------
        int 1 or 2

        """
        return 1 + len(self) % 2

    def other(self):
        """Return opposing agent. Currently not their turn. 

        Return
        ------
        int 1 or 2
        """
        return 2 - len(self) % 2

    def clear(self):
        """Reset to starting board."""

    def __str__(self):
        """Return string for command line interface."""

    def __repr__(self):
        """Return 2d matrix.

        Return
        ----
        str
            [ a00 ... a0n ]
                  ...
            [ am0 ... amn ] 

        """
