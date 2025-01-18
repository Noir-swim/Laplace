import math
import random

class WaterIceAI:
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

    def evaluate_board(self, board, stone, total_stones):
        corner_positions = [(0, 0), (0, 5), (5, 0), (5, 5)]
        bad_positions = [(0, 1), (1, 0), (4, 0), (5, 1), (0, 4), (1, 5), (4, 5), (5, 4)]
        edge_positions = [
            (0, 2), (0, 3), (2, 0), (3, 0),
            (5, 2), (5, 3), (2, 5), (3, 5),
        ]

        score = 0

        for y in range(len(board)):
            for x in range(len(board[0])):
                if board[y][x] == stone:
                    if (x, y) in corner_positions:
                        score += 150
                    elif (x, y) in bad_positions:
                        score -= 100
                    elif (x, y) in edge_positions:
                        score += 25
                    else:
                        score += 5
                elif board[y][x] == 3 - stone:
                    if (x, y) in corner_positions:
                        score -= 150
                    elif (x, y) in bad_positions:
                        score += 100
                    elif (x, y) in edge_positions:
                        score -= 25
                    else:
                        score -= 5

        # モビリティ
        my_moves = len(self.get_valid_moves(board, stone))
        opponent_moves = len(self.get_valid_moves(board, 3 - stone))
        score += (my_moves - opponent_moves) * 10

        # 序盤は中央重視、終盤は石数重視
        if total_stones < 20:
            score += sum(1 for y in range(2, 4) for x in range(2, 4) if board[y][x] == stone) * 50
        elif total_stones > 40:
            my_count = sum(row.count(stone) for row in board)
            opponent_count = sum(row.count(3 - stone) for row in board)
            score += (my_count - opponent_count) * 10

        return score

    def negamax(self, board, stone, depth, alpha, beta, total_stones):
        valid_moves = self.get_valid_moves(board, stone)

        if depth == 0 or not valid_moves:
            return self.evaluate_board(board, stone, total_stones), None

        max_eval = -math.inf
        best_move = None

        for x, y in sorted(valid_moves, key=lambda m: self.evaluate_board(self.apply_move(board, stone, *m), stone, total_stones), reverse=True):
            temp_board = self.apply_move(board, stone, x, y)
            eval, _ = self.negamax(temp_board, 3 - stone, depth - 1, -beta, -alpha, total_stones + 1)
            eval = -eval

            if eval > max_eval:
                max_eval = eval
                best_move = (x, y)

            alpha = max(alpha, eval)
            if alpha >= beta:
                break  # βカット

        return max_eval, best_move

    def place(self, board, stone):
        total_stones = sum(row.count(1) + row.count(2) for row in board)

        if total_stones < 20:
            depth = 5  # 序盤
        elif total_stones < 50:
            depth = 7  # 中盤
        else:
            depth = 9  # 終盤

        _, best_move = self.negamax(board, stone, depth, -math.inf, math.inf, total_stones)
        return best_move or random.choice(self.get_valid_moves(board, stone))
