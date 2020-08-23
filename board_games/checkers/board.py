from board_games.base_class.board import get_hashes, Board
from collections import namedtuple

"""
indices
-------
[    0     1     2     3]
[ 4     5     6     7   ]
[    8     9    10    11]
[12    13    14    15   ]
[   16    17    18    19]
[20    21    22    23   ]
[   24    25    26    27]
[28    29    30    31   ]

"""

PIECES = ('.', 'x', 'o', 'X', 'O')
ROWS = tuple(slice(i, i+4) for i in range(0, 32, 4))
HASHES = get_hashes(5, 32)

# up/left, up/right, down/left, down/right
EDGES = [[None]*4 for i in range(32)]
# up/left
for i in range(5, 37, 8):
    for j in range(i, i+3):
        EDGES[j][0] = j-5
for i in range(8, 32, 8):
    for j in range(i, i+4):
        EDGES[j][0] = j-4
# up/right
for i in range(4, 36, 8):
    for j in range(i, i+4):
        EDGES[j][1] = j-4
for i in range(8, 32, 8):
    for j in range(i, i+3):
        EDGES[j][1] = j-3
# down/left
for i in range(0, 32, 8):
    for j in range(i, i+4):
        EDGES[j][2] = j+4
for i in range(5, 29, 8):
    for j in range(i, i+3):
        EDGES[j][2] = j+3
# down/right
for i in range(0, 32, 8):
    for j in range(i, i+3):
        EDGES[j][3] = j+5
for i in range(4, 28, 8):
    for j in range(i, i+4):
        EDGES[j][3] = j+4

Slide  = namedtuple('Slide', 'up start stop promotion')
Jump   = namedtuple( 'Jump', 'up start stop promotion capture piece')
Path   = namedtuple( 'Path', 'start stop promotion captures pieces')

SLIDES_UP   = [[] for _ in range(32)]
SLIDES_DOWN = [[] for _ in range(32)]
SLIDES      = [[] for _ in range(32)]
JUMPS_UP    = [[] for _ in range(32)]
JUMPS_DOWN  = [[] for _ in range(32)]
JUMPS       = [[] for _ in range(32)]
ADJ = [[None]*32 for _ in range(32)]

for start, adj in enumerate(EDGES):
    for stop in adj[:2]:
        if stop is None:
            continue
        promotion = False if stop > 3 else True
        slide = Slide(True, start, stop, promotion)
        SLIDES_UP[start].append(slide)
        SLIDES[start].append(slide)
        ADJ[start][stop] = slide
    for stop in adj[2:]:
        if stop is None:
            continue
        promotion = False if stop < 28 else True
        slide = Slide(False, start, stop, promotion)
        SLIDES_DOWN[start].append(slide)
        SLIDES[start].append(slide)
        ADJ[start][stop] = slide

for start, adj in enumerate(EDGES):
    for direc, capture in enumerate(adj):
        if capture is None:
            continue
        stop = EDGES[capture][direc] 
        if stop is None:
            continue
        if direc < 2:
            promotion = False if stop > 3 else True
            jump = Jump(True, start, stop, promotion, capture, None)
            JUMPS_UP[start].append(jump)
            JUMPS[start].append(jump)
            ADJ[start][stop] = jump
        else:
            promotion = False if stop < 28 else True
            jump = Jump(False, start, stop, promotion, capture, None)
            JUMPS_DOWN[start].append(jump)
            JUMPS[start].append(jump)
            ADJ[start][stop] = jump

SLIDES_UP   = tuple(tuple(slides) for slides in SLIDES_UP)
SLIDES_DOWN = tuple(tuple(slides) for slides in SLIDES_DOWN)
SLIDES      = tuple(tuple(slides) for slides in SLIDES)
JUMPS_UP    = tuple(tuple(jumps) for jumps in JUMPS_UP)
JUMPS_Down  = tuple(tuple(jumps) for jumps in JUMPS_DOWN)
JUMPS       = tuple(tuple(jumps) for jumps in JUMPS)
ADJ = tuple(tuple(row) for row in ADJ)

