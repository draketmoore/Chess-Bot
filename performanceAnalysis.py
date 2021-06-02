from myChess import MyChess
from searchAgents import minimaxAgent, alphaBetaPruningAgent, quietSearch, nullMoveAlphaBetaAgent
from evaluation import evaluate, add_eval
from random import randint
from timeit import timeit
from numpy import average, std, var, amin, amax, median
import sys


def run_agent(agent, eval_func, depth, move_count=None):
    chess_state = MyChess()
    chess_bot = agent(chess_state, eval_func)

    if move_count is None:
        move_count = randint(0, 20)

    # Performs move_count random moves.
    ii = 0
    while ii < move_count:
        moves = list(chess_state.get_board().legal_moves)
        random_move = str(moves[randint(0, len(moves) - 1)])
        chess_state.execute_move(random_move)
        if chess_state.is_game_over():
            chess_state.get_board().pop()
            continue
        ii += 1

    move = chess_bot.get_action(chess_state, depth)
    chess_state.execute_move(move)

# Change these parameters to adjust testing metrics
MAX_DEPTH = 3
# Add values to this list if you want to test a customized set of depths (for example, [1, 2, 5, 10, 100])
CUSTOM_DEPTHS = []
EVAL_FUNC = add_eval
AGENT = quietSearch
# the number of moves to run before running the agent (these moves are chosen randomly)
# number of turns = number of moves / 2. If set to None, will select a random number from 0 to 20 for each repetition.
MOVE_COUNT = None
REPETITIONS = 100

max_depth_arr = CUSTOM_DEPTHS if CUSTOM_DEPTHS else list(range(1, MAX_DEPTH + 1))

print("Testing agent \"{}\" with evaluation function \"{}\", at n = {}...\n"
      .format(AGENT.__name__, EVAL_FUNC.__name__, REPETITIONS))

for depth in max_depth_arr:
    runtimes = []

    for _ in range(0, REPETITIONS):
        runtimes.append(timeit('run_agent(AGENT, EVAL_FUNC, depth, MOVE_COUNT)',
                               'from __main__ import run_agent, AGENT, EVAL_FUNC, depth, MOVE_COUNT', number=1))

    avg = average(runtimes) * 1000
    stdev = std(runtimes) * 1000
    variance = var(runtimes) * (1000 ** 2)
    min = amin(runtimes) * 1000
    med = median(runtimes) * 1000
    max = amax(runtimes) * 1000

    print("Depth = {}\nAverage: {}\nStDev: {}\nVar: {}\nMin: {}\nMedian: {}\nMax: {}\n"
          .format(depth, avg, stdev, variance, min, med, max))


