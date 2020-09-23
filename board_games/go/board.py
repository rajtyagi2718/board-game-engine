import numpy as np
from collections import namedtuple
from board_games.base_class.board import get_winners, get_hashes, Board
from board_games.go.utils import DisjointSet

"""
indices
-------
[ 0  1  2  3  4  5  6  7  8]
[ 9 10 11 12 13 14 15 16 17]
...
[63 64 65 66 67 68 69 70 71]
[72 73 74 75 76 77 78 79 80]
"""

PIECES = ('.', 'x', 'o')
ROWS = tuple(slice(i, i+9) for i in range(0, 81, 9))
HASHES = get_hashes(3, 81)

ADJS = [[i-9, i-1, i+1, i+9] for i in range(81)]
for i in range(1, 8):
    ADJS[i].pop(0)
for i in range(9, 72, 9):
    ADJS[i].pop(1)
for i in range(17, 80, 9):
    ADJS[i].pop(2)
for i in range(73, 80):
    ADJS[i].pop(3)
ADJS[0] = [1, 9]
ADJS[8] = [7, 17]
ADJS[72] = [63, 73]
ADJS[80] = [71, 79]
ADJS = tuple(tuple(x) for x in ADJS)


# adj: array map from index to adjacent indices
# board: array map from index to color
# groups: disjoint set map from index to root
# components: list map from root index to component 
# liberties: list indices 

# place stone in index
#     board
# connect stone to friendly groups
#     adj, group, group.connect, group.union_liberties
# capture enemy groups 
#     adj, group, group.capture
# self capture
#     group.capture

class GoBoard(Board):

    _pieces = PIECES  # strs
    _rows = ROWS  # slices
    _hashes = HASHES  # ints
    _adjs = ADJS # ints

    def __init__(self):
        super().__init__(81)
        self._legal_actions = set(range(81)) | {None}
        self._groups = DisjointSet(81)
        self._components = [{i} for i in range(81)]
        self._liberties = [set(adj) for adj in self._adjs]

    def legal_actions(self):
        return tuple(self._legal_actions)

    def legal(self, action):
        return action in self._legal_actions

    def check_winner(self):
        if ((self[-1] is None and self[-2] is None and len(self) > 1) or 
            len(self._legal_actions) == 1):
            # TODO calculate winner
            self.winner = 3

    def _join(self, friends):
        """Join friends together. Update groups, components, liberties."""
        # friends are all roots sorted in decreasing size
        for i,j in zip(friends, friends[1:]): 
            self._groups.connect(i, j)
        root = friends[0]
        # old sets stored in history, make new sets
        self._components[root] = set().union(*(self._components[i]
                                               for i in friends))
        self._liberties[root] = set().union(*(self._liberties[i]
                                              for i in friends))

    def _capture(self, root):
        """Remove root group. Reset groups, components, liberties.""" 
        component = tuple(self._components[root])
        self._groups.atomize(component)
        for i in component:
            self._board[i] = 0
            self._components[i] = {i}
            self._legal_actions.add(i)

        # compute component liberties separate loop, depends on empty board
        # component are all zeroed and roots
        for i in component:
            self._liberties[i] = set()
            for adj in self._adjs[i]:
                if self._board[adj]:
                    captor = self._groups.root(adj)
                    self._liberties[captor].add(i)
                else:
                    self._liberties[i].add(adj)

    def append(self, action):
        # check action is legal
        assert self.legal(action), (
            'illegal action by agent%d. %s already played.' % (self.turn(), action))
        if action is None:
            self._actions.append(action)
            self.check_winner()
            return

        trn = self.turn()
        oth = self.other()

        # place stone
        self._board[action] = trn

        # remove action liberty from adjs
        adjs = set(self._groups.root(i) for i in self._adjs[action])
        for adj in adjs:
            self._liberties[adj].remove(action)

        # connect stone with friends
        friends = set(self._groups.root(i) for i in self._adjs[action] 
                      if self._board[i] == trn)
        friends = sorted(friends, key=lambda i: self._groups._weight[i],
                         reverse=True)
        friends.append(action)
        if len(friends) > 1:
            self._join(friends)

        # check enemy captures: if root has no liberties
        enemies = set(self._groups.root(i) for i in self._adjs[action]
                      if self._board[i] == oth)
        enemies = [i for i in enemies if not self._liberties[i]]
        for enemy in enemies:
            self._capture(enemy)

        # check self capture: friends[0] is root of action group
        if not self._liberties[friends[0]]:
            self._capture(friends[0])

        # turn depends on number of moves
        # increment hash value before appending to actions
        # self._hash_value += self.hash_calc(trn, action)
        self._actions.append(action)
        self._legal_actions.remove(action)
        self.check_winner()

    def pop(self):
        assert False, 'pop not defined yet'
        last_action = self._actions.pop()
        if last_action is None:
            self.winner = None 
            return

        trn = self.turn()
        oth = self.other()
        self._board[last_action] = 0

        for adj in self._adjs[last_action][::-1]:
            if self._board[adj] == trn:
                self._groups.undo(adj, last_action)
                if self._groups.captured(adj):
                    # print("*"*10 + "Atari!" + "*"*10) 
                    for comp in self._groups.component(adj):
                        self._board[comp] = oth
                        self._legal_actions.remove(comp)
            self._groups.add(adj, last_action)

        # turn depends on number of moves
        # decrement hash value after popping from actions
        self._hash_value -= self.hash_calc(self.turn(), last_action)
        self._legal_actions.add(last_action)

        comps = str(self._groups)
        # print('\n'.join([comps[i:i+9] for i in range(0, 81, 9)]))

        return last_action

    def clear(self):
        self._board[:] = 0
        self._actions.clear()
        self._hash_value = 0
        self.winner = None

        self._legal_actions = set(range(81))
        self._groups.clear()
        self._components = [{i} for i in range(81)]
        self._liberties = [set(adj) for adj in self._adjs]

    def __str__(self):
        """Return string for command line interface.

        Examples
        --------
        ///////////////////////    ///////////////////////
        // ..... . . . ..... //    // . x . . . . x x o //
        // . . . . . . ..... //    // o o . . . . o o x //
        // ..... . . . ..... //    // x o x . . . x o x //
        // . . . ..... . . . //    // x o x . . . x o x //
        // . . . ..... . . . //    // x o x . . . x o x //
        // . . . ..... . . . //    // x o x . . . x o x //
        // ..... . . . ..... //    // x o x . . . x o x //
        // ..... . . . ..... //    // x o x . . . x o x //
        // ..... . . . ..... //    // x o x . . . x o x //
        ///////////////////////    ///////////////////////

        """
        result = '/'*23 + '\n'
        for row in self._rows:
            line = '// '
            line += ' '.join(self._pieces[actn] for actn in self._board[row])
            line += ' //'
            result += line + '\n'
        result += '/'*23
        return result

    def _state(self):
        """Return string of state info for logger."""
        result = super()._state() 
        groups = str(self._groups)
        groups = '\n'.join((' '.join(groups[i:i+9]) for i in range(0, 81, 9)))
        result += '\nCOMPONENTS:\n%s' % (groups)
        return result
