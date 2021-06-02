# Authors: Drake Moore, John Lam, Nathan Cheng
# searchAgents.py


import chess
from myChess import MyChess
from multiplier import Multiplier
import evaluation
import random

# -----------------------------------------------------------------------------------------------------------
# Search Agents
# -----------------------------------------------------------------------------------------------------------

class multiSearchAgent():
    # initializes the chessbot with an instance of myChess
    def __init__(self, chess_state: MyChess, eval_func=evaluation.add_eval, max_depth=1):
        self.myChess = chess_state
        self.board = self.myChess.board
        self.eval_func = eval_func
        self.max_depth = max_depth

    # Gets the next best action, based on the given gamestate (myChess), and whose turn we are selecting an action for
    def get_action(self, chess_state: MyChess, turn):
        raise NotImplementedError("multiSearchAgent.get_action is not defined; see child classes instead")


class minimaxAgent(multiSearchAgent):

    # Gets the next best action, based on the given gamestate (myChess), and whose turn we are selecting an action for
    # Has an optional parameter max_depth to choose a different depth than self.max_depth
    # TODO: Should we add an optional eval_func parameter here? Or just stick with self.eval_func?
    def get_action(self, chess_state: MyChess, max_depth=None):
        if max_depth is None:
            max_depth = self.max_depth

        # The action from this method call is stored in the 0th index of the tuple
        # TODO: Make this choose randomly for bot tourneys?? At the moment, always chooses the first move
        #  for consistency (for testing)
        return self.minimax(0, max_depth, chess_state, True)[0]

    # minimax evaluation function only returns best evaluation scores
    # max_turn defines is we are maxing white's turn or black's turn
    # returns a tuple of (move, value)
    def minimax(self, curr_depth, target_depth, chess_state, max_turn):
        if curr_depth == target_depth or chess_state.is_game_over():
            return None, self.eval_func(chess_state)

        values = {}
        if max_turn:
            for move in chess_state.str_legal_moves():
                next_board = chess_state.try_move(move)
                # The value from the recursive call is stored in the 1st index of the tuple
                values[move] = self.minimax(curr_depth + 1, target_depth, MyChess(next_board), False)[1]

            best_val = max(values.values())

        else: # it is currently the minimizer's turn
            for move in chess_state.str_legal_moves():
                next_board = chess_state.try_move(move)
                values[move] = self.minimax(curr_depth + 1, target_depth, MyChess(next_board), True)[1]

            best_val = min(values.values())

        best_moves = [move for (move, value) in values.items() if value == best_val]
        return (best_moves[0], best_val)




class alphaBetaPruningAgent(multiSearchAgent):

    # Gets the next best action, based on the given gamestate (myChess), and whose turn we are selecting an action for
    # Has an optional parameter max_depth to choose a different depth than self.max_depth
    # TODO: Should we add an optional eval_func parameter here? Or just stick with self.eval_func?
    def get_action(self, chess_state: MyChess, max_depth=None):
        if max_depth is None:
            max_depth = self.max_depth
        self.color = chess_state.get_turn()
        # The action from this method call is stored in the 0th index of the tuple
        return self.alpha_beta_minimax(0, max_depth, chess_state, True, float('-inf'), float('inf'))[0]

    # Performs alpha-beta minimax on the given chess state. Returns a tuple of (move, value)
    def alpha_beta_minimax(self, curr_depth, target_depth, chess_state, max_turn, alpha, beta):
        if curr_depth >= target_depth or chess_state.is_game_over():
            return None, self.eval_func(chess_state, self.color)

        values = {}

        if max_turn:
            for move in chess_state.str_legal_moves():
                next_board = chess_state.try_move(move)
                # The value from the recursive call is stored in the 1st index of the tuple
                values[move] = self.alpha_beta_minimax(curr_depth + 1, target_depth, MyChess(next_board), False, alpha, beta)[1]
                alpha = max(alpha, values[move])
                if beta <= alpha:
                    break

            best_val = max(values.values())

        else:  # it is currently the minimizer's turn
            for move in chess_state.str_legal_moves():
                next_board = chess_state.try_move(move)
                values[move] = self.alpha_beta_minimax(curr_depth + 1, target_depth, MyChess(next_board), True, alpha, beta)[1]
                beta = min(beta, values[move])
                if beta <= alpha:
                    break

            best_val = min(values.values())

        best_moves = [move for (move, value) in values.items() if value == best_val]
        return (best_moves[0], best_val)

