import numpy as np
from collections import namedtuple

Connection = namedtuple('Connection', 'parent child')
Atoms = namedtuple('Atoms', 'component weight parent')

# component chars: 0-9, a-z, A-Z, alpha-omega\o
ALPHABET = list(str(i) for i in range(10))
ALPHABET.extend(chr(i) for i in range(ord('a'), ord('a')+26))
ALPHABET.extend(chr(i) for i in range(ord('A'), ord('A')+26))
ALPHABET.extend(chr(i) for i in range(int('03B1', 16),
                                      int('03B1', 16)+14))
ALPHABET.extend(chr(i) for i in range(int('03B1', 16)+15,
                                      int('03B1', 16)+24))

class DisjointSet():

    def __init__(self, size):
        self._weight = np.ones(size, dtype='uint8')
        self._parent = np.arange(size, dtype='uint8')
        self._connections = []

    def __len__(self):
        """Return number of nodes."""
        return len(self._weight)

    def root(self, i):
        """Return oldest ancestor."""
        while i != self._parent[i]:
            i = self._parent[i]
        return i

    def weight(self, i):
        """Return weight of root."""
        return self._weight[self.root(i)]

    def connect(self, i, j):
        """Connect roots j to i. Weight invariant assumed satisfied."""
        self._connections.append(Connection(i, j))
        self._parent[j] = i
        self._weight[i] += self._weight[j]

    def atomize(self, component):
        """Break component into singletons."""
        weight = tuple(self._weight[i] for i in component)
        parent = tuple(self._parent[i] for i in component)
        self._connections.append(Atoms(component, weight, parent))
        for i in component:
            self._weight[i] = 1
            self._parent[i] = i

    def undo_connection(self, i, j):
        """Disconnect roots j to i. Assumed to be last connection."""
        
        connection = self._connections.pop()
        assert isinstance(connection, Connection), 'last operation was not to connect'
        assert (connection.parent, connection.child) == (i, j), 'last connection was between %d and %d, not %d and %d' % (connection.parent, connection.child, i, j)
        self._parent[j] = j
        self._weight[i] -= self._weight[j]

    def undo_atomize(self, component):
        """Reconnect component together. Assumed to be last change."""
        atoms = self._connections.pop() 
        assert isinstance(connection, Atoms), 'last operation was not to atomize'
        assert atoms.component == component, 'last atomized component was %s not %s' % (atoms.component, component)
        for i,w,p in zip(atoms.component, atoms.weight, atoms.parent):
            self._weight[i] = w
            self._parent[i] = p

    def clear(self):
        self._weight[:] = 1
        self._parent[:] = range(len(self))
        self._connections.clear()

    def __eq__(self, other):
        """Return bool if current states equivalent. Disregard connections."""
        return (np.all(self._weight == other._weight) and 
                np.all(self._parent == other._parent))

    def __repr__(self):
        """Return weight and parent arrays on separate lines."""
        return str(self._weight) + '\n' + str(self._parent) 

    def __str__(self):
        """Return list of components.""" 
        result = [ALPHABET[self.root(i)] for i in range(len(self))]
        return ''.join(result) 

    def _connect(self, i, j):
        """Make heaviest root new parent of other. Increment weights."""
        # roots
        pi = self.root(i)
        pj = self.root(j)

        # already connected
        if pi == pj:  
            self._connections.append(None)
            return

        # connect j to i
        if self._weight[pi] >= self._weight[pj]:
            self._connections.append(Connection(pi, pj))
            self._parent[pj] = pi
            self._weight[pi] += self._weight[pj]

        # connect i to j
        else:
            self._connections.append(Connection(pj, pi))
            self._parent[pi] = pj
            self._weight[pj] += self._weight[pi]

    def connected(self, i, j):
        """Return bool if i and j share same root."""
        return self.root(i) == self.root(j)

