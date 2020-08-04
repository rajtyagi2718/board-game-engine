from board_games.base_class.board import Board

PIECES = ('.', 'x', 'o')

ROWS = tuple(slice(i, i+3) for i in range(0, 9, 3))
COLS = tuple(slice(i, 9, 3) for i in range(3))
DIAG = (slice(0, 9, 4), slice(2, 8, 2))

rng = range(9)
WINNERS = [[] for _ in rng]
for slc in ROWS + COLS + DIAG:
    for x in rng[slc]:
        WINNERS[x].append(slc)
WINNERS = tuple(tuple(slices) for slices in WINNERS)

class TicTacToeBoard(Board):

    pieces = PIECES

    rows = ROWS
    cols = COLS
    diag = DIAG
    
    winners = WINNERS

    def __init__(self):
        super().__init__((9,))
        self._legal_actions = set(range(9))

    def legal_actions(self):
        return tuple(self._legal_actions)

    def legal(self, action):
        return action in self._legal_actions

    def append(self, action):
        assert legal(action), ('illegal action by agent%d.' % (self.turn()) +
                               repr(self),)
        self._board[action] = self.turn()

        # Turn is function of number of moves i.e. len of played_keys.
        # Call hash key before incrementing number of moves.
        # TODO: hash class
        # self.hash_value += HashTable.get_hash_key(self.turn(), key)

        self._actions.append(action)
        self._legal_actions.remove(action)

        # TODO: hash class
        # self.winner = HashTable.get_winner(hash(self))

    def pop(self):
        last_action = self._actions.pop()
        self._board[last_action] = 0
        self._legal_actions.add(last_action)
        self.winner = None

        # TODO: hash class
        # self.hash_value -= HashTable.get_hash_key(self.turn(), last_key)

        return last_action

    def clear(self):
        self._board[:] = 0
        self._actions.clear()
        self._legal_actions = set(range(9))
        self._hash_value = 0
        self.winner = None

    def __repr__(self):
        """Return 2-dim grid. 0-open, 1-agent1, 2-agent2.

        Return
        ------
        str

        Examples
        --------
        [0 0 0]    [0 1 0]    [1 1 2]
        [0 0 0]    [2 2 0]    [2 2 1]
        [0 0 0]    [1 2 1]    [1 2 1]

        """
        return '\n'.join(str(self._board[row]) for row in ROWS)


    def __str__(self):
        """Return string for command line interface.

        Examples
        --------
        ///////////    ///////////     ///////////
        // . . . //    // . x . //     // x o . //
        // . . . //    // o o . //     // o o x //
        // . . . //    // . x x //     // o x x //
        ///////////    ///////////     ///////////
        """
        result = '/'*11 + '\n'
        for row in ROWS:
            line = '// '
            line += ' '.join(self.pieces[action] for action in self._board[row])
            line += ' //'
            result += line + '\n'
        result += '/'*11
        return result

    # TODO: copy needed?
    # def copy(self):
    #     """Return deep copy of current instance."""
    #     return Board(np.array(self.values), list(self.played_keys),
    #                  set(self.open_keys), self.winner, self.hash_value)