class quietSearch(multiSearchAgent):

    def isCaptureMove(self, chess_state, move):
        return chess_state.board.piece_at(move.to_square) is not None

    #all the moves to capture a piece
    def getCaptureMoves(self, chess_state):
        legalMoves = chess_state.str_legal_moves()
        captureMoves = []

        for move in legalMoves:
            chessMove = chess.Move.from_uci(move)
            if self.isCaptureMove(chess_state, chessMove):
                captureMoves.append(move)

        if captureMoves == []:
            return None
        return captureMoves

    def get_action(self, chess_state: MyChess, max_depth=None):
        if max_depth is None:
            max_depth = self.max_depth
        self.color = chess_state.get_turn()
        num_pieces = chess_state.get_num_pieces(self.color)
        if num_pieces <= 4:
            max_depth = 4
        # The action from this method call is stored in the 0th index of the tuple
        return self.alpha_beta_minimax(0, max_depth, chess_state, True, float('-inf'), float('inf'))[0]

    # Performs alpha-beta minimax on the given chess state. Returns a tuple of (move, value)
    def qSearch(self, curr_depth, max_depth, chess_state, max_turn, alpha, beta):
        capture_moves = self.getCaptureMoves(chess_state)
        if chess_state.is_game_over() or capture_moves is None or curr_depth == max_depth:
            return None, self.eval_func(chess_state, self.color)

        values = {}

        if max_turn:
            for move in capture_moves:
                next_board = chess_state.try_move(move)
                # The value from the recursive call is stored in the 1st index of the tuple
                values[move] = \
                self.qSearch(curr_depth + 1, max_depth, MyChess(next_board), False, alpha, beta)[1]
                alpha = max(alpha, values[move])
                if beta <= alpha:
                    break

            best_val = max(values.values())

        else:  # it is currently the minimizer's turn
            for move in capture_moves:
                next_board = chess_state.try_move(move)
                values[move] = \
                self.qSearch(curr_depth + 1, max_depth, MyChess(next_board), True, alpha, beta)[1]
                beta = min(beta, values[move])
                if beta <= alpha:
                    break

            best_val = min(values.values())

        best_moves = [move for (move, value) in values.items() if value == best_val]

        return (best_moves[0], best_val)



    # Performs alpha-beta minimax on the given chess state. Returns a tuple of (move, value)
    def alpha_beta_minimax(self, curr_depth, target_depth, chess_state, max_turn, alpha, beta):
        if curr_depth >= target_depth or chess_state.is_game_over():
            return None, self.eval_func(chess_state, self.color)

        values = {}

        if max_turn:
            for move in chess_state.str_legal_moves():
                next_board = chess_state.try_move(move)
                if chess_state.board.piece_at(chess.Move.from_uci(move).to_square) is not None:
                    values[move] = self.qSearch(curr_depth + 1, 10, MyChess(next_board), False, alpha, beta)[1]
                else:
                # The value from the recursive call is stored in the 1st index of the tuple
                    values[move] = self.alpha_beta_minimax(curr_depth + 1, target_depth, MyChess(next_board),
                                                           False, alpha, beta)[1]
                alpha = max(alpha, values[move])
                if beta <= alpha:
                    break

            best_val = max(values.values())

        else:  # it is currently the minimizer's turn
            for move in chess_state.str_legal_moves():
                next_board = chess_state.try_move(move)
                if chess_state.board.piece_at(chess.Move.from_uci(move).to_square) is not None:
                    values[move] = self.qSearch(curr_depth + 1, 10, MyChess(next_board), True, alpha, beta)[1]
                else:
                    values[move] = self.alpha_beta_minimax(curr_depth + 1, target_depth, MyChess(next_board),
                                                           True, alpha, beta)[1]
                beta = min(beta, values[move])
                if beta <= alpha:
                    break

            best_val = min(list(values.values()))

        best_moves = [move for (move, value) in values.items() if value == best_val]
        return (best_moves[0], best_val)








