import numpy as np
from collections import namedtuple, defaultdict
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

# Actions
Action = namedtuple('Action', 'action adjs join captures')
Capture = namedtuple('Capture', 
    'turn, indices, components, liberties, captors, boundaries')
Join = namedtuple('Join', 'friends component liberty')

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

    def _territory(self):
        """Return score of captured empty components."""
        score = np.zeros(3)

        # depth first search, explicit stac
        visited = np.array(self._board, dtype='bool')
        for i in range(81):
            if visited[i]:
                continue
            
            stack = [i]
            component = set()
            threats1 = False
            threats2 = False

            while stack and not (threats1 and threats2):
                j = stack.pop()
                if visited[j]:
                    continue
                visited[j] = True
                component.add(j)
               
                for adj in self._adjs[j]:
                    if self._board[adj] == 1:
                        threats1 = True 
                    elif self._board[adj] == 2:
                        threats2 = True 
                    elif not visited[adj]:
                        stack.append(adj) 

            if threats1 and not threats2:
                score[1] += len(component) 
            elif threats2 and not threats1:
                score[2] += len(component) 
            
        return score

    def check_winner(self):
        if ((self[-1] is None and self[-2] is None and len(self) > 1) or 
            len(self._legal_actions) == 1):

            # count stones
            score = np.zeros(3)
            for i in range(81):
                if self._board[i]:
                    score[self._board[i]] += 1
            
            # count territory 
            score += self._territory()

            if score[1] != score[2]:
                self.winner = score.argmax()
            else:     
                self.winner = 0

    def _join(self, friends):
        """Join friends together. Update data structures. Return join tuple."""
        root = friends[0]
        result = Join(friends, self._components[root], self._liberties[root])

        # friends are all roots sorted in decreasing size
        for i,j in zip(friends, friends[1:]): 
            self._groups.connect(i, j)

        # old sets stored in history, make new sets
        self._components[root] = set().union(*(self._components[i]
                                               for i in friends))
        self._liberties[root] = set().union(*(self._liberties[i]
                                              for i in friends))
        return result

    def _capture(self, root):
        """Remove root group. Reset data structures. Return capture tuple."""
        component = tuple(self._components[root])

        # gather Capture data
        turn = self._board[component[0]] 
        indices = component
        components = tuple(self._components[i] for i in indices)
        liberties = tuple(self._liberties[i] for i in indices)
        captors = defaultdict(set)

        self._groups.atomize(component)
        for i in component:
            self._board[i] = 0
            self._components[i] = {i}
            self._legal_actions.add(i)

        # compute component liberties separate loop, depends on empty board
        # component are all zeroed roots
        for i in component:
            self._liberties[i] = set()
            for adj in self._adjs[i]:
                if self._board[adj]:
                    captor = self._groups.root(adj)
                    self._liberties[captor].add(i)
                    # add to Capture data
                    captors[captor].add(i)
                else:
                    self._liberties[i].add(adj)
        
        boundaries = tuple(tuple(v) for v in captors.values())
        captors = tuple(captors.keys())

        return Capture(turn, indices, components, liberties, captors, 
                       boundaries)

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
        self._legal_actions.remove(action)

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

        # join and gather Join data
        if len(friends) > 1:
            join = self._join(friends)
        else:
            join = None

        # captures data
        captures = []

        # check enemy captures: if root has no liberties
        enemies = set(self._groups.root(i) for i in self._adjs[action]
                      if self._board[i] == oth)
        enemies = [i for i in enemies if not self._liberties[i]]
        for enemy in enemies:
            captures.append(self._capture(enemy))

        # check self capture: friends[0] is root of action group
        if not self._liberties[friends[0]]:
            captures.append(self._capture(friends[0]))

        # self._hash_value += self.hash_calc(trn, action)
        action = Action(action, tuple(adjs), join, tuple(captures))
        self._actions.append(action)
        self.check_winner()

    def _undo_capture(self, capture):
        for i, component, liberty in zip(capture.indices, capture.components, 
                                         capture.liberties):
            self._board[i] = capture.turn 
            self._components[i] = component
            self._legal_actions.remove(i)
            self._liberties[i] = liberty

        for captor,boundary in zip(capture.captors, capture.boundaries):
            for i in boundary:
                self._liberties[captor].remove(i)
        
        self._groups.undo_atomize(capture.indices)

    def _undo_join(self, join):
        root = join.friends[0]
        self._components[root] = join.component
        self._liberties[root] = join.liberty

        for i,j in zip(join.friends[-2::-1], join.friends[::-1]):
            self._groups.undo_connect(i, j) 

    def pop(self):
        action = self._actions.pop()
        if action is None:
            self.winner = None 
            return

        assert isinstance(action, Action), 'last action %s' % str(action)

        for capture in action.captures[::-1]:
            self._undo_capture(capture)

        if action.join:
            self._undo_join(action.join)

        for adj in action.adjs[::-1]:
            self._liberties[adj].add(action.action)
        
        self._board[action.action] = 0
        self._legal_actions.add(action.action)

        # self._hash_value -= self.hash_calc(self.turn(), last_action)
        return action.action

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
