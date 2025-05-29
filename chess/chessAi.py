import random
from collections import namedtuple

CHECKMATE = 1000
STALEMATE = 0
MAX_DEPTH = 3

PIECE_VALUES = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}
TranspositionEntry = namedtuple("TranspositionEntry", ["depth", "score"])


class EvaluationTables:
    piece_scores = {
        "N": [[1, 1, 1, 1, 1, 1, 1, 1],
              [1, 2, 2, 2, 2, 2, 2, 1],
              [1, 2, 3, 3, 3, 3, 2, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 2, 3, 3, 3, 3, 2, 1],
              [1, 2, 2, 2, 2, 2, 2, 1],
              [1, 1, 1, 1, 1, 1, 1, 1]],

        "B": [[4, 3, 2, 1, 1, 2, 3, 4],
              [3, 4, 3, 2, 2, 3, 4, 3],
              [2, 3, 4, 3, 3, 4, 3, 2],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [2, 3, 4, 3, 3, 4, 3, 2],
              [3, 4, 3, 2, 2, 3, 4, 3],
              [4, 3, 2, 1, 1, 2, 3, 4]],

        "Q": [[1, 1, 1, 3, 1, 1, 1, 1],
              [1, 2, 3, 3, 3, 1, 1, 1],
              [1, 4, 3, 3, 3, 4, 2, 1],
              [1, 2, 3, 3, 3, 2, 2, 1],
              [1, 2, 3, 3, 3, 2, 2, 1],
              [1, 4, 3, 3, 3, 4, 2, 1],
              [1, 1, 2, 3, 3, 1, 1, 1],
              [1, 1, 1, 3, 1, 1, 1, 1]],

        "R": [[4, 3, 4, 4, 4, 4, 3, 4],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [1, 1, 2, 3, 3, 2, 1, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 1, 2, 2, 2, 2, 1, 1],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [4, 3, 2, 1, 1, 2, 3, 4]],

        "wp": [[8, 8, 8, 8, 8, 8, 8, 8],
               [8, 8, 8, 8, 8, 8, 8, 8],
               [5, 6, 6, 7, 7, 6, 6, 5],
               [2, 3, 3, 5, 5, 3, 3, 2],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 1, 2, 3, 3, 2, 1, 1],
               [1, 1, 1, 0, 0, 1, 1, 1],
               [0, 0, 0, 0, 0, 0, 0, 0]],

        "bp": [[0, 0, 0, 0, 0, 0, 0, 0],
               [1, 1, 1, 0, 0, 1, 1, 1],
               [1, 1, 2, 3, 3, 2, 1, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [2, 3, 3, 5, 5, 3, 3, 2],
               [5, 6, 6, 7, 7, 6, 6, 5],
               [8, 8, 8, 8, 8, 8, 8, 8],
               [8, 8, 8, 8, 8, 8, 8, 8]]
    }


