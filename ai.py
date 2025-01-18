import math
import random

class WaterIceAI:
    def __init__(self):
        self.transposition_table = {}

    def face(self):
        return "🐢"

    def get_valid_moves(self, board, stone):
        moves = []
        for y in range(len(board)):
            for x in range(len(board[0])):
                if self.can_place_x_y(board, stone, x, y):
                    moves.append((x, y))
        return moves

    def can_place_x_y(self, board, stone, x, y):
        if board[y][x] != 0:
            return False

        opponent = 3 - stone
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),         (0, 1),
                      (1, -1), (1, 0), (1, 1)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            found_opponent = False

            while 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == opponent:
                nx += dx
                ny += dy
                found_opponent = True

            if found_opponent and 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == stone:
                return True

        return False

    def apply_move(self, board, stone, x, y):
        new_board = [row[:] for row in board]
        new_board[y][x] = stone

        opponent = 3 - stone
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),         (0, 1),
                      (1, -1), (1, 0), (1, 1)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            stones_to_flip = []

            while 0 <= nx < len(new_board[0]) and 0 <= ny < len(new_board) and new_board[ny][nx] == opponent:
                stones_to_flip.append((nx, ny))
                nx += dx
                ny += dy

            if stones_to_flip and 0 <= nx < len(new_board[0]) and 0 <= ny < len(new_board) and new_board[ny][nx] == stone:
                for flip_x, flip_y in stones_to_flip:
                    new_board[flip_y][flip_x] = stone

        return new_board

    def evaluate_board(self, board, stone):
        corner_positions = [(0, 0), (0, 5), (5, 0), (5, 5)]
        bad_positions = [(0, 1), (1, 0), (4, 0), (5, 1), (0, 4), (1, 5), (4, 5), (5, 4)]

        score = 0

        # 基本評価（角や辺を優先）
        for y in range(len(board)):
            for x in range(len(board[0])):
                if board[y][x] == stone:
                    if (x, y) in corner_positions:
                        score += 100
                    elif (x, y) in bad_positions:
                        score -= 50
                    else:
                        score += 1
                elif board[y][x] == 3 - stone:
                    if (x, y) in corner_positions:
                        score -= 100
                    elif (x, y) in bad_positions:
                        score += 50
                    else:
                        score -= 1

        # モビリティ（合法手数の差）
        my_moves = len(self.get_valid_moves(board, stone))
        opponent_moves = len(self.get_valid_moves(board, 3 - stone))
        score += (my_moves - opponent_moves) * 10

        return score

    def move_ordering(self, board, stone):
        # Moves are sorted by their heuristic score to improve pruning efficiency
        valid_moves = self.get_valid_moves(board, stone)
        scored_moves = []
        for move in valid_moves:
            temp_board = self.apply_move(board, stone, move[0], move[1])
            score = self.evaluate_board(temp_board, stone)
            scored_moves.append((score, move))
        scored_moves.sort(reverse=True, key=lambda x: x[0])  # Descending order
        return [move for _, move in scored_moves]

    def negamax(self, board, stone, depth, alpha, beta):
        board_key = tuple(tuple(row) for row in board)  # Immutable board for caching

        # キャッシュを利用する
        if (board_key, stone, depth) in self.transposition_table:
            return self.transposition_table[(board_key, stone, depth)]

        valid_moves = self.get_valid_moves(board, stone)

        # 終端条件
        if depth == 0 or not valid_moves:
            score = self.evaluate_board(board, stone)
            return score, None

        max_eval = -math.inf
        best_move = None

        # Move orderingを使用
        ordered_moves = self.move_ordering(board, stone)

        for x, y in ordered_moves:
            temp_board = self.apply_move(board, stone, x, y)
            eval, _ = self.negamax(temp_board, 3 - stone, depth - 1, -beta, -alpha)
            eval = -eval  # ネガマックス特有の符号反転

            if eval > max_eval:
                max_eval = eval
                best_move = (x, y)

            alpha = max(alpha, eval)
            if alpha >= beta:
                break  # βカット

        # キャッシュに保存
        self.transposition_table[(board_key, stone, depth)] = (max_eval, best_move)
        return max_eval, best_move

    def place(self, board, stone):
        total_stones = sum(row.count(1) + row.count(2) for row in board)

        # 序盤: 深さ8, 中盤: 深さ13, 終盤: 深さ18
        if total_stones < 20:
            depth = 8
        elif total_stones < 50:
            depth = 13
        else:
            depth = 18

        _, best_move = self.negamax(board, stone, depth, -math.inf, math.inf)
        if best_move:
            return best_move
        else:
            return random.choice(self.get_valid_moves(board, stone))
