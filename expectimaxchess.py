from searchAgents import *
from multiplier import Multiplier
from myChess import myChess
import evaluation 

from bisect import bisect_left

class expectimaxAgent(multiSearchAgent):

	def get_action(self, chess_state: MyChess, max_depth=None):

		if max_depth is None: 
			max_depth = self.max_depth

		return self.expectimax(0, max_depth, chess_state, True)[0]


	def max_action(self, chess_state, target_depth):
		values = {}
		
		for move in chess_state.str_legal_moves():
			next_board = chess_state.try_move(move)

			values[move] = self.expectimax(curr_depth + 1, target_depth, MyChess(next_board), False)[1]

		maxi = max(values.values())
		for k, v in values.items(): 
			if v == maxi: 
				return k, v
		return None

	def take_closest(self, val_list, num):
		pos = bisect_left(val_list, num)
		if pos == 0:
			return val_list[0]
		if pos == len(val_list):
			return val_list[-1]
		before = val_list[pos-1]
		after = val_list[pos]
		if after - num < num - before:
			return after
		else:
			return before

	def bad_min_action(self, chess_state, target_depth):
		values = {}
		
		for move in chess_state.str_legal_moves():
			next_board = chess_state.try_move(move)

			values[move] = self.expectimax(curr_depth + 1, target_depth, MyChess(next_board), True)[1]

		avg = sum(values.values()) / len(values.values())
		closest = self.take_closest(self, list(values.values()), avg)
		for k, v in values.items(): 
			if v == closest:
				return k, v
		return None


	def expectimax(self, curr_depth, target_depth, chess_state, max_turn):
		if curr_depth == target_depth or chess_state.is_win(max_turn) \
				or chess_state.is_lose(max_turn) or chess_state.is_draw():
			return None, self.eval_func(chess_state)

		if max_turn:
			return best_move, best_val = self.max_action(chess_state)

		else:
			return best_move, best_val = self.bad_min_action(chess_state)





