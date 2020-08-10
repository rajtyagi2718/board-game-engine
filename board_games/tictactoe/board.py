from board_games.base_class.board import get_winners, get_hashes, Board

"""
indices
-------
[0 1 2]
[3 4 5]
[6 7 8]

"""

PIECES = ('.', 'x', 'o')

SLICES = []
for i in range(0, 9, 3):  # rows
    SLICES.append(slice(i, i+3))
ROWS = tuple(SLICES)
for j in range(3):  # columns
    SLICES.append(slice(j, 9, 3))
SLICES.extend((slice(0, 9, 4), slice(2, 8, 2)))  # diagonals
WINNERS = get_winners(9, SLICES)
del SLICES
HASHES = get_hashes(3, 9)

class TicTacToeBoard(Board):

    _pieces = PIECES  # strs
    _rows = ROWS  # slices
    _winners = WINNERS  # tuples
    _hashes = HASHES  # ints

    def __init__(self):
        super().__init__(9)
        self._legal_actions = set(range(9))

    def legal_actions(self):
        return tuple(self._legal_actions)

    def legal(self, action):
        return action in self._legal_actions

    def check_winner(self):
        # agent takes at least 3 turns to win 
        if len(self) < 5:
            return

        # last agent to take turn can win
        oth = self.other()
        for slc in self._winners[self[-1]]:
            if self._board[slc[0]] == oth and self._board[slc[1]] == oth:
                self.winner = oth
                break

        # full board without winner is draw
        if len(self) == 9:
            self.winner = 0

    def append(self, action):
        assert self.legal(action), (
            'illegal action by agent%d' % (self.turn()) + repr(self),)
        trn = self.turn()
        self._board[action] = trn
        # turn depends on number of moves
        # increment hash value before appending to actions
        self._hash_value += self.hash_calc(trn, action)
        self._actions.append(action)
        self._legal_actions.remove(action)
        self.check_winner()

    def pop(self):
        last_action = self._actions.pop()
        self._board[last_action] = 0
        self._legal_actions.add(last_action)
        self.winner = None
        # turn depends on number of moves
        # decrement hash value after popping from actions
        self._hash_value -= self.hash_calc(self.turn(), last_action)
        return last_action

    def clear(self):
        self._board[:] = 0
        self._actions.clear()
        self._legal_actions = set(range(9))
        self._hash_value = 0
        self.winner = None

    def __repr__(self):
        """Return 2-dim grid. 0 -> open, 1 -> agent1, 2 -> agent2.

        Return
        ------
        str

        Examples
        --------
        [0 0 0]    [0 1 0]    [1 1 2]
        [0 0 0]    [2 2 0]    [2 2 1]
        [0 0 0]    [1 2 1]    [1 2 1]

        """
        return '\n'.join(str(self._board[row]) for row in self._rows)


    def __str__(self):
        """Return string for command line interface.

        Examples
        --------
        ///////////    ///////////     ///////////
        // . . . //    // . x . //     // x x o //
        // . . . //    // o o . //     // o o x //
        // . . . //    // x o x //     // x o x //
        ///////////    ///////////     ///////////
        """
        result = '/'*11 + '\n'
        for row in self._rows:
            line = '// '
            line += ' '.join(self._pieces[actn] for actn in self._board[row])
            line += ' //'
            result += line + '\n'
        result += '/'*11
        return result