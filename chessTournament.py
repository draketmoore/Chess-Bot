# Authors: Drake Moore, John Lam, Nathan Cheng
# chessbot.py

from evaluation import add_eval, evaluate
from myChess import MyChess
from chessBot import chessBot
from searchAgents import alphaBetaPruningAgent, minimaxAgent, quietSearch, nullMoveAlphaBetaAgent

chess_state = MyChess()
whiteBot = chessBot(chess_state, quietSearch, add_eval, 4, True)
blackBot = chessBot(chess_state, alphaBetaPruningAgent, add_eval, 4, False)


movenum = 0
while True:
    if chess_state.is_game_over():
        break

    whiteBot.make_move()
    if chess_state.is_game_over():
        break
    blackBot.make_move()
    movenum += 1
    print("Move {0}".format(movenum))
    print(chess_state.get_pgn())

print(chess_state.board.outcome())
print(chess_state.get_pgn())
