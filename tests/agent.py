from agents.agent import Agent

class TestAgent(Agent):

    def __init__(self, name='test', actions=()):
        super().__init__(name) 
        self._actions = list(reversed(actions))

    def act(self, game):
        action = self._actions.pop()
        return action

    def clear(self):
        self._record = dict.fromkeys(self._record, 0)
