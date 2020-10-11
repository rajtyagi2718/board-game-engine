import numpy as np

class TransTable:

    """Maps game boards by hash to value, depth, lowerbound, upperbound."""

    def __init__(self, size=2**16):
        self._table = np.zeros((size, 4), dtype=np.float32)
        # set default values: random values, zero depth, TODO: bounds?
        self.rng = np.random.default_rng()
        # random floats (-1, 1)
        self._table[:,0] = self.rng.random(size) * self.rng.choice([-1,1],size)

    def __len__(self):
        return len(self._table)

    def __setitem__(self, board, item):
        self._table[hash(board)] = item

    def __getitem__(self, board):
        return self._table[hash(board)]

    def __delitem__(self, board):
        self._table[hash(board)] = 0
        self._table[hash(board)] = self.rng.random(size)

    def clear(self):
        self._table[:] = 0
        self._table[:,0] = self.rng.random(size) * self.rng.choice([-1,1],size)
