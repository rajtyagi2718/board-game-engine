import random

from agents.agent import Agent

class RandomAgent(Agent):

    def __init__(self, name='random'):
        super().__init__(name) 

    def act(self, game):
        return random.choice(game.legal_actions())