class nullMoveAlphaBetaAgent(alphaBetaPruningAgent):

    def get_action(self, chess_state: MyChess, max_depth=None):
        if max_depth is None:
            max_depth = self.max_depth
        self.color = chess_state.get_turn()
        num_pieces = chess_state.get_num_pieces(self.color)
        if num_pieces <= 4:
            max_depth += 2
        # The action from this method call is stored in the 0th index of the tuple
        return self.alpha_beta_minimax(0, max_depth, chess_state, True, float('-inf'), float('inf'))[0]

    # Performs alpha-beta minimax with a null heuristic on a chess state. Returns a single move
    def alpha_beta_minimax(self, curr_depth, target_depth, chess_state, max_turn, alpha, beta):
        return self.ab_null_heuristic_minimax(curr_depth, target_depth, chess_state, max_turn, alpha, beta, False)

    # Performs alpha-beta minimax with a null heuristic on a chess state. Returns a tuple in the form of
    # ((move, value), cutoff), where cutoff is a boolean that indicates if the condition beta <= alpha
    # was ever reached.
    def ab_null_heuristic_minimax(
            self, curr_depth, target_depth, chess_state, max_turn, alpha, beta, last_move_was_null):
        if curr_depth >= target_depth or chess_state.is_game_over():
            return ((None, self.eval_func(chess_state, self.color)), False)


        # Check for zugzwang. In other words, perform a shallow null-move alpha-beta search
        # if and only if all of the conditions below are true:
        #  - The side to move is not in check
        #  - The side to move has only its king and pawns remaining
        #  - The side to move has a small number (defined here as less than 5) pieces remaining
        #  - The previous move in the search was also a null move
        if not last_move_was_null and not self.is_zugzwang(chess_state):
            move, val = self.ab_null_heuristic_minimax(
                curr_depth + 1, target_depth // 2, chess_state, not max_turn, alpha, beta, True)
            if beta <= val:
                return (move, val)

        values = {}

        if max_turn:
            for move in chess_state.str_legal_moves():
                next_board = chess_state.try_move(move)
                # The value from the recursive call is stored in the 1st index of the tuple
                values[move] = self.ab_null_heuristic_minimax(
                    curr_depth + 1, target_depth, MyChess(next_board), False, alpha, beta, False)[1]
                alpha = max(alpha, values[move])
                if beta <= alpha:
                    break

            best_val = max(values.values())

        else:  # it is currently the minimizer's turn
            for move in chess_state.str_legal_moves():
                next_board = chess_state.try_move(move)
                values[move] = self.ab_null_heuristic_minimax(
                    curr_depth + 1, target_depth, MyChess(next_board), True, alpha, beta, False)[1]
                beta = min(beta, values[move])
                if beta <= alpha:
                    break

            best_val = min(values.values())

        best_moves = [move for (move, value) in values.items() if value == best_val]
        return (best_moves[0], best_val)

    # Check for zugzwang. In other words, check if any one of the conditions below are true:
    #  - The side to move is not in check
    #  - The side to move has only its king and pawns remaining
    #  - The side to move has a small number (defined here as less than 5) pieces remaining
    #  - The previous move in the search was also a null move
    def is_zugzwang(self, chess_state):
        return chess_state.in_check() or self.zugzwang_helper(chess_state)

    # Checks if the side to move has only its king and pawns remaining, or if the side to move has less than
    # 5 pieces remaining
    def zugzwang_helper(self, chess_state):
        piece_list = chess_state.get_piece_list()
        turn = chess_state.get_turn()
        total_pieces = 0
        only_king_and_pawns = True

        for (piece, _) in piece_list:
            if turn and piece.isupper():
                if piece != "K" and piece != "P":
                    only_king_and_pawns = False
                total_pieces += 1

            elif turn and piece.islower():
                if piece != "k" and piece != "p":
                    only_king_and_pawns = False
                total_pieces += 1

        return only_king_and_pawns or total_pieces < 5
