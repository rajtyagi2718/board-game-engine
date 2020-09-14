import numpy as np
from collections import namedtuple

Connection = namedtuple('Connection', 'master slave')

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

    def _find(self, i):
        """Return root i.e. latest ancestor."""
        while i != self._parent[i]:
            i = self._parent[i]
        return i

    def connected(self, i, j):
        """Return bool if i and j share same root."""
        return self._find(i) == self._find(j)

    def weight(self, i):
        """Return weight of root."""
        return self._weight[self._find(i)]

    def component(self, i):
        """Return items in connected component i.e. share root."""
        p = self._find(i)
        return (j for j in range(len(self)) if self._find(j) == p)

    def connect(self, i, j):
        """Make heaviest root new parent of other. Increment weights."""
        # roots
        pi = self._find(i)
        pj = self._find(j)

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

    def undo(self):
        """Undo last call to connect. Use last connection to restore structs"""
        connection = self._connections.pop() 
        if connection:
            self._parent[connection.slave] = connection.slave
            self._weight[connection.master] -= self._weight[connection.slave]

    def __eq__(self, other):
        """Return bool if current states equivalent. Disregard connections."""
        return (np.all(self._weight == other._weight) and 
                np.all(self._parent == other._parent))

    def __repr__(self):
        """Return weight and parent arrays on separate lines."""
        return str(self._weight) + '\n' + str(self._parent) 

    def __str__(self):
        """Return list of components.""" 
        result = [ALPHABET[self._find(i)] for i in range(len(self))]
        return ''.join(result) 

LibertiesConnection = namedtuple('LibertiesConnection', 
                                 'master slave liberties i j')
                                 # 'master slave liberties')

class LibertiesDisjointSet(DisjointSet):
    """Extension of Disjoint Set with set of liberties per component."""

    def __init__(self, size, liberties):
        super().__init__(size)
        self._liberties = np.array([set(libs) for libs in liberties], 
                                   dtype=object)

    def liberties(self, i):
        """Return tuple of liberties of component i, stored in root node."""
        return tuple(self._liberties[self._find(i)])

    def add(self, i, lib):
        """Add liberty to component i."""
        self._liberties[self._find(i)].add(lib)

    def remove(self, i, lib):
        """Remove liberty to component i."""
        try:
            self._liberties[self._find(i)].remove(lib)
        except KeyError:
            print("Redundant call to remove")

    def captured(self, i):
        """Return bool if component i has no liberties."""
        return not self._liberties[self._find(i)] 

    def atari(self, i):
        """Return bool if component i has exactly one liberty."""
        return len(self._liberties[self._find(i)]) == 1

    def connect(self, i, j): 
        """Make heaviest root new parent of other. Add weights, liberties."""
        # roots
        pi = self._find(i)
        pj = self._find(j)

        # already connected
        if pi == pj:
            # self._connections.append(None)
            self._connections.append(LibertiesConnection(None, None, None, i, j))
            return

        # connect j to i
        if self._weight[pi] >= self._weight[pj]:
            self._connections.append(
                # LibertiesConnection(pi, pj, self._liberties[pi]))
                LibertiesConnection(pi, pj, self._liberties[pi],
                                    i, j))
            self._parent[pj] = pi
            self._weight[pi] += self._weight[pj]
            # make new set for union, old set stored in connection
            self._liberties[pi] = self._liberties[pi] | self._liberties[pj]

        # connect i to j
        else:
            self._connections.append(
                # LibertiesConnection(pj, pi, self._liberties[pj]))
                LibertiesConnection(pj, pi, self._liberties[pj],
                                    i, j))
            self._parent[pi] = pj
            self._weight[pj] += self._weight[pi]
            # make new set for union, old set stored in connection
            self._liberties[pj] = self._liberties[pj] | self._liberties[pi]

    def undo(self, i, j):
        """Undo last call to connect. Use last connection to restore structs"""
        connection = self._connections.pop() 
        if connection.i == i and connection.j == j:
            if connection.master:
                self._parent[connection.slave] = connection.slave
                self._weight[connection.master] -= self._weight[connection.slave]
                self._liberties[connection.master] = connection.liberties

        else:
            raise IndexError("cannot undo. last connection was %r"
                             % connection)
        # if connection:
        #     self._parent[connection.slave] = connection.slave
        #     self._weight[connection.master] -= self._weight[connection.slave]
        #     self._liberties[connection.master] = connection.liberties

    def __eq__(self, other):
        """Return bool if current states equivalent. Disregard connections."""
        return (np.all(self._weight == other._weight) and 
                np.all(self._parent == other._parent) and
                np.all(self._liberties == other._liberties))

    def __repr__(self):
        """Return weight, parent, and liberties arrays on separate lines."""
        return (str(self._weight) + '\n' + str(self._parent) + '\n' +
                str([sorted(libs) for libs in self._liberties]))