class ChessAI:
    def __init__(self):
        self.transposition_table = {}
        self.best_move = None
        self.best_eval = 0  # Store the evaluation of the best move

    def choose_move(self, gs, valid_moves, returnQueue):
        self.transposition_table.clear()
        self.best_move = None
        self.best_eval = 0
        is_white_bot = 1 if gs.whiteToMove else -1
        random.shuffle(valid_moves)

        for depth in range(1, MAX_DEPTH + 1):
            print(f"Depth {depth} search")
            eval_score = self._negamax(gs, valid_moves, depth, -CHECKMATE, CHECKMATE, is_white_bot)
            if self.best_move is not None:
                self.best_eval = eval_score  # Store the evaluation at the root

        print(f"Best move: {self.best_move}, Evaluation: {self.best_eval:.2f}")
        for move in valid_moves:
            gs.makeMove(move)
            eval_score = -self._negamax(gs, gs.getValidMoves(), MAX_DEPTH - 1, -CHECKMATE, CHECKMATE, -is_white_bot)
            gs.undoMove()
            print(f"Move: {move}, Eval: {eval_score:.2f}")
            if eval_score > self.best_eval or self.best_move is None:
                self.best_eval = eval_score
                self.best_move = move
        returnQueue.put(self.best_move)

    def _negamax(self, gs, moves, depth, alpha, beta, color):
        board_key = (gs.getBoardString(), depth, color)
        if board_key in self.transposition_table:
            return self.transposition_table[board_key].score

        if depth == 0:
            return self._quiescence(gs, alpha, beta, color)

        max_score = -CHECKMATE
        for move in self._prioritize_moves(moves):
            gs.makeMove(move)
            opponent_moves = gs.getValidMoves()
            score = -self._negamax(gs, opponent_moves, depth - 1, -beta, -alpha, -color)
            gs.undoMove()

            if score > max_score:
                max_score = score
                if depth == MAX_DEPTH:
                    self.best_move = move

            alpha = max(alpha, max_score)
            if alpha >= beta:
                break

        self.transposition_table[board_key] = TranspositionEntry(depth, max_score)
        return max_score

    def _quiescence(self, gs, alpha, beta, color, qdepth=2):
        if qdepth == 0:
            return color * self._evaluate(gs)

        stand_pat = color * self._evaluate(gs)
        if stand_pat >= beta:
            return beta
        alpha = max(alpha, stand_pat)

        # Only consider captures, promotions, and checks
        for move in gs.getValidMoves():
            if getattr(move, 'isCapture', False) or getattr(move, 'isPawnPromotion', False) or getattr(move, 'isCheck', False):
                gs.makeMove(move)
                score = -self._quiescence(gs, -beta, -alpha, -color, qdepth - 1)
                gs.undoMove()
                if score >= beta:
                    return beta
                alpha = max(alpha, score)

        return alpha

    def _evaluate(self, gs):
        """
        Positive score: White is better.
        Negative score: Black is better.
        """
        if gs.checkmate:
            return -CHECKMATE if gs.whiteToMove else CHECKMATE
        elif gs.stalemate:
            return STALEMATE

        total_score = 0
        white_pawns, black_pawns = 0, 0
        for r in range(8):
            for c in range(8):
                piece = gs.board[r][c]
                if piece != "--":
                    color, ptype = piece[0], piece[1]
                    base_score = PIECE_VALUES[ptype]
                    pos_score = 0
                    key = f"{color}{ptype}" if ptype == "p" else ptype
                    if key in EvaluationTables.piece_scores:
                        pos_score = EvaluationTables.piece_scores[key][r][c]
                    score = base_score + pos_score * 0.1
                    if color == 'w':
                        total_score += score
                        if ptype == 'p':
                            white_pawns += 1
                    else:
                        total_score -= score
                        if ptype == 'p':
                            black_pawns += 1

        # Mobility
        my_moves = len(gs.getValidMoves())
        gs.whiteToMove = not gs.whiteToMove
        opp_moves = len(gs.getValidMoves())
        gs.whiteToMove = not gs.whiteToMove
        total_score += 0.1 * (my_moves - opp_moves)

        # Pawn structure: penalize doubled pawns
        total_score -= 0.2 * (self._count_doubled_pawns(gs, 'w'))
        total_score += 0.2 * (self._count_doubled_pawns(gs, 'b'))

        # King safety: penalize if king is not castled and queens are on board
        if self._king_not_castled(gs, 'w'):
            total_score -= 0.2
        if self._king_not_castled(gs, 'b'):
            total_score += 0.2

        # Endgame bonus: king and pawn vs king
        if self._is_simple_endgame(gs):
            total_score += 0.5 if self._has_pawn(gs, 'w') else -0.5

        return total_score

    def _is_simple_endgame(self, gs):
        # Only kings and pawns left
        pieces = [piece for row in gs.board for piece in row if piece != "--"]
        return all(p[1] in ['K', 'p'] for p in pieces)

    def _has_pawn(self, gs, color):
        return any(piece == color + 'p' for row in gs.board for piece in row)

    def _count_doubled_pawns(self, gs, color):
        doubled = 0
        for col in range(8):
            pawns = 0
            for row in range(8):
                piece = gs.board[row][col]
                if piece == (color + 'p'):
                    pawns += 1
            if pawns > 1:
                doubled += (pawns - 1)
        return doubled

    def _king_not_castled(self, gs, color):
        if color == 'w':
            king_row, king_col = gs.whiteKinglocation
            return king_row != 7 or king_col not in [6, 2, 4]
        else:
            king_row, king_col = gs.blackKinglocation
            return king_row != 0 or king_col not in [6, 2, 4]

    def _prioritize_moves(self, moves):
        def move_value(move):
            val = 0
            if getattr(move, 'isCapture', False):
                victim = PIECE_VALUES.get(move.pieceCaptured[1], 0)
                attacker = PIECE_VALUES.get(move.pieceMoved[1], 0)
                val += 10 * victim - attacker
            if getattr(move, 'isPawnPromotion', False):
                val += 5
            # Prioritize checks
            if hasattr(move, 'isCheck') and move.isCheck:
                val += 3
            return -val
        return sorted(moves, key=move_value)


def random_move(valid_moves):
    return random.choice(valid_moves)

def findRandomMoves(validMoves):
    return random_move(validMoves)

