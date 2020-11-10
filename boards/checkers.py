import numpy as np
from collections import namedtuple

from boards.board import get_winners, get_hashes, boards, Board

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
_EDGES = [[None]*4 for i in range(32)]
# up/left
for i in range(5, 37, 8):
    for j in range(i, i+3):
        _EDGES[j][0] = j-5
for i in range(8, 32, 8):
    for j in range(i, i+4):
        _EDGES[j][0] = j-4
# up/right
for i in range(4, 36, 8):
    for j in range(i, i+4):
        _EDGES[j][1] = j-4
for i in range(8, 32, 8):
    for j in range(i, i+3):
        _EDGES[j][1] = j-3
# down/left
for i in range(0, 32, 8):
    for j in range(i, i+4):
        _EDGES[j][2] = j+4
for i in range(5, 29, 8):
    for j in range(i, i+3):
        _EDGES[j][2] = j+3
# down/right
for i in range(0, 32, 8):
    for j in range(i, i+3):
        _EDGES[j][3] = j+5
for i in range(4, 28, 8):
    for j in range(i, i+4):
        _EDGES[j][3] = j+4

# actions
Slide  = namedtuple('Slide', 'up start stop promotion')
Jump   = namedtuple( 'Jump', 'up start stop promotion capture  piece')
Path   = namedtuple( 'Path',    'start stop promotion captures pieces')

SLIDES_UP   = [[] for _ in range(32)]
SLIDES_DOWN = [[] for _ in range(32)]
SLIDES      = [[] for _ in range(32)]
JUMPS_UP    = [[] for _ in range(32)]
JUMPS_DOWN  = [[] for _ in range(32)]
JUMPS       = [[] for _ in range(32)]

# TODO cleaner style?
for start, adj in enumerate(_EDGES):
    for stop in adj[:2]:
        if stop is None:
            continue
        promotion = False if stop > 3 else True
        slide = Slide(True, start, stop, promotion)
        SLIDES_UP[start].append(slide)
        SLIDES[start].append(slide._replace(promotion=False)) # promote once
    for stop in adj[2:]:
        if stop is None:
            continue
        promotion = False if stop < 28 else True
        slide = Slide(False, start, stop, promotion)
        SLIDES_DOWN[start].append(slide)
        SLIDES[start].append(slide._replace(promotion=False))

for start, adj in enumerate(_EDGES):
    for direc, capture in enumerate(adj):
        if capture is None:
            continue
        stop = _EDGES[capture][direc] 
        if stop is None:
            continue
        if direc < 2:
            promotion = False if stop > 3 else True
            jump = Jump(True, start, stop, promotion, capture, None)
            JUMPS_UP[start].append(jump)
            JUMPS[start].append(jump._replace(promotion=False))
        else:
            promotion = False if stop < 28 else True
            jump = Jump(False, start, stop, promotion, capture, None)
            JUMPS_DOWN[start].append(jump)
            JUMPS[start].append(jump._replace(promotion=False))

SLIDES_UP   = tuple(tuple(slides) for slides in SLIDES_UP)
SLIDES_DOWN = tuple(tuple(slides) for slides in SLIDES_DOWN)
SLIDES      = tuple(tuple(slides) for slides in SLIDES)
JUMPS_UP    = tuple(tuple(jumps) for jumps in JUMPS_UP)
JUMPS_Down  = tuple(tuple(jumps) for jumps in JUMPS_DOWN)
JUMPS       = tuple(tuple(jumps) for jumps in JUMPS)

del _EDGES

