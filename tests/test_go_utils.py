import unittest
import copy
import random
from board_games.go.utils import DisjointSet, LibertiesDisjointSet
from board_games.go.board import ADJS

class DisjointSetTestCase(unittest.TestCase):

    def setUp(self):
        self.D = DisjointSet(81)
        self.to_connect = [random.sample(range(len(self.D)), 2)
                           for _ in range(1000)]

    def test_random(self): 
        for i,j in self.to_connect:
            S = copy.deepcopy(self.D)
            self.D.connect(i, j)
            if random.random() < .5:
                with self.subTest(i=i, j=j):
                    self.D.undo()
                    self.assertEqual(self.D, S, '\n'+str(S)+'\n'+str(self.D))
                if S != self.D:
                    break

class LibertiesDisjointSetTestCase(DisjointSetTestCase, unittest.TestCase):

    def setUp(self):
        self.D = LibertiesDisjointSet(81, ADJS)
        self.to_connect = [random.sample(range(len(self.D)), 2)
                           for _ in range(1000)]