def findBestMove(gs, validMoves, returnQueue):
    board_str = gs.getBoardString()
    if board_str in OPENING_BOOK:
        # Convert the book move to your Move object
        move_uci = OPENING_BOOK[board_str]
        for move in validMoves:
            if move.getChessNotation() == move_uci:
                returnQueue.put(move)
                return
    ai = ChessAI()
    ai.choose_move(gs, validMoves, returnQueue)

OPENING_BOOK = {
    # Initial position: play e2e4
    "bRbNbBbQbKbBbNbRbpbpbpbpbpbpbpbp------------------------"
    "------------------------wpwpwpwpwpwpwpwpwRwNwBwQwKwBwNwR": "e2e4",
    # After 1.e4 e5: play Nf3
    "bRbNbBbQbKbBbNbRbpbpbpbp--bpbp------------------------"
    "----wpwpwpwpwpwpwpwpwRwNwBwQwKwBwNwR": "g1f3",
    # After 1.d4: play d2d4
    "bRbNbBbQbKbBbNbRbpbpbpbpbpbpbpbp------------------------"
    "----------------wpwpwpwpwpwpwpwpwRwNwBwQwKwBwNwR": "d2d4",
    # After 1.d4 d5: play c4
    "bRbNbBbQbKbBbNbRbpbpbpbp--bpbp------------------------"
    "----wpwpwpwpwpwpwpwpwRwNwBwQwKwBwNwR": "c2c4",
    # After 1.e4 c5: play Nf3 (Sicilian)
    "bRbNbBbQbKbBbNbRbpbp--bpbpbpbp------------------------"
    "----wpwpwpwpwpwpwpwpwRwNwBwQwKwBwNwR": "g1f3",
    # After 1.e4 e6: play d4 (French)
    "bRbNbBbQbKbBbNbRbpbpbpbp--bpbp------------------------"
    "----wpwpwpwpwpwpwpwpwRwNwBwQwKwBwNwR": "d2d4",
    # After 1.e4 c6: play d4 (Caro-Kann)
    "bRbNbBbQbKbBbNbRbpbp--bpbpbpbp------------------------"
    "----wpwpwpwpwpwpwpwpwRwNwBwQwKwBwNwR": "d2d4",
    # After 1.d4 Nf6: play c4
    "bRbNbBbQbKbBbNbRbpbpbpbpbpbpbpbp------------------------"
    "----------------wpwpwpwpwpwpwpwpwRwNwBwQwKwBwNwR": "c2c4",
    # After 1. e4 (White plays e2e4), Black plays e7e5
    "bRbNbBbQbKbBbNbRbpbpbpbpbpbpbpbp------------------------"
    "----wpwpwpwpwpwpwpwpwRwNwBwQwKwBwNwR": "e7e5",

    # After 1. d4 (White plays d2d4), Black plays d7d5
    "bRbNbBbQbKbBbNbRbpbpbpbpbpbpbpbp----------------wpwpwpwpwpwpwpwpwRwNwBwQwKwBwNwR": "d7d5",

    # After 1. c4 (White plays c2c4), Black plays e7e5 (English Opening, reversed Sicilian)
    "bRbNbBbQbKbBbNbRbpbpbpbpbpbpbpbp------------------------"
    "--wpwpwpwpwpwpwpwpwRwNwBwQwKwBwNwR": "e7e5",

    # After 1. Nf3 (White plays g1f3), Black plays d7d5
    "bRbNbBbQbKbBbNbRbpbpbpbpbpbpbpbp------------------------"
    "----------------wpwpwpwpwpwpwpwpwRwNwBwQwKwBwNwR": "d7d5",

    # After 1. e4 c5 (White plays e2e4, Black plays c7c5, Sicilian Defense)
    "bRbNbBbQbKbBbNbRbpbpbpbp--bpbp------------------------"
    "----wpwpwpwpwpwpwpwpwRwNwBwQwKwBwNwR": "c7c5",

    # After 1. e4 e6 (French Defense)
    "bRbNbBbQbKbBbNbRbpbpbpbp--bpbp------------------------"
    "----wpwpwpwpwpwpwpwpwRwNwBwQwKwBwNwR": "e7e6",

    # After 1. e4 c6 (Caro-Kann Defense)
    "bRbNbBbQbKbBbNbRbpbp--bpbpbpbp------------------------"
    "----wpwpwpwpwpwpwpwpwRwNwBwQwKwBwNwR": "c7c6",

    # After 1. d4 Nf6 (Indian Defense)
    "bRbNbBbQbKbBbNbRbpbpbpbpbpbpbpbp------------------------"
    "----------------wpwpwpwpwpwpwpwpwRwNwBwQwKwBwNwR": "g8f6",

    # Add more positions as needed for deeper opening knowledge
}
