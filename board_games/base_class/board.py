import numpy as np

class Board:

    pieces = ()  # str for each piece, called by __str__

    def __init__(self, size):
        """Construct board as flat array of length size.
        
        Args
        ----
        size - int
        
        """
        # unsigned int < 256, numpy very flexible
        self._board = np.zeros(size, dtype='uint8')
        self._actions = []
        self._hash_value = 0
        self.winner = None

    def legal_actions(self):
        """Return all possible legal actions for current agent.

        Return
        ------
        tuple

        """

    def legal(self, action):
        """Assess if current agent can take action.

        Args
        ----
        action : tuple

        Return
        ------
        bool

        """

    def __len__(self):
        """Return number of moves played.

        Return
        ------
        int

        """
        return len(self._actions)

    def __getitem__(self, index):
        """Return action at index. Return None if IndexError."""
        try:
            return self._actions[-1]
        except IndexError:
            return None

    def append(self, action):
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

    def clear(self):
        """Reset to starting board."""

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

    def __bool__(self):
        """Return True unless board is terminal.

        Return
        ------
        bool

        """
        return self.winner is None

    def utility(self):
        """Return state value from agent1 pov: +1 if win, -1 lose, 0 else.
        
        Return
        ------
        int 0, 1, or 2

        """
        if self.winner == 1:
            return 1
        if self.winner == 2:
            return -1
        return 0

    def __hash__(self):
        """Return (nearly) unique value identifying board state.

        Return 
        ------
        int

        """
        return self._hash_value

    def __eq__(self, other):
        """Boards of equal hash are equal.

        Return
        ------
        bool

        """
        return hash(self) == hash(other)

    def __str__(self):
        """Return string for command line interface."""

    def __repr__(self):
        """Return 2d matrix.

        Return
        ------
        str
            [ a00 ... a0n ]
                  ...
            [ am0 ... amn ] 

        """
