from agents.agent import Agent
from logs.log import get_logger

LOGGER = get_logger(__name__)

class TestAgent(Agent):

    def __init__(self, name='test', actions=()):
        super().__init__(name) 
        self._actions = list(reversed(actions))

    def act(self, game):
        action = self._actions.pop()
        LOGGER.info('{!r}\tACTION: {!s}'.format(self, action))
        return action

    def clear(self):
        self._record = dict.fromkeys(self._record, 0)
        LOGGER.info('{!r}\tRECORD CLEARED'.format(self))
