from agents.agent import Agent
from logs.log import get_logger

LOGGER = get_logger(__name__)

class RandomAgent(Agent):

    def __init__(self, name='random'):
        super().__init__(name) 

    def act(self, game):
        action = random.choice(game.legal_actions())
        LOGGER.info('{!r}\tACTION: {!s}'.format(self, action))
        return action

    def clear(self):
        self._record = dict.fromkeys(self._record, 0)
        LOGGER.info('{!r}\tRECORD CLEARED'.format(self))