class CheckersBoard(Board):

    _pieces = PIECES  # strs
    _rows = ROWS  # slices
    _hashes = HASHES  # ints

    # actions: Slide or Jump
    _slides = (None, SLIDES_UP, SLIDES_DOWN, SLIDES, SLIDES)
    _jumps = (None, JUMPS_UP, JUMPS_DOWN, JUMPS, JUMPS)
    # _adj = ADJ TODO utlize adj

    def __init__(self):
        super().__init__(32)
        self._indices = (None, set(range(20, 32)), set(range(0, 12)),
                         set(), set())
        for i in range(20, 32):
            self._board[i] = 1 
        for i in range(0, 12):
            self._board[i] = 2

    def _legal_slides(self):
        """Return list of legal jumps."""
        trn = self.turn()
        return tuple(slide for piece in (trn, trn+2)
                           for index in self._indices[piece]
                           for slide in self._slides[piece][index]
                           if not self._board[slide.stop])

    def _add_piece_paths(self, piece, index):
        self._board[index] = piece
        self._indices[piece].add(index)

    def _del_piece_paths(self, index):
        """Update board, indices with removed piece."""
        piece = self._board[index]
        self._board[index] = 0
        self._indices[piece].remove(index)

    def _append_paths(self, jump, trn):
        # can only promote once
        piece = self._board[jump.start]
        if jump.promotion and piece > 2:
            jump = jump._replace(promotion=False)   

        # start
        self._del_piece_search(jump.start)

        # stop
        if jump.promotion:
            piece = trn + 2
        self._add_piece_search(piece, jump.stop)

        # capture
        jump = jump._replace(piece=self._board[jump.capture])
        self._del_piece_search(jump.capture) 

        self._actions.append(jump)

        for piece in range(1, 5):
            for index in self._indices[piece]:
                assert self._board[index] == piece

        return jump
         
    def _pop_paths(self): 
        self.winner = None
        action = self._actions.pop() 

        # capture
        self._add_piece_search(action.piece, action.capture)
        
        # stop
        piece = self._board[action.stop]
        self._del_piece_search(action.stop)

        # start
        if action.promotion:
            piece -= 2
        self._add_piece_search(piece, action.start)

    def _legal_paths(self, jump):
        oth = self.other()

        def pred(jump):
            return (self._board[jump.capture] in (oth, oth+2) and
                    not self._board[jump.stop])
        
        def explore(jump):
            paths = []
            jump = self._append_paths(jump) 
            for adj in self._jumps[self._board[jump.start]][jump.stop]:
                if pred(adj):
                    paths.extend([jump] + path for path in explore(adj))
            self._pop_paths(jump)
            return paths if paths else [[jump]]

        if not pred(jump):
            return []
        paths = explore(jump)
        if len(paths) == 1:
            return paths[0]
        for path in paths:
            start = path[0].start
            stop = path[-1].stop
            promotion = any(jump.promotion for jump in path)
            captures = tuple(jump.capture for jump in path)
            pieces = tuple(jump.piece for jump in path)
            yield Path(start, stop, promotion, captures, pieces)

    # def _legal_jumps(self):
    #     """Return list of legal jumps."""
    #     # TODO multiple jumps
    #     trn = self.turn()
    #     return tuple(action
    #                  for piece in (trn, trn+2)
    #                  for index in self._indices[piece]
    #                  for jump in self._jumps[piece][index]
    #                  for action in self._legal_paths(jump))
                          

    def _legal_jumps(self):
        """Return list of legal jumps."""
        # TODO multiple jumps
        trn = self.turn()
        oth = self.other()
        return tuple(jump for piece in (trn, trn+2)
                          for index in self._indices[piece]
                          for jump in self._jumps[piece][index]
                          if (self._board[jump.capture] in (oth, oth+2) and
                              not self._board[jump.stop]))

    def legal_actions(self):
        # TODO use start stop tuples for action
        return self._legal_jumps() or self._legal_slides()
         
    def _legal_slide(self, slide):
        """Return True if slide is a legal action."""
        # next position must be empty
        if self._board[slide.stop]:
            return False
        trn = self.turn()
        piece = self._board[slide.start]
        return ((piece == trn and bool(trn - 1) != slide.up) or 
                (piece - 2 == trn))

    def _legal_jump(self, jump):
        """Return True if jump is a legal action."""
        oth = self.other()
        return (self._board[jump.capture] in (oth, oth+2) and
                self._legal_slide(jump))

    def legal(self, action):
        if action is None:
            return False
        if isinstance(action, Jump):
            return self._legal_jump(action)
        return not self._legal_jumps() and self._legal_slide(action)

    # TODO _check_winner, _legal, _turn, _other, _hash_calc
    def check_winner(self):
        if not self.legal_actions():
            self.winner = self.other()
        # trn = self.turn()
        # if not self._indices[trn] and not self._indices[trn+2]:
        #     self.winner = self.other()

    def _add_piece(self, piece, index):
        """Update board, hash, indices with added piece."""
        self._board[index] = piece
        self._hash_value += self.hash_calc(piece, index)
        self._indices[piece].add(index)

    def _del_piece(self, index):
        """Update board, hash, indices with removed piece."""
        piece = self._board[index]
        self._board[index] = 0
        self._hash_value -= self.hash_calc(piece, index)
        self._indices[piece].remove(index)

    def append(self, action):
        # TODO use start stop tuples for action,
        # start, stop = action
        # action = self._adj[start][stop]
        assert self.legal(action), (
            'illegal action by agent%d' % (self.turn()) + repr(self),)
        trn = self.turn()

        # can only promote once
        piece = self._board[action.start]
        if action.promotion and piece > 2:
            action = action._replace(promotion=False)   

        # start
        self._del_piece(action.start)

        # stop
        if action.promotion:
            piece = trn + 2
        self._add_piece(piece, action.stop)

        # capture
        if isinstance(action, Jump):
            assert piece == self._board[action.capture], (piece, self._board[action.capture])
            # action = action._replace(piece=self._board[action.capture])
            self._del_piece(action.capture)
        elif isinstance(action, Path):
            for piece, capture in zip(action.pieces, action.captures):
                assert piece == self._board[capture], (piece, self._board[capture])
            for capture in action.captures:
                self._del_piece(capture) 
            

        self._actions.append(action)
        self.check_winner()

        print(action)
        print(self.winner, self._indices)
        for piece in range(1, 5):
            for index in self._indices[piece]:
                assert self._board[index] == piece
         
    def pop(self): 
        self.winner = None
        action = self._actions.pop() 

        # capture
        if isinstance(action, Jump):
            self._add_piece(action.piece, action.capture)
        elif isinstance(action, Path):
            for piece, capture in zip(action.pieces, action.captures):
                self._add_piece(piece, capture)
        
        # stop
        piece = self._board[action.stop]
        self._del_piece(action.stop) 

        # start
        if action.promotion:
            piece -= 2
        self._add_piece(piece, action.start)

        return action

    def clear(self):
        self._board[:] = [2]*12 + [0]*8 + [1]*12
        self._actions.clear()
        self._indices = (None, set(range(20, 32)), set(range(0, 12)),
                         set(), set())
        self._hash_value = 0 
        self.winner = None 

    def __str__(self):
        """Return string for command line interface.

        Examples
        --------
        /////////////////////    /////////////////////
        //   .   .   .   . //    //   o   o   o   o //
        // .   .   .   .   //    // o   o   o   o   //
        //   .   .   .   . //    //   o   o   o   o //
        // .   .   .   .   //    // .   .   .   .   //
        //   .   .   .   . //    //   .   .   .   . //
        // .   .   .   .   //    // x   x   x   x   //
        //   X   .   .   . //    //   x   x   x   x //
        // .   .   .   .   //    // x   x   x   x   //
        /////////////////////    /////////////////////

        """
        result = '/'*21 + '\n'
        even = True
        for row in self._rows:
            line = '// '
            if even:
                line += ' '.join('  ' + self._pieces[actn] 
                                 for actn in self._board[row])
            else:
                line += ' '.join(self._pieces[actn] + '  '
                                 for actn in self._board[row])
            even = not even
            line += ' //'
            result += line + '\n'
        result += '/'*21
        return result
