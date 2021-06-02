# Authors: Drake Moore, John Lam, Nathan Cheng
# chessbot.py


import chess
import chess.pgn


class MyChess():
    # maps values to each of the pieces
    mapped = {
        'P': 1,  # White Pawn
        'p': -1,  # Black Pawn
        'N': 3,  # White Knight
        'n': -3,  # Black Knight
        'B': 3,  # White Bishop
        'b': -3,  # Black Bishop
        'R': 5,  # White Rook
        'r': -5,  # Black Rook
        'Q': 9,  # White Queen
        'q': -9,  # Black Queen
        'K': 100,  # White King
        'k': -100  # Black King
    }

    def __init__(self, board=None):
        if board is None:
            board = chess.Board()

        self.board = board
        self.pgnGame = chess.pgn.Game()
        self.pgn = self.pgnGame


    # gets the current board
    def get_board(self):
        return self.board

    # gets the current turn (white is True, black is False)
    def get_turn(self):
        return self.board.turn

    # returns if the current gamestate is a win for the given player
    def is_win(self, turn):
        winner = self.get_winner()
        return winner == turn if winner else False

    # returns if the current gamestate is a win for the given player
    def is_lose(self, turn):
        winner = self.get_winner()
        return winner != turn if winner else False

    # returns if the current gamestate is a win for the given player
    def is_draw(self):
        outcome = self.board.outcome()
        return outcome.winner is None if outcome else False

    # Gets the winning color, or None if there is no winner (i.e. the game is a draw or not yet finished)
    def get_winner(self):
        outcome = self.board.outcome()
        return outcome.winner if outcome else None

    # returns if the game is over (if the game is a win, loss, or draw)
    def is_game_over(self):
        return self.board.is_game_over()

    # returns if the current player is in check
    def in_check(self):
        return self.board.is_check()

    # gets the pgn of the whole game
    def get_pgn(self):
        return self.pgnGame

    # returns an integer representation of the board based on piece values
    @staticmethod
    def convert_to_int(board):
        epd_string = board.epd()
        list_int = []
        for i in epd_string:
            if i == " ":
                return list_int
            elif i != "/":
                if i in MyChess.mapped:
                    list_int.append(MyChess.mapped[i])
                else:
                    for counter in range(0, int(i)):
                        list_int.append(0)

    # returns a list of all the pieces on the board in the form of (piece, (x, y))
    # piece is a string in {'P', 'B', 'N', 'R', 'Q', 'K', 'p', 'b', 'n', 'r', 'q', 'k'}. Uppercase letters represent
    # white pieces, and lowercase black pieces.
    # (x, y) are the of the piece's location (top-left is (0, 0)).
    def get_piece_list(self):
        epd_string = self.board.epd()

        piece_list = []
        cur_x, cur_y = 0, 0
        for char in epd_string:
            if char == " ":
                return piece_list
            elif char != "/":
                if char.isnumeric():
                    cur_x += int(char) - 1
                else:
                    piece_list.append((char, (cur_x, cur_y)))

                if cur_x == 7:
                    cur_x = 0
                    cur_y += 1
                else:
                    cur_x += 1

    # Gets the piece at the given pos (in the format of 'filerank' as a string, such as 'a1'),
    # or None if none exists
    def get_piece_at_pos(self, pos):
        square = chess.parse_square(pos)
        piece_type = self.board.piece_type_at(square)
        color = self.board.color_at(square)

        if piece_type:
            piece_symbol = chess.piece_symbol(piece_type).upper() if color else chess.piece_symbol(piece_type)
        else:
            piece_symbol = None

        return piece_symbol, color

    @staticmethod
    def piece_to_int(piece):
        return MyChess.mapped[str(piece)]

    # executes the given move on the current board, and returns it (note that this modififes the current gamestate)
    # TODO: it may make sense to modify this method and try_move to return an instance of myChess instead of a board
    def execute_move(self, move: str):
        if not self.is_move_legal(move):
            raise ValueError("{} is not a legal move".format(move))

        self.board.push(chess.Move.from_uci(move))
        self.pgn = self.pgn.add_variation(chess.Move.from_uci(move))
        return self.board

    # returns a copy of the current board with the new move, without modifying the current board
    def try_move(self, move: str):

        if not self.is_move_legal(move):
            raise ValueError("{} is not a legal move".format(move))

        new_board = self.board.copy()
        new_board.push(chess.Move.from_uci(move))
        return new_board

    # returns a list of legal moves in string format
    def str_legal_moves(self):
        legal_moves = list(self.board.legal_moves)
        str_legal_moves = list(map(str, legal_moves))
        return str_legal_moves

    # Checks if the given move is legal
    def is_move_legal(self, move):
        return move in self.str_legal_moves()

    def __str__(self):
        return str(self.board)

    def get_num_pieces(self, color):
        num = 0
        for val in self.convert_to_int(self.board):
            if color:
                if val > 2:
                    num += 1
            else:
                if val < -2:
                    num += 1
        return num

