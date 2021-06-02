from myChess import MyChess
from searchAgents import minimaxAgent, alphaBetaPruningAgent, nullMoveAlphaBetaAgent, quietSearch
from random import randint
from evaluation import evaluate, add_eval
from chessGUI import chessGUI

# a class that represents a bot that you can play with
class chessBot:
    def __init__(self, chess_state: MyChess= None, bot=None, eval_func=evaluate, depth=1, player_turn: bool=True):
        if bot is None or player_turn is None:
            raise ValueError("Error: chessBot configuration is invalid: Given bot is None")

        self.chess_state = chess_state if chess_state is not None else MyChess()
        self.bot = bot(self.chess_state, eval_func, depth)
        # self.player_turn represents the color that you (the player) are playing as;
        # the bot will play the opposite color
        self.player_turn = player_turn

    def get_state(self):
        return self.chess_state

    def get_player(self):
        return self.player_turn

    # Makes a move based on the current gamestate and agent. Returns the executed move.
    def make_move(self):
        move = self.bot.get_action(self.chess_state)
        self.chess_state.execute_move(move)
        return move

def main():
    white, black = True, False

    chess_bot = chessBot(MyChess(), quietSearch, add_eval, 2, white)
    #gui = chessGUI.twoPlayerChessGUI()

    gui = chessGUI.onePlayerChessGUI(chess_bot)
    gui.run_game()


if __name__ == "__main__":
    main()
