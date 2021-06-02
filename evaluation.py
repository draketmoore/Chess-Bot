# Authors: Drake Moore, John Lam, Nathan Cheng
# searchAgents.py


from myChess import MyChess
from multiplier import Multiplier, Adder
import chess
from enum import Enum

CHECKMATEVAL = 1000000

class Values(Enum):
    PAWN = 100
    KNIGHT = 320
    BISHOP = 330
    ROOK = 500
    QUEEN = 900
    KING = 20000

adder = Adder()



# -----------------------------------------------------------------------------------------------------------
# Evaluation Functions
# -----------------------------------------------------------------------------------------------------------


# returns an evaluation of the current board state for the given color
# positive integer means the color is winning. negative means losing
# 0 means the game is even.
def evaluate(chess_state: MyChess, color=None):
    board = chess_state.get_board()
    color = chess_state.get_turn() if color is None else color
    int_vals = MyChess.convert_to_int(board)

    evaluation = 0
    for val in int_vals:
        evaluation += val
    return evaluation if color else -evaluation


# Evaluation function using the Adder to add weights based on pieces positions
def add_eval(chess_state: MyChess, color=None):
    board = chess_state.get_board()
    color = chess_state.get_turn() if color is None else color

    if board.is_checkmate():
        return CHECKMATEVAL if chess_state.get_turn() != color else -CHECKMATEVAL
    if board.is_game_over():
        return 0
    evaluation = 0
    for col in range(8):
        for row in range(8):
            square = chess.square(col, row)
            piece = board.piece_at(square)
            if piece is not None:
                evaluation += getValueAtLocation(piece, col, row)

    # if color is white, return white evaluation, otherwise return black.
    return evaluation if color else -evaluation


def getValueAtLocation(piece, col, row):
    pieceSymbol = piece.symbol()
    pieceType = piece.piece_type
    global adder

    value = 0
    if pieceType == chess.PAWN:
        value = Values.PAWN.value
        value += getLocationValue(pieceSymbol, adder.pawn, col, row)
    elif pieceType == chess.BISHOP:
        value = Values.BISHOP.value
        value += getLocationValue(pieceSymbol, adder.bishop, col, row)
    elif pieceType == chess.KNIGHT:
        value = Values.KNIGHT.value
        value += getLocationValue(pieceSymbol, adder.knight, col, row)
    elif pieceType == chess.ROOK:
        value = Values.ROOK.value
        value += getLocationValue(pieceSymbol, adder.rook, col, row)
    elif pieceType == chess.QUEEN:
        value = Values.QUEEN.value
        value += getLocationValue(pieceSymbol, adder.queen, col, row)
    elif pieceType == chess.KING:
        value = Values.KING.value
        value += getLocationValue(pieceSymbol, adder.king, col, row)
    return value if pieceSymbol.isupper() else -value


def getLocationValue(pieceSymbol, table, col, row):
    if pieceSymbol.isupper():
        invertedRow = 7 - row
        return table[invertedRow][col]
    else:
        return table[row][col]




