import unittest
import random

from boards.tictactoe import TicTacToeBoard

class TicTacToeBoardTestCase(unittest.TestCase):

    def setUp(self):
        self.board = TicTacToeBoard()
    
    def tearDown(self): 
        del self.board

    def test_legal_actions(self):
        self.assertEqual(9, len(self.board.legal_actions()))

    def test_legal(self):
        for action in range(9):
            self.assertTrue(self.board.legal(action))

    def test_len(self):
        self.assertEqual(0, len(self.board))

    def test_append(self):
        actions = random.sample(range(9), 5)
        ln = 0
        tn = 1
        ot = 2 
        for i in range(5):
            with self.subTest(i=i):
                self.assertTrue(self.board)
                self.board.append(actions.pop())
                ln += 1
                self.assertEqual(ln, len(self.board))
                tn, ot = ot, tn
                self.assertEqual(tn, self.board.turn())
                self.assertEqual(ot, self.board.other())
        self.board.clear()

    def test_pop(self):
        actions = random.sample(range(9), 5)
        for action in actions:
            self.board.append(action)
        tn = 1
        for i in range(4, -1, -1):
            with self.subTest(i=i):
                self.assertEqual(actions.pop(), self.board.pop())
                self.assertEqual(i, len(self.board))
                self.assertEqual(tn, self.board.turn())
                self.assertTrue(self.board)
                tn = 3 - tn
        self.board.clear()

    def test_clear(self):
        for action in random.sample(range(9), 9):
            self.board.append(action)
            self.board.pop()
        self.board.clear()
        self.assertEqual(0, len(self.board))
        self.assertEqual(9, len(self.board.legal_actions()))
        self.assertTrue(self.board)

    def test_turn(self):
        self.assertEqual(1, self.board.turn())

    def test_other(self):
        self.assertEqual(2, self.board.other())

    def test_mock_game(self):
        self.assertTrue(self.board)
        actions = [[0, 3, 1, 4, 2],
                   [0, 1, 3, 4, 8, 7],
                   [4, 0, 1, 7, 3, 5, 2, 6, 8],
                  ]
        bools = [[True]*4 + [False],
                 [True]*5 + [False],
                 [True]*8 + [False],
                ]
        winners = [[None]*4 + [1],
                   [None]*5 + [2],
                   [None]*8 + [0],
                  ]
        strings = [['000000001',
                    '000002001',  
                    '000002011',  
                    '000022011',  
                    '000022111'],  
                   ['000000001',
                    '000000021',
                    '000001021',
                    '000021021',
                    '100021021',
                    '120021021'],
                   ['000010000',
                    '000010002',
                    '000010012',
                    '020010012',
                    '020011012',
                    '020211012',
                    '020211112',
                    '022211112',
                    '122211112']
                  ]

        for acts, blns, wins in zip(actions, bools, winners):
            with self.subTest(acts=acts, blns=blns, wins=wins):
                for a, b, w in zip(acts, blns, wins):
                    with self.subTest(a=a, b=b, w=w):
                        self.board.append(a)
                        self.assertEqual(b, bool(self.board))
                        self.assertEqual(w, self.board.winner)
            self.board.clear()