@boards('checkers')
class CheckersBoard(Board):

    _pieces = PIECES  # strs
    _rows = ROWS  # slices
    _hashes = HASHES  # ints

    _slides = (None, SLIDES_UP, SLIDES_DOWN, SLIDES, SLIDES)
    _jumps = (None, JUMPS_UP, JUMPS_DOWN, JUMPS, JUMPS)

    def __init__(self):
        super().__init__(32)
        self._indices = (None, set(range(20, 32)), set(range(0, 12)),
                         set(), set())
        for i in range(20, 32):
            self._add_piece(1, i)
        for i in range(0, 12):
            self._add_piece(2, i)
        self._start_hash_value = self._hash_value

    def _legal_slides(self):
        """Return list of legal jumps."""
        trn = self.turn()
        return tuple(slide for piece in (trn, trn+2)
                           for index in self._indices[piece]
                           for slide in self._slides[piece][index]
                           if not self._board[slide.stop])

    def _add_piece_paths(self, piece, index):
        """Update board, indices with added piece. Hash unaffected."""
        self._board[index] = piece
        self._indices[piece].add(index)

    def _del_piece_paths(self, index):
        """Update board, indices with removed piece. Hash unaffected."""
        piece = self._board[index]
        self._board[index] = 0
        self._indices[piece].remove(index)

    def _append_paths(self, jump):
        piece = self._board[jump.start]

        # start
        self._del_piece_paths(jump.start)

        # stop
        if jump.promotion:
            piece += 2
        self._add_piece_paths(piece, jump.stop)

        # capture
        jump = jump._replace(piece=self._board[jump.capture])
        self._del_piece_paths(jump.capture) 

        self._actions.append(jump)

        for piece in range(1, 5):
            for index in self._indices[piece]:
                assert self._board[index] == piece

        return jump
         
    def _pop_paths(self): 
        action = self._actions.pop() 

        # capture
        self._add_piece_paths(action.piece, action.capture)
        
        # stop
        piece = self._board[action.stop]
        self._del_piece_paths(action.stop)

        # start
        if action.promotion:
            piece -= 2
        self._add_piece_paths(piece, action.start)

    def _legal_paths(self, jump):
        """DFS all paths with jump as first edge.""" 
        oth = self.other()

        def pred(jump):
            """Return True if jump is legal."""
            return (self._board[jump.capture] in (oth, oth+2) and
                    not self._board[jump.stop])
        
        def explore(jump):
            """Depth first search graph of positions (nodes), jumps (edges)."""
            paths = []
            jump = self._append_paths(jump) 
            for adj in self._jumps[self._board[jump.stop]][jump.stop]:
                if pred(adj):
                    paths.extend([jump] + path for path in explore(adj))
            self._pop_paths()
            return paths if paths else [[jump]]


        if not pred(jump):
            return []
        paths = explore(jump)

        if len(paths) == 1 and len(paths[0]) == 1:
            jump = paths[0][0]
            jump = jump._replace(piece=self._board[jump.capture])
            yield jump
            return

        for path in paths:
            start = path[0].start
            stop = path[-1].stop
            promotion = any(jump.promotion for jump in path)
            captures = tuple(jump.capture for jump in path)
            pieces = tuple(jump.piece for jump in path)
            yield Path(start, stop, promotion, captures, pieces)

    def _legal_jumps(self):
        """Return list of legal jumps."""
        trn = self.turn()
        return tuple(action
                     for piece in (trn, trn+2)
                     for index in self._indices[piece]
                     for jump in self._jumps[piece][index]
                     for action in self._legal_paths(jump))
                          
    def legal_actions(self):
        """Return all legal jumps and paths. If none, return legal slides."""
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

    def _legal_path(self, path):
        """Return True if path is a legal action."""
        trn = self.turn()
        oth = self.other()
        return (all(self._board[capture] in (oth, oth+2)
                    for capture in path.captures) and
                all(self._board[capture] == piece for capture, piece 
                    in zip(path.captures, path.pieces)) and
                (not self._board[path.stop] or path.start == path.stop) and
                self._board[path.start] in (trn, trn+2))

    def legal(self, action):
        """Return True if aciton is legal."""
        if action is None:
            return False
        if isinstance(action, Jump):
            return self._legal_jump(action)
        if isinstance(action, Path):
            return self._legal_path(action)
        return not self._legal_jumps() and self._legal_slide(action)

    # TODO _check_winner, _legal, _turn, _other, _hash_calc
    def check_winner(self):
        if not self.legal_actions():
            self.winner = self.other()
        # TODO optimizations: False when moves < 20
        #                     yield legal actions

    def _add_piece(self, piece, index):
        """Update board, hash, indices with added piece."""
        self._board[index] = piece
        self._hash_value ^= self.hash_calc(piece, index)
        self._indices[piece].add(index)

    def _del_piece(self, index):
        """Update board, hash, indices with removed piece."""
        piece = self._board[index]
        self._board[index] = 0
        self._hash_value ^= self.hash_calc(piece, index)
        self._indices[piece].remove(index)

    def append(self, action):
        assert self.legal(action), (
            'illegal action by agent%d: %s\n%s' % (self.turn(), action, self))
        # cache start piece before deleted
        piece = self._board[action.start]

        # start
        # remove start first since stop may equal start
        self._del_piece(action.start)

        # stop
        if action.promotion:
            piece += 2
        self._add_piece(piece, action.stop)

        # capture
        if isinstance(action, Jump):
            assert action.piece == self._board[action.capture], (action.piece, self._board[action.capture], action, self)
            # action = action._replace(piece=self._board[action.capture])
            self._del_piece(action.capture)
        elif isinstance(action, Path):
            for piece, capture in zip(action.pieces, action.captures):
                assert piece == self._board[capture], (piece, self._board[capture])
            for capture in action.captures:
                self._del_piece(capture) 
            
        self._actions.append(action)
        self.check_winner()

        # print('Indices: %s' % str(self._indices))
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
        self._hash_value = self._start_hash_value
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

    # logger interface

    def info(self):
        return [self._action_str(action) for action in self]

    def _action_str(self, action):
        """Return triplet: start, stop, captures."""
        if isinstance(action, Slide):
            capture = ()
        elif isinstance(action, Jump):
            capture = (action.capture,)
        else: # isinstance(action, Path)
            capture = action.captures
        return (action.start, action.stop, capture)

    # agent interface

    def heuristic(self):
        # TODO: actual heuristic
        return np.zeros(19557, dtype=np.bool)
