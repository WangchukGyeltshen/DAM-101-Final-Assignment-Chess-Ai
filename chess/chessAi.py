import random
pieceScore = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}

knightScores = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]

bishopScores = [[4, 3, 2, 1, 1, 2, 3, 4],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [4, 3, 2, 1, 1, 2, 3, 4]]

queenScores = [[1, 1, 1, 3, 1, 1, 1, 1],
               [1, 2, 3, 3, 3, 1, 1, 1],
               [1, 4, 3, 3, 3, 4, 2, 1],
               [1, 2, 3, 3, 3, 2, 2, 1],
               [1, 2, 3, 3, 3, 2, 2, 1],
               [1, 4, 3, 3, 3, 4, 2, 1],
               [1, 1, 2, 3, 3, 1, 1, 1],
               [1, 1, 1, 3, 1, 1, 1, 1]]

rookScores = [[4, 3, 4, 4, 4, 4, 3, 4],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [1, 1, 2, 3, 3, 2, 1, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 1, 2, 2, 2, 2, 1, 1],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [4, 3, 2, 1, 1, 2, 3, 4]]

whitePawnScores = [[8, 8, 8, 8, 8, 8, 8, 8],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [0, 0, 0, 0, 0, 0, 0, 0]]

blackPawnScores = [[0, 0, 0, 0, 0, 0, 0, 0],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [8, 8, 8, 8, 8, 8, 8, 8]]


piecePositionScores = {"N": knightScores, "B": bishopScores, "Q": queenScores,
                       "R": rookScores, "wp": whitePawnScores, "bp": blackPawnScores}


CHECKMATE = 1000
STALEMATE = 0
DEPTH = 4
SET_WHITE_AS_BOT = -1

transposition_table = {}


def findRandomMoves(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


def findBestMove(gs, validMoves, returnQueue):
    global nextMove, whitePawnScores, blackPawnScores, transposition_table
    nextMove = None
    random.shuffle(validMoves)
    transposition_table = {}

    if gs.playerWantsToPlayAsBlack:
        whitePawnScores, blackPawnScores = blackPawnScores, whitePawnScores

    SET_WHITE_AS_BOT = 1 if gs.whiteToMove else -1

    bestMoveSoFar = None
    for currentDepth in range(1, DEPTH + 1):
        print(f"Searching to depth {currentDepth}...")
        findMoveNegaMaxAlphaBeta(gs, validMoves, currentDepth, -
                                 CHECKMATE, CHECKMATE, SET_WHITE_AS_BOT)
        if nextMove is not None:
            bestMoveSoFar = nextMove
    returnQueue.put(bestMoveSoFar)


# with alpha beta pruning
'''
alpha is keeping track of maximum so far
beta is keeping track of minimum so far
'''


def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    # --- Transposition Table Lookup ---
    boardString = gs.getBoardString()
    tt_key = (boardString, depth, turnMultiplier)
    if tt_key in transposition_table:
        return transposition_table[tt_key]
    # --- End Transposition Table Lookup ---

    if depth == 0:
        return quiescence(gs, alpha, beta, turnMultiplier)

    maxScore = -CHECKMATE
    for move in orderMoves(validMoves):
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()  # opponent validmoves
        score = -findMoveNegaMaxAlphaBeta(
            gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
                print(move, score)
        gs.undoMove()
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break

    # --- Store in Transposition Table ---
    transposition_table[tt_key] = maxScore
    # --- End Store ---

    return maxScore


'''
Positive score is good for white
Negative score is good for black
'''


def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            gs.checkmate = False
            return -CHECKMATE  # black wins
        else:
            gs.checkmate = False
            return CHECKMATE  # white wins
    elif gs.stalemate:
        return STALEMATE

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                piecePositionScore = 0
                # score positionally based on piece type
                if square[1] != "K":
                    # return score of the piece at that position
                    if square[1] == "p":
                        piecePositionScore = piecePositionScores[square][row][col]
                    else:
                        piecePositionScore = piecePositionScores[square[1]][row][col]
                if SET_WHITE_AS_BOT:
                    if square[0] == 'w':
                        score += pieceScore[square[1]] + \
                            piecePositionScore * .1
                    elif square[0] == 'b':
                        score -= pieceScore[square[1]] + \
                            piecePositionScore * .1
                else:
                    if square[0] == 'w':
                        score -= pieceScore[square[1]] + \
                            piecePositionScore * .1
                    elif square[0] == 'b':
                        score += pieceScore[square[1]] + \
                            piecePositionScore * .1

    return score

def quiescence(gs, alpha, beta, turnMultiplier, qdepth=8):
    if qdepth == 0:
        return turnMultiplier * scoreBoard(gs)
    stand_pat = turnMultiplier * scoreBoard(gs)
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    # Only consider capture moves for quiescence
    captureMoves = [move for move in gs.getValidMoves() if move.isCapture]
    for move in captureMoves:
        gs.makeMove(move)
        score = -quiescence(gs, -beta, -alpha, -turnMultiplier, qdepth-1)
        gs.undoMove()
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
    return alpha

def orderMoves(moves):
    # Prioritize captures and promotions
    def moveScore(move):
        score = 0
        if hasattr(move, 'isCapture') and move.isCapture:
            # MVV-LVA: Most Valuable Victim - Least Valuable Attacker
            victim = move.pieceCaptured[1] if move.pieceCaptured != '--' else None
            attacker = move.pieceMoved[1]
            if victim and victim in pieceScore and attacker in pieceScore:
                score += 10 * pieceScore[victim] - pieceScore[attacker]
            else:
                score += 10  # generic capture
        if hasattr(move, 'isPawnPromotion') and move.isPawnPromotion:
            score += 5
        # You can add more heuristics (e.g., checks) here
        return -score  # negative for descending sort
    return sorted(moves, key=moveScore)
