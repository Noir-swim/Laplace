import math
import random

class weareteamphysAI:
    def face(self):
        return "🎓nori"

    def get_valid_moves(self, board, stone):
        valid_moves = []
        for y in range(len(board)):
            for x in range(len(board[0])):
                if self.can_place_x_y(board, stone, x, y):
                    valid_moves.append((x, y))
        return valid_moves

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
        """
        改良された評価関数
        - 角: 高評価
        - 辺: 中評価
        - モビリティ: 高評価
        """
        corner_positions = [(0, 0), (0, 5), (5, 0), (5, 5)]
        edge_positions = [(0, 1), (0, 4), (1, 0), (1, 5),
                          (4, 0), (4, 5), (5, 1), (5, 4)]

        score = 0

        # 盤面評価
        for y in range(len(board)):
            for x in range(len(board[0])):
                if board[y][x] == stone:
                    if (x, y) in corner_positions:
                        score += 100  # 角を確保
                    elif (x, y) in edge_positions:
                        score += 10   # 辺を確保
                    else:
                        score += 1    # その他
                elif board[y][x] == 3 - stone:
                    if (x, y) in corner_positions:
                        score -= 100  # 相手の角
                    elif (x, y) in edge_positions:
                        score -= 10   # 相手の辺
                    else:
                        score -= 1    # その他

        # モビリティ
        my_moves = len(self.get_valid_moves(board, stone))
        opponent_moves = len(self.get_valid_moves(board, 3 - stone))
        score += (my_moves - opponent_moves) * 5

        return score

    def minimax(self, board, stone, depth, maximizing, alpha=-math.inf, beta=math.inf):
        valid_moves = self.get_valid_moves(board, stone)

        if depth == 0 or not valid_moves:
            return self.evaluate_board(board, stone), None

        best_move = None
        if maximizing:
            max_eval = -math.inf
            for x, y in valid_moves:
                temp_board = self.apply_move(board, stone, x, y)
                eval, _ = self.minimax(temp_board, 3 - stone, depth - 1, False, alpha, beta)
                if eval > max_eval:
                    max_eval = eval
                    best_move = (x, y)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # βカット
            return max_eval, best_move
        else:
            min_eval = math.inf
            for x, y in valid_moves:
                temp_board = self.apply_move(board, stone, x, y)
                eval, _ = self.minimax(temp_board, 3 - stone, depth - 1, True, alpha, beta)
                if eval < min_eval:
                    min_eval = eval
                    best_move = (x, y)
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # αカット
            return min_eval, best_move

    def place(self, board, stone):
        total_stones = sum(row.count(BLACK) + row.count(WHITE) for row in board)

        # 序盤: 深さ3, 中盤: 深さ5, 終盤: 深さ7
        if total_stones < 20:
            depth = 3
        elif total_stones < 50:
            depth = 5
        else:
            depth = 7

        _, best_move = self.minimax(board, stone, depth, True)
        if best_move:
            return best_move
        else:
            valid_moves = self.get_valid_moves(board, stone)
            return random.choice(valid_moves) if valid_moves else None
