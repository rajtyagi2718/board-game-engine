from board_games.base_class.board import get_winners, get_hashes, Board

"""
indices
-------
[ 0  1  2  3  4  5  6  7  8]
[ 9 10 11 12 13 14 15 16 17]
...
[72 73 74 75 76 77 78 79 80]
"""

PIECES = ('.', 'x', 'o')
ROWS = tuple(slice(i, i+9) for i in range(0, 81, 9))
HASHES = get_hashes(3, 81)

class GoBoard(Board):

    _pieces = PIECES  # strs
    _rows = ROWS  # slices
    _hashes = HASHES  # ints

    def __init__(self):
        super().__init__(81)
        self._legal_actions = set(range(81))

    def legal_actions(self):
        return tuple(self._legal_actions)

    def legal(self, action):
        return action in self._legal_actions

    def check_winner(self):
        pass

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
        self._legal_actions = set(range(81))
        self._hash_value = 0
        self.winner = None

    def __repr__(self):
        """Return 2-dim grid. 0 -> open, 1 -> agent1, 2 -> agent2.

        Return
        ------
        str

        Examples
        --------
        [0 0 0 0 0 0 0 0 0]    [0 1 0 0 0 0 1 1 2]
        [0 0 0 0 0 0 0 0 0]    [2 2 0 0 0 0 2 2 1]
        [0 0 0 0 0 0 0 0 0]    [1 2 1 0 0 0 1 2 1]
        [0 0 0 0 0 0 0 0 0]    [1 2 1 0 0 0 1 2 1]
        [0 0 0 0 0 0 0 0 0]    [1 2 1 0 0 0 1 2 1]
        [0 0 0 0 0 0 0 0 0]    [1 2 1 0 0 0 1 2 1]
        [0 0 0 0 0 0 0 0 0]    [1 2 1 0 0 0 1 2 1]
        [0 0 0 0 0 0 0 0 0]    [1 2 1 0 0 0 1 2 1]
        [0 0 0 0 0 0 0 0 0]    [1 2 1 0 0 0 1 2 1]

        """
        return '\n'.join(str(self._board[row]) for row in self._rows)


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
