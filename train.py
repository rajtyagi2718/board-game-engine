from logs.log import get_logger
from models.treestrap_minimax import TreeStrapMinimax
from board_games.base_class.agent import (
    RandomAgent, HeuristicAgent, TrainAgent)
from board_games.tictactoe.game import TicTacToeGame

def main(name, depth, alpha, runs):
    TSM = TreeStrapMinimax(name, depth, alpha)
    print('training started.')
    print('SEARCH: minimax')
    print(TSM._info())
    print('RUNS: {}'.format(runs))
    TSM.runs(runs)
    print('training done!')

    train_agent = TrainAgent('tree_strap_minimax') 
    random_agent = RandomAgent()
    heuristic_agent = HeuristicAgent('minimax')
        
    print('competition started.')
    game = TicTacToeGame(train_agent, random_agent)
    game.compete(100)
    print(game._info())
    game = TicTacToeGame(train_agent, heuristic_agent)
    game.compete(100)
    print(game._info())
    print('competition done!')

if __name__ == '__main__':
    main('tictactoe', 3, 1e-2, 100)
