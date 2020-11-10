from logs.log import get_logger

LOGGER = get_logger(__name__)

class Game:
    """
    Handles game play: two agents alternate turns on board until win or draw.

    A board is given with two agents. During a run, they alternate taking a
    step by pushing an action onto the board. First agent starts on an empty
    board. When the board is terminal, the game run ends with a winner and
    loser, or both draw.
    """

    def __init__(self, name, board, agent1, agent2):
        self._name = name
        self._board = board
        self._agent1 = agent1
        self._agent2 = agent2

    def legal_actions(self):
        """Return all possible legal actions for current agent.

        Return:
        list

        """
        return self._board.legal_actions()

    def current_agent(self):
        """Return agent for current turn. Game awaits their action.

        Return:
        Agent

        """
        if self._board.turn() == 1:
            return self._agent1
        return self._agent2

    def other_agent(self):
        """Current agent acts next. Return the other agent.

        Return:
        Agent

        """
        if self._board.other() == 1:
            return self._agent1
        return self._agent2

    def step(self):
        """Query current agent to act. Push action onto board."""
        action = self.current_agent().act(self)
        LOGGER.debug(self.current_agent().debug(action)) 
        self._board.append(action)
        LOGGER.debug(self._board.debug())

    def run(self):
        """Take steps until board is terminal. Return winner: 0, 1, or 2."""
        while self._board:
            self.step()
        self._update_records()
        LOGGER.info(self.info())
        return self._board.winner

    def _update_records(self):
        """Increment each agent's (win, draw, loss) records."""
        u = self._board.utility()
        self._agent1.update_record(u)
        self._agent2.update_record(-u)

    def clear(self):
        """Return to intial state. Ready for new run."""
        self._board.clear()

    def change_agents(self, agent1=None, agent2=None):
        if agent1 is not None:
            self._agent1 = agent1
        if agent2 is not None:
            self._agent2 = agent2

    def swap_agents(self):
        self._agent1, self._agent2 = self._agent2, self._agent1

    def runs(self, num_runs, index_offset=1):
        LOGGER.info('AGENT1 {!s}\nAGENT2 {!s}'.format(
            self._agent1, self._agent2))
        for r in range(index_offset, num_runs + index_offset):
            LOGGER.info('RUN {}'.format(r))
            self.clear()
            self.run()

    def compete(self, num_runs):
        """Run game num_runs times. Swap who goes first halfway through."""
        LOGGER.info('GAME {!r}\nNUM RUNS {}'.format(self, num_runs))
        m = num_runs // 2
        self.runs(m)
        self.swap_agents()
        self.runs(num_runs-m, index_offset=m+1)
        self.swap_agents()
        log_info = 'GAME {!r}\nNUM RUNS {} complete!'
        log_info += '\nRESULTS\nAGENT1 {!r}\nAGENT2 {!r}\n'
        LOGGER.info(log_info.format(self, num_runs, self._agent1, self._agent2))

    def __repr__(self):
        """Return name - agent1 - agent2 - board.

        Return
        ------
        str

        """
        return '{} : {!s} vs {!s}'.format(
            self._name, self._agent1, self._agent2)

    def info(self):
        """Return board history for info logger."""
        winner = self._board.winner
        result = 'ACTIONS {}\nWINNER {} '.format(self._board.info(), winner)
        if winner:
            result += str(self.other_agent())
        else:
            result += 'draw'
        return result
