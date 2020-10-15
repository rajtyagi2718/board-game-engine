from boards.boards import BOARDS
from games.game import Game

GAMES = {}

def GameFactory(name, gameclsname, boardcls):
    """Return game cls derived from Game.

    GameFactory('tictactoe', 'TicTacToeGame', TicTacToeBoard) 
    equivalent to
    
    class TicTacToeGame(Game):

        def __init__(self, agent1, agent):
            super().__init__(name, TicTacToeBoard(), agent1, agent2)

    """

    def __init__(self, agent1, agent2):
        Game().__init__(self, name, boardcls(), agent1, agent2)

    gamecls = type(gameclsname, (Game,), {'__init__' : __init__})
    return gamecls

# create and register games
# GAMES['tictactoe'] = TicTacToeGame
for name, boardcls in BOARDS.items():
    # 'TicTacToeBoard' -> 'TicTacToe'
    gameclsname = boardcls.__name__[:-5] += 'Game'
    gamecls = GameFactory(name, gameclsname, boardcls)

    # register gamecls with name in GAMES
    GAMES[name] = gamecls
