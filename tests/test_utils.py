import unittest
import copy
import random

from utils.disjointset import DisjointSet

class DisjointSetTestCase(unittest.TestCase):

    def setUp(self):
        self.D = DisjointSet(81)

    def test_connect_undo(self): 
        self.D.clear()
        to_connect = [random.sample(range(len(self.D)), 2) for _ in range(100)]
        for i,j in to_connect:
            S = copy.deepcopy(self.D)
            ri, rj = sorted((self.D.root(i), self.D.root(j)), 
                            key=lambda x: self.D.weight(x), reverse=True)
            if ri == rj:
                continue
            self.D.connect(ri, rj)
            if random.random() < .5:
                with self.subTest(ri=ri, rj=rj):
                    self.D.undo_connect(ri, rj)
                    self.assertEqual(self.D, S, '\n'+str(S)+'\n'+str(self.D))
                if S != self.D:
                    break

    def test_undo(self): 
        self.D.clear()
        to_connect = [random.sample(range(len(self.D)), 2) for _ in range(100)]

        for i,j in to_connect:
            ri, rj = sorted((self.D.root(i), self.D.root(j)), 
                            key=lambda x: self.D.weight(x), reverse=True)

            if ri != rj:
                S = copy.deepcopy(self.D)
                self.D.connect(ri, rj)
                if random.random() < .5:
                    with self.subTest(ri=ri, rj=rj):
                        self.D.undo_connect(ri, rj)
                        self.assertEqual(self.D, S, 
                                         '\n'+str(S)+'\n'+str(self.D))
                    if S != self.D:
                        break

            if random.random() < .2:
                S = copy.deepcopy(self.D)
                root = self.D.root(random.randrange(len(self.D)))
                component = tuple(i for i in range(len(self.D)) 
                                  if self.D.root(i) == root)
                self.D.atomize(component)
                if random.random() < .5:
                    with self.subTest(component=component):
                        self.D.undo_atomize(component)
                        self.assertEqual(self.D, S, 
                                         '\n'+str(S)+'\n'+str(self.D))
                    if S != self.D:
                        print('\n'+repr(S)+'\n'+repr(self.D))
                        break
