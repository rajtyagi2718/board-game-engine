from board_games.base_class.board import get_winners, get_hashes, Board

"""
indices
-------
[35 36 37 38 39 40 41]
[28 29 30 31 32 33 34]
[21 22 23 24 25 26 27]
[14 15 16 17 18 19 20]
[ 7  8  9 10 11 12 13]
[ 0  1  2  3  4  5  6]

"""

PIECES = ('.', 'x', 'o')
ROWS = tuple(slice(i, i+7) for i in range(35, -1, -7))

_SLICES = []
for i in range(0, 42, 7):  # rows
    for j in range(4):
        _SLICES.append(slice(i+j, i+j+4))
for i in range(0, 21, 7):  # columns
    for j in range(7):
        _SLICES.append(slice(i+j, i+j+28, 7))
for i in range(0, 21, 7):  # diagonals
    for j in range(4):
        _SLICES.append(slice(i+j, i+j+32, 8))
for i in range(0, 21, 7):
    for j in range(3, 7):
        _SLICES.append(slice(i+j, i+j+24, 6))
    
WINNERS = get_winners(42, _SLICES)
HASHES = get_hashes(3, 42)

del _SLICES

class ConnectFourBoard(Board):

    _pieces = PIECES  # strs
    _rows = ROWS  # slices
    _winners = WINNERS  # tuples
    _hashes = HASHES  # ints

    def __init__(self):
        super().__init__(42)
        self._legal_actions = [list(range(i, -1, -7)) for i in range(35, 42)]
        self._indices = []

    def legal_actions(self):
        return tuple(i for i in range(7) if self._legal_actions[i])

    def legal(self, action):
        return bool(self._legal_actions[action])

    def check_winner(self):
        # agent takes at least 4 turns to win 
        if len(self) < 7:
            return

        # last agent to take turn can win
        oth = self.other()
        for slc in self._winners[self._indices[-1]]:
            if all(self._board[i] == oth for i in slc):
                self.winner = oth
                break

        # full board without winner is draw
        if len(self) == 42:
            self.winner = 0

    def append(self, action):
        assert self.legal(action), (
            'illegal action by agent%d' % (self.turn()) + repr(self),)
        trn = self.turn()
        ind = self._legal_actions[action].pop()
        self._board[ind] = trn
        # turn depends on number of moves
        # increment hash value before appending to actions
        self._hash_value ^= self.hash_calc(trn, ind)
        self._actions.append(action)
        self._indices.append(ind)
        self.check_winner()

    def pop(self):
        action = self._actions.pop()
        index = self._indices.pop()
        self._board[index] = 0
        self._legal_actions[action].append(index)
        self.winner = None
        # turn depends on number of moves
        # decrement hash value after popping from actions
        self._hash_value ^= self.hash_calc(self.turn(), index)
        return action

    def clear(self):
        self._board[:] = 0
        self._actions.clear()
        self._indices.clear()
        self._legal_actions = [list(range(i, -1, -7)) for i in range(35, 42)]
        self._hash_value = self._hashes[0,0]
        self.winner = None

    def __str__(self):
        """Return string for command line interface.

        Examples
        --------
        ///////////////////    ///////////////////
        // . . . . . . . //    // . . . . . . . //
        // . . . . . . . //    // . . . . . . . //
        // . . . . . . . //    // . x o . . . . //
        // . . . . . . . //    // . o x o . . . //
        // . . . . . . . //    // . o x x x . . //
        // . . . . . . . //    // . o x x o . . //
        ///////////////////    ///////////////////

        """
        result = '/'*19 + '\n'
        for row in self._rows:
            line = '// '
            line += ' '.join(self._pieces[actn] for actn in self._board[row])
            line += ' //'
            result += line + '\n'
        result += '/'*19
        return result
