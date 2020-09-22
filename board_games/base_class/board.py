from abc import ABC, abstractmethod
import numpy as np

def get_winners(size, slices):
    """Return subset of indices for each possible winning slice.
    
    Args
    ----
    size - int
    slices - list(slice)

    Return
    ------
    tuple(tuple(tuple(slice)))
        
    Example
    -------
    3-in-a-row
    [0 1 2]  (2)  row     (0, 1)
    [3 4 5]  -->  col --> (5, 8)
    [6 7 8]       dia     (4, 6) 

    """
    tpl = tuple(range(size))
    winners = [[] for _ in range(size)]
    for slc in slices:
        ts = tpl[slc] 
        for x in ts:
            winners[x].append(tuple(y for y in ts if y != x))
    return tuple(tuple(slicess) for slicess in winners)

def get_hashes(num_pieces, size):
    """Return hash array. Multiples of num_pieces.

    Args
    ----
    num_pieces - int
    size - int

    Return
    ------
    tuple

    >>> get_hashes(3, 5)
    >>> [1, 3, 9, 81, 727]
    
    """
    hashes = [1]
    for _ in range(1, size):
        hashes.append(hashes[-1] * num_pieces)
    return tuple(hashes)

class Board(ABC):

    _pieces = ()  # tuple of strs for each piece, called by __str__, __hash__
    _rows = ()    # tuple of slices, called by __repr__, __str__
    _hashes = ()  # tuple of ints, called by append, pop

    def __init__(self, size):
        """Construct board as flat array of length size.
      
        Args
        ----
        size - int
        
        """
        self._size = size
        # unsigned int < 256, numpy array very flexible
        self._board = np.zeros(size, dtype='uint8')
        self._actions = []
        self._hash_value = 0
        self.winner = None

    @abstractmethod
    def legal_actions(self):
        """Return all possible legal actions for current agent.

        Return
        ------
        tuple

        """

    @abstractmethod
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

    @abstractmethod
    def check_winner(self):
        """Determine if board is terminal (win, loss, or draw) or not."""

    @abstractmethod
    def append(self, action):
        """Have current agent take action.

        Args
        ----
        action : tuple

        """

    @abstractmethod
    def pop(self):
        """Undo last action. Return the action.

        Return
        ------
        tuple
        
        """

    @abstractmethod
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

    @classmethod
    def hash_calc(cls, piece, position):
        """Return hash value to place piece at position on board."""
        return piece * cls._hashes[position]

    def __hash__(self):
        """Return (nearly) unique value identifying board state.

        Return 
        ------
        int

        """
        return int(self._hash_value)

    def __eq__(self, other):
        """Boards of equal hash are equal.

        Return
        ------
        bool

        """
        return hash(self) == hash(other)

    def __repr__(self):
        """Return 2d matrix.

        Return
        ------
        str
            [ a00 ... a0n ]
                  ...
            [ am0 ... amn ] 

        """
        return '\n'.join(str(self._board[row]) for row in self._rows)

    @abstractmethod
    def __str__(self):
        """Return string for command line interface."""

    def _state(self):
        """Return string of state info for logger."""
        result =   'MOVES: %d' % (len(self))
        result += '\tTURN: %d' % (self.turn()) 
        result += '\tWINNER: %s' % (self.winner)
        result += '\nACTION: %s' % (self[-1])
        result += '\nHASH: %d' % (self._hash_value)
        result += '\nBOARD:\n%s' % (self)
        result += '\nLEGAL ACTIONS: %s' % (str(self.legal_actions()))
        return result

    def _log(self, filepath):
        """Write state info into file."""
        with filepath.open('a') as f:
            f.write(self._state())
