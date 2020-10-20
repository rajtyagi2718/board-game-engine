from pathlib import Path
import numpy as np

from agents.agent import Agent

WEIGHTS_PATH = Path('data/weights/')

class HeuristicAgent(Agent):

    def __init__(self, name, weights_path=WEIGHTS_PATH):
        super().__init__(name)
        self._weights = {}

        for path in weights_path.iterdir():
            # 'data/weights/tictactoe.txt' -> 'tictactoe'
            game_name = path.name[:-4]
            weights = np.genfromtxt(path, delimiter='\n', dtype=np.float64)
            self._weights[game_name] = weights

    def act(self, game):
        """Evaluate afterstate of each action. Linear appprox most valuable."""
        board = game._board
        actions = game.legal_actions()
        weights = self._weights[game._name]
        values = np.zeros(len(actions))
        argext = np.argmax if board.turn() == 1 else np.argmin

        for i, action in enumerate(actions):
            board.append(action)
            values[i] = weights @ board.heuristic()
            board.pop()

        action = actions[argext(values)]
        return action
