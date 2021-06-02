import pygame
from myChess import MyChess
from os import path
from threading import Thread
from queue import Queue


# A class for a rudimentary GUI.
# TODO: Find some fun sound files
class chessGUI:

    # Piece Names
    W_PAWN = "P"
    W_BISH = "B"
    W_KGHT = "N"
    W_ROOK = "R"
    W_QUEN = "Q"
    W_KING = "K"
    B_PAWN = "p"
    B_BISH = "b"
    B_KGHT = "n"
    B_ROOK = "r"
    B_QUEE = "q"
    B_KING = "k"
    BACKGD = "background"

    P_MVMT = "piece_mvmt"
    CKMATE = "checkmate"

    # Piece Images
    # TODO: modify load_image calls with os.path.join for absolute paths (to increase compatability)
    GUI_FILES = {
        W_PAWN:"./GUIFiles/Images/WhitePawn.png",
        W_BISH:"./GUIFiles/Images/WhiteBishop.png",
        W_KGHT: "./GUIFiles/Images/WhiteHorsie.png",
        W_ROOK: "./GUIFiles/Images/WhiteCastle.png",
        W_QUEN: "./GUIFiles/Images/WhiteQueen.png",
        W_KING: "./GUIFiles/Images/WhiteKing.png",
        B_PAWN: "./GUIFiles/Images/BlackPawn.png",
        B_BISH: "./GUIFiles/Images/BlackBishop.png",
        B_KGHT: "./GUIFiles/Images/BlackHorsie.png",
        B_ROOK: "./GUIFiles/Images/BlackCastle.png",
        B_QUEE: "./GUIFiles/Images/BlackQueen.png",
        B_KING: "./GUIFiles/Images/BlackKing.png",
        BACKGD: "./GUIFiles/Images/background.png",
        P_MVMT: "./GUIFiles/Sounds/PieceMove.midi",
        CKMATE: "./GUIFiles/Sounds/Checkmate.midi"
    }

    # Image/Sound files to be loaded in once run_game is called
    FILES = {}
    VALID_PIC_EXT = [".jpg", ".jpeg", ".png", ".tif", ".bmp"]
    VALID_SOUND_EXT = [".wav", ".mp3", ".midi"]

    # Colors for the squares on the board
    SQUARE_COL1 = (255, 255, 255, 0)
    SQUARE_COL2 = (0, 65, 155, 1)
    MATED_COL = (255, 0, 0, 1)

    # Board and window dimensions
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 600
    WIDTH = 8
    HEIGHT = 8
    BLOCK_SIZE = WINDOW_WIDTH // 8

    # Frame rate
    FPS = 30

    # chess_state is the initial state of the board; player represents
    # who you are playing as (White is True, Black is False). The player will always be drawn at the bottom
    # of the screen
    def __init__(self, chess_state: MyChess=None, chess_bot=None):

        # If no bot is specified, set up GUI for 2-player chess
        if chess_bot is None:
            self.chess_state = chess_state if chess_state is not None else MyChess()
            # Set to whosever turn is first (so that white is drawn on the bottom)
            self.player = self.chess_state.get_turn()
        else: # Else, set the GUI for 1-player chess against the given bot
            self.chess_state = chess_bot.get_state()
            self.player = chess_bot.get_player()

        self.chess_bot = chess_bot
        self.is_bot_move = False

        # Background and screen will be created once run_game is called
        self.background = None
        self.screen = None
        self.clock = pygame.time.Clock()
        self.clicked_pos = None

    @classmethod
    # Requires you to specify a bot to play against
    def onePlayerChessGUI(cls, bot):
        return cls(chess_bot=bot)

    @classmethod
    def twoPlayerChessGUI(cls):
        return cls()

    # Runs the game
    def run_game(self):
        pygame.init()
        self.screen = pygame.display.set_mode((chessGUI.WINDOW_WIDTH, chessGUI.WINDOW_HEIGHT))
        self.load_files()
        self.draw_initial_board()

        # Set up event queue by blocking all events, and then allowing only mouse up/down/motion,
        # and quit (doing this is probably optional)
        # Pieces will be moved by clicking on them once, and then clicking again at the destination square
        allowed_events = [pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN, pygame.QUIT]
        pygame.event.set_blocked(None)
        pygame.event.set_allowed(allowed_events)

        # If this is 1-player chess, and the player is black (the bot is white), let the bot make the first move:
        if self.chess_bot is not None and self.chess_bot.get_player() == False:
            bot_move = self.chess_bot.make_move()
            pygame.time.wait(1500)
            self.update_GUI_with_move(bot_move)
            pygame.display.update()

        # Threads are used here since asking the bot to make a move takes a long time, and waiting to draw the move
        # on the GUI causes lag and an incorrect image.
        bot_move_q = Queue()
        bot_move_thread = None

        while True:

            # Check if it's the bot's turn. If so, let the bot execute its move, and update the GUI.
            if self.is_bot_move and (self.chess_bot is not None) and (not self.chess_state.is_game_over()):
                # bot_move = self.chess_bot.make_move()
                if bot_move_thread is None:
                    bot_move_thread = Thread(target=self.get_bot_move, args=(bot_move_q,))
                    bot_move_thread.start()

                # On future frames, check if the thread is still running. If so, continue to the next iteration. If
                # not, retrieve the move that the bot performed, and update the GUI.
                elif not bot_move_thread.is_alive():
                    bot_move_thread.join()
                    bot_move = bot_move_q.get()
                    self.update_GUI_with_move(bot_move)
                    self.play_sound(chessGUI.P_MVMT)
                    self.is_bot_move = False
                    bot_move_thread = None
                    pygame.display.update()

                # Skip event processing in for loop below, so the bot and GUI can update on this tick
                pygame.event.pump()
                continue

            # Process events (mouse clicks) in the queue
            for event in pygame.event.get():
                # If this is 1-player chess, ask the bot to make a move (on the frame after the player makes their move)
                # (provided that the game isn't over), and then update the GUI
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # No piece has currently been selected
                    if self.clicked_pos is None:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        file, rank = self.screen_pos_to_file_rank((mouse_x, mouse_y))
                        str_pos = "{}{}".format(file, rank)

                        piece, color = self.chess_state.get_piece_at_pos(str_pos)

                        # If the player made a valid click (for either 1-player or 2-player chess, depending on
                        # whether or not self.chess_bot exists
                        if self.chess_bot is None:
                            if piece is not None and color == self.chess_state.get_turn():
                                self.clicked_pos = str_pos
                        else:
                            if piece is not None and color == self.player == self.chess_state.get_turn():
                                self.clicked_pos = str_pos

                    else:  # Else, attempt to place the selected piece on the new square
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        file, rank = self.screen_pos_to_file_rank((mouse_x, mouse_y))
                        str_pos = "{}{}".format(file, rank)

                        move = self.clicked_pos + str_pos

                        # Execute the move and update the GUI if it's legal
                        if self.chess_state.is_move_legal(move):
                            self.chess_state.execute_move(move)

                            # Update GUI with player move
                            self.update_GUI_with_move(move)
                            self.play_sound(chessGUI.P_MVMT)

                            # Set self.is_bot_move to True so that the bot moves on the next frame
                            self.is_bot_move = True

                            # # If this is 1-player chess, ask the bot to make a move
                            # # (provided that the game isn't over), and then update the GUI
                            # if self.chess_bot is not None and not self.chess_state.is_game_over():
                            #     bot_move = self.chess_bot.make_move()
                            #     self.update_GUI_with_move(bot_move)
                            #     self.play_sound(chessGUI.P_MVMT)

                        # Clear the clicked position
                        self.clicked_pos = None
                        # print(self.chess_state)

                elif event.type == pygame.QUIT:
                    pygame.quit()
                    return

            self.clock.tick(chessGUI.FPS)

    # Load all image/sound files in (will reload files each time this method is called)
    def load_files(self):
        for (name, pth) in chessGUI.GUI_FILES.items():
            if not path.exists(pth):
                # If no file exists, set it to none
                self.FILES[name] = None
            else:
                extension = path.splitext(pth)[1]
                file = None

                # If the file is a picture...
                if extension in chessGUI.VALID_PIC_EXT:

                    # convert_alpha is called here to make the background transparent
                    image = pygame.image.load(pth).convert_alpha()

                    # If the given image is a piece, scale it accordingly.
                    # If the image is not a piece (i.e. the background), do nothing.
                    if name == chessGUI.BACKGD:
                        file = image
                    else:
                        file = pygame.transform.scale(image, (chessGUI.BLOCK_SIZE, chessGUI.BLOCK_SIZE))
                elif extension in chessGUI.VALID_SOUND_EXT:
                    file = pygame.mixer.Sound(pth)

                self.FILES[name] = file

    # Draws the initial board based on self.chess_state
    def draw_initial_board(self):
        self.draw_grid()
        self.draw_pieces()
        pygame.display.update()

    # Draws the initial blank grid of the board. If a background.png file exists in the Images directory,
    # it will use that instead of generating a new one.
    def draw_grid(self):

        # Attempt to retrieve the background from a file
        if self.FILES[chessGUI.BACKGD] is not None:
            self.background = self.FILES[chessGUI.BACKGD]
            # Add the background to the screen
            self.screen.blit(self.background, (0, 0))
            return

        # Generate a new background (since no file exists)
        self.background = pygame.display.set_mode((chessGUI.WINDOW_WIDTH, chessGUI.WINDOW_HEIGHT))

        for yy in range(chessGUI.HEIGHT):
            for xx in range(chessGUI.WIDTH):
                rect = pygame.Rect(xx * chessGUI.BLOCK_SIZE, yy * chessGUI.BLOCK_SIZE,
                                   chessGUI.BLOCK_SIZE, chessGUI.BLOCK_SIZE)

                # If the player is white, use the standard color scheme. If the player is black,
                # invert the color scheme.
                if self.player:
                    color = chessGUI.SQUARE_COL1 if xx % 2 == yy % 2 else chessGUI.SQUARE_COL2
                else:
                    color = chessGUI.SQUARE_COL2 if xx % 2 == yy % 2 else chessGUI.SQUARE_COL1

                pygame.draw.rect(self.background, color, rect)

        pygame.image.save_extended(self.background, chessGUI.GUI_FILES[chessGUI.BACKGD])
        self.FILES[chessGUI.BACKGD] = pygame.image.load(chessGUI.GUI_FILES[chessGUI.BACKGD])
        self.background = self.FILES[chessGUI.BACKGD]

        # Add the background to the screen
        self.screen.blit(self.background, (0, 0))

    # Adds pieces onto the board based on self.chess_state
    def draw_pieces(self):
        piece_list = self.chess_state.get_piece_list()
        for (piece, coords) in piece_list:
            xx, yy = coords
            yy = yy if self.player else (chessGUI.HEIGHT - 1) - yy

            image = self.FILES[piece]
            self.screen.blit(image, (xx * chessGUI.BLOCK_SIZE, yy * chessGUI.BLOCK_SIZE))

    # Executes the move on the GUI, assuming that the move is valid.
    # Note: Assumes that the gamestate has already been changed, and does NOT change the gamestate further
    def update_GUI_with_move(self, move):

        init_pos = move[0]+ move[1]
        new_pos = move[2] + move[3]
        blitted_rects = []

        # Erase the piece on the initial square
        blitted_rects.append(self.blit_square(self.background, init_pos, False))

        # Erase any pieces on the new square (if there is one), and then draw the piece on the new square\
        image = self.FILES[self.chess_state.get_piece_at_pos(new_pos)[0]]
        blitted_rects.append(self.blit_square(self.background, new_pos, False))
        blitted_rects.append(self.blit_square(image, new_pos))

        castle_rook_move = self.get_castle_rook_move(move)
        if self.get_castle_rook_move(move) is not None:
            self.update_GUI_with_move(castle_rook_move)

        winner = self.chess_state.get_winner()
        # If the game is a win or loss (i.e. not a draw), mark the checkmated king
        if winner is not None:
            piece_list = self.chess_state.get_piece_list()

            mated_king_sym = chessGUI.B_KING if winner else chessGUI.W_KING
            king_x = None
            king_y = None
            for (piece, coord) in piece_list:
                if piece == mated_king_sym:
                    king_x = coord[0]
                    king_y = coord[1]
                    break

            # Add 97 to convert the int to an ASCII character
            file = chr(king_x + 97)
            rank = chessGUI.HEIGHT - king_y
            king_pos = (file, rank)
            king_screen_x, king_screen_y = self.file_rank_to_screen_pos(king_pos)
            king_screen_square = (king_screen_x, king_screen_y, chessGUI.BLOCK_SIZE, chessGUI.BLOCK_SIZE)
            mated_king_img = self.FILES[mated_king_sym]
            pygame.draw.rect(self.screen, chessGUI.MATED_COL, king_screen_square)
            blitted_rects.append(king_screen_square)
            blitted_rects.append(self.blit_square(mated_king_img, king_pos))

            # Unfortunately, this is the only place where we check for checkmate currently, so we will play the sound
            # cue here.
            self.play_sound(chessGUI.CKMATE)
        pygame.display.update(blitted_rects)

    # Return the rook move if the given move is a castle move. If the given move is not a castle, returns None.
    # For example, if white castles king side, the given move would be "e1g1", and the returned rook move would
    # be "h1f1"
    def get_castle_rook_move(self, move):
        init_pos = move[0] + move[1]
        new_pos = move[2] + move[3]
        init_file, new_file = init_pos[0], new_pos[0]
        init_col, new_col = ord(init_file) - 97, ord(new_file) - 97
        init_rank, new_rank = init_pos[1], new_pos[1]

        piece = self.chess_state.get_piece_at_pos(new_pos)[0]
        hor_move_dist = abs(init_col - new_col)

        # To check whether the given move is a castling move, we first check if the moved piece was a king, and if the
        # king has moved more than one file away.
        if (piece == self.W_KING or piece == self.B_KING) and hor_move_dist > 1:
            # Check if we castled king-side (in which case the king moves over 2 squares)
            if new_file == "g":
                return "h{}f{}".format(new_rank, new_rank)
            # Check if we castled queen-side (in which case the king moves over 3 squares)
            elif new_file == "c":
                return "a{}d{}".format(new_rank, new_rank)
        else:
            return None

    # Tells the bot to make it's move, and stores the move inside of return_val, which should be a queue.Queue
    def get_bot_move(self, return_q: Queue):
        return_q.put(self.chess_bot.make_move())

    # Given an pos in the form of (file, rank), converts it to screen coordinates.
    def file_rank_to_screen_pos(self, pos):
        xx, yy, = pos
        # ord(xx) - 97 converts the ASCII character (since files are written as letters from a-h) to a number
        screen_x = (ord(xx) - 97) * chessGUI.BLOCK_SIZE

        if self.chess_bot is not None and not self.chess_bot.get_player():
            screen_y = (int(yy) - 1) * chessGUI.BLOCK_SIZE
        else:
            screen_y = chessGUI.WINDOW_HEIGHT - int(yy) * chessGUI.BLOCK_SIZE

        return (screen_x, screen_y)

    # Given a set of screen coordinates, converts it to a (file, rank) format
    def screen_pos_to_file_rank(self, screen_pos):
        screen_x, screen_y = screen_pos
        # Add 97 to coordinate to convert the int to an ASCII character (from a-h lowercase)
        file = chr(screen_x // chessGUI.BLOCK_SIZE + 97)

        if self.chess_bot is not None and not self.chess_bot.get_player():
            rank = screen_y // chessGUI.BLOCK_SIZE + 1
        else:
            rank = chessGUI.HEIGHT - screen_y // chessGUI.BLOCK_SIZE

        return (file, rank)

    # Given an image and a tuple (file, rank), this method will blit (draw on) the square at that (file, rank)
    # with the given image.
    # By default, this method will attempt to blit the entire given image, but if whole_img is set to False, it will
    # select only a portion of the image determined by pos (the selected portion of the image will be the same
    # selected portion of self.screen).
    # Returns the square (as a pygame.Rect) that was blitted.
    def blit_square(self, img, pos, whole_img=True):
        screen_x, screen_y = self.file_rank_to_screen_pos(pos)
        square = (screen_x, screen_y, chessGUI.BLOCK_SIZE, chessGUI.BLOCK_SIZE)
        img_rect = None if whole_img else square
        self.screen.blit(img, square, img_rect)
        return square

    # Plays the given sound (if it exists)
    def play_sound(self, sound):
        sound_file = self.FILES[sound]
        if sound_file is not None:
            pygame.mixer.Sound.play(self.FILES[sound])