AdjConnection = namedtuple('AdjConnection', 
                           'master slave adjs liberties i j')

class AdjDisjointSet(DisjointSet):
    """Extension of Disjoint Set with set of liberties per component."""

    def __init__(self, size, adjs, liberties):
        super().__init__(size)
        self._adjs = np.array([set(adj) for adj in adjs], dtype=object)
        self._liberties = np.array([set(libs) for libs in liberties], 
                                   dtype=object)

    def adjs(self, i):
        """Return tuple of adjs of component i, stored in root node."""
        return tuple(self._adjs[self._find(i)])

    def liberties(self, i):
        """Return tuple of liberties of component i, stored in root node."""
        return tuple(self._liberties[self._find(i)])

    def add(self, i, lib):
        """Add liberty to component i."""
        self._liberties[self._find(i)].add(lib)

    def remove(self, i, lib):
        """Remove liberty to component i."""
        try:
            self._liberties[self._find(i)].remove(lib)
        except KeyError:
            print("Redundant call to remove")

    def captured(self, i):
        """Return bool if component i has no liberties."""
        return not self._liberties[self._find(i)] 

    def atari(self, i):
        """Return bool if component i has exactly one liberty."""
        return len(self._liberties[self._find(i)]) == 1

    def connect(self, i, j): 
        """Make heaviest root new parent of other. Add weights, liberties."""
        # roots
        pi = self._find(i)
        pj = self._find(j)

        # already connected
        if pi == pj:
            self._connections.append(AdjConnection(None, None, None, None, i, j))
            return

        # connect j to i
        if self._weight[pi] >= self._weight[pj]:
            self._connections.append(
                AdjConnection(pi, pj, self._liberties[pi],
                              self._adjs[pi], i, j))
            self._parent[pj] = pi
            self._weight[pi] += self._weight[pj]
            # make new set for symmetric difference
            self._adjs[pi] = self._adjs[pi] ^ self._adjs[pj] 
            # make new set for union
            self._liberties[pi] = self._liberties[pi] | self._liberties[pj]

        # connect i to j
        else:
            self._connections.append(
                AdjConnection(pj, pi, self._liberties[pj], 
                              self._adjs[pj], i, j))
            self._parent[pi] = pj
            self._weight[pj] += self._weight[pi]
            # make new set for symmetric difference
            self._adjs[pj] = self._adjs[pi] ^ self._adjs[pj] 
            # make new set for union
            self._liberties[pj] = self._liberties[pi] | self._liberties[pj]

    def undo(self, i, j):
        """Undo last call to connect. Use last connection to restore structs"""
        connection = self._connections.pop() 
        if connection.i == i and connection.j == j:
            if connection.master:
                self._parent[connection.slave] = connection.slave
                self._weight[connection.master] -= self._weight[connection.slave]
                self._adjs[connection.master] = connection.adjs
                self._liberties[connection.master] = connection.liberties

        else:
            raise IndexError("cannot undo. last connection was %r"
                             % connection)

    def __eq__(self, other):
        """Return bool if current states equivalent. Disregard connections."""
        return (np.all(self._weight == other._weight) and 
                np.all(self._parent == other._parent) and
                np.all(self._liberties == other._liberties))

    def __repr__(self):
        """Return weight, parent, and liberties arrays on separate lines."""
        return (str(self._weight) + '\n' + str(self._parent) + '\n' +
                str([sorted(libs) for libs in self._liberties]))
