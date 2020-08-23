import np.array

class WeightedQuickUnionDisjointSet():

    def __init__(self, size):
        self._size = size
        self._weight = np.zeros(size, dtype='uint8')
        self._parent = np.zeros(size, dtype='uint8')

    def _find(self, i):
        """Return root i.e. latest ancestor."""
        while i != self._parent[i]:
            i = self._parent[i]
        return i

    def weight(self, i):
        """Return weight of root."""
        return self._weight[self._find(i)]

    def component(self, i):
        """Return items in connected component i.e. share root."""
        p = self._find(i)
        return (j for j in range(self._size) if self._find(j) == p)

    def connect(self, i, j):
        """Make heaviest root new parent of other. Increment weights."""
        pi = self._find(i)
        pj = self._find(j)
        if pi == pj:  # already connected
            return
        if self._weight[pi] > self._parent[pj]:
            self._parent[j] = pi
            self._weight[pi] += self._weight[pj]
        else:
            self._parent[i] = pj
            self._weight[pj] += self._weight[pi]

    def _find_second(self, i):
        p = self._parent[i]
        while p != self._parent[p]:
            i = p
            p = self._parent[p] 
        return p, i

    def undo(self, i, j):
        """Disconnect i and j, where last call to connect was between them."""
        pass
