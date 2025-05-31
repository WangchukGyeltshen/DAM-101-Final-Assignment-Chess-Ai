'''
    Add or remove bots :
    
    SET_WHITE_AS_BOT = False
    SET_BLACK_AS_BOT = True
'''

# Responsible for handling user input and displaying the current Gamestate object

import sys, asyncio
import pygame as p
from engine import GameState, Move
from chessAi import ChessAI, findBestMove, findRandomMoves
from multiprocessing import Process, Queue

# Initialize the mixer
p.mixer.init()
# Load sound files
move_sound = p.mixer.Sound("sounds/move-sound.mp3")
capture_sound = p.mixer.Sound("sounds/capture.mp3")
promote_sound = p.mixer.Sound("sounds/promote.mp3")

BOARD_WIDTH = BOARD_HEIGHT = 512
EVAL_BAR_WIDTH = 40
MOVE_LOG_PANEL_HEIGHT = 80
WINDOW_WIDTH = BOARD_WIDTH + EVAL_BAR_WIDTH
WINDOW_HEIGHT = BOARD_HEIGHT + MOVE_LOG_PANEL_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

'''

     ADD BOTS         
    IF IN GameState() , 
    
    playerWantsToPlayAsBlack = True
    SET_BLACK_AS_BOT SHOULD BE = FALSE

'''

SET_WHITE_AS_BOT = False
SET_BLACK_AS_BOT = True

# Define colors

# 1 Green

LIGHT_SQUARE_COLOR = (237, 238, 209)
DARK_SQUARE_COLOR = (119, 153, 82)
MOVE_HIGHLIGHT_COLOR = (84, 115, 161)
POSSIBLE_MOVE_COLOR = (255, 255, 51)

EVAL_BAR_BG = (220, 220, 220)
EVAL_BAR_WHITE = (240, 240, 255)
EVAL_BAR_BLACK = (100, 120, 180)

# 2 Brown

'''
LIGHT_SQUARE_COLOR = (240, 217, 181)
DARK_SQUARE_COLOR = (181, 136, 99)
MOVE_HIGHLIGHT_COLOR = (84, 115, 161)
POSSIBLE_MOVE_COLOR = (255, 255, 51)
'''

# 3 Gray

'''
LIGHT_SQUARE_COLOR = (220,220,220)
DARK_SQUARE_COLOR = (170,170,170)
MOVE_HIGHLIGHT_COLOR = (84, 115, 161)
POSSIBLE_MOVE_COLOR = (164,184,196)
'''


def loadImages():
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK',
              'bp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'wp']
    for piece in pieces:
        image_path = "images1/" + piece + ".png"
        original_image = p.image.load(image_path)
        # p.transform.smoothscale is bit slower than p.transform.scale, using this to reduce pixelation and better visual quality for scaling images to larger sizes
        IMAGES[piece] = p.transform.smoothscale(
            original_image, (SQ_SIZE, SQ_SIZE))


def pawnPromotionPopup(screen, gs):
    font = p.font.SysFont("Times New Roman", 30, False, False)
    text = font.render("Choose promotion:", True, p.Color("black"))

    # Create buttons for promotion choices with images
    button_width, button_height = 100, 100
    buttons = [
        p.Rect(100, 200, button_width, button_height),
        p.Rect(200, 200, button_width, button_height),
        p.Rect(300, 200, button_width, button_height),
        p.Rect(400, 200, button_width, button_height)
    ]

    if gs.whiteToMove:
        button_images = [
            p.transform.smoothscale(p.image.load(
                "images1/bQ.png"), (100, 100)),
            p.transform.smoothscale(p.image.load(
                "images1/bR.png"), (100, 100)),
            p.transform.smoothscale(p.image.load(
                "images1/bB.png"), (100, 100)),
            p.transform.smoothscale(p.image.load("images1/bN.png"), (100, 100))
        ]
    else:
        button_images = [
            p.transform.smoothscale(p.image.load(
                "images1/wQ.png"), (100, 100)),
            p.transform.smoothscale(p.image.load(
                "images1/wR.png"), (100, 100)),
            p.transform.smoothscale(p.image.load(
                "images1/wB.png"), (100, 100)),
            p.transform.smoothscale(p.image.load("images1/wN.png"), (100, 100))
        ]

    while True:
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                mouse_pos = e.pos
                for i, button in enumerate(buttons):
                    if button.collidepoint(mouse_pos):
                        if i == 0:
                            return "Q"  # Return the index of the selected piece
                        elif i == 1:
                            return "R"
                        elif i == 2:
                            return "B"
                        else:
                            return "N"

        screen.fill(p.Color(LIGHT_SQUARE_COLOR))
        screen.blit(text, (110, 150))

        for i, button in enumerate(buttons):
            p.draw.rect(screen, p.Color("white"), button)
            screen.blit(button_images[i], button.topleft)

        p.display.flip()


'''
moveLocationWhite = ()
movedPieceWhite = ""
moveLocationBlack = ()
movedPieceBlack = ""

moveWhiteLog = []
moveBlackLog = []
'''


def main():
    # initialize py game
    p.init()
    screen = p.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color(LIGHT_SQUARE_COLOR))
    moveLogFont = p.font.SysFont("Arial", 16, False, False)
    # Creating gamestate object calling our constructor
    gs = GameState()
    if (gs.playerWantsToPlayAsBlack):
        gs.board = gs.board1
    # if a user makes a move we can ckeck if its in the list of valid moves
    validMoves = gs.getValidMoves()
    moveMade = False  # if user makes a valid moves and the gamestate changes then we should generate new set of valid move
    animate = False  # flag var for when we should animate a move
    loadImages()
    running = True
    squareSelected = ()  # keep tracks of last click
    # clicking to own piece and location where to move[(6,6),(4,4)]
    playerClicks = []
    gameOver = False  # gameover if checkmate or stalemate
    playerWhiteHuman = not SET_WHITE_AS_BOT
    playerBlackHuman = not SET_BLACK_AS_BOT
    AIThinking = False  # True if ai is thinking
    moveFinderProcess = None
    moveUndone = False
    pieceCaptured = False
    positionHistory = ""
    previousPos = ""
    countMovesForDraw = 0
    COUNT_DRAW = 0
    ai = ChessAI()
    while running:
        humanTurn = (gs.whiteToMove and playerWhiteHuman) or (
            not gs.whiteToMove and playerBlackHuman)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Mouse Handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:  # allow mouse handling only if its not game over
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    # if user clicked on same square twice or user click outside board
                    if squareSelected == (row, col) or col >= 8:
                        squareSelected = ()  # deselect
                        playerClicks = []  # clear player clicks
                    else:
                        squareSelected = (row, col)
                        # append player both clicks (place and destination)
                        playerClicks.append(squareSelected)
                    # after second click (at destination)
                    if len(playerClicks) == 2 and humanTurn:
                        # user generated a move
                        move = Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            # check if the move is in the validMoves
                            if move == validMoves[i]:
                                # Check if a piece is captured at the destination square
                                # print(gs.board[validMoves[i].endRow][validMoves[i].endCol])
                                if gs.board[validMoves[i].endRow][validMoves[i].endCol] != '--':
                                    pieceCaptured = True
                                gs.makeMove(validMoves[i])
                                if (move.isPawnPromotion):
                                    # Show pawn promotion popup and get the selected piece
                                    promotion_choice = pawnPromotionPopup(
                                        screen, gs)
                                    # Set the promoted piece on the board
                                    gs.board[move.endRow][move.endCol] = move.pieceMoved[0] + \
                                        promotion_choice
                                    promote_sound.play()
                                    pieceCaptured = False
                                # add sound for human move
                                if (pieceCaptured or move.isEnpassantMove):
                                    # Play capture sound
                                    capture_sound.play()
                                    # print("capture sound")
                                elif not move.isPawnPromotion:
                                    # Play move sound
                                    move_sound.play()
                                    # print("move sound")
                                pieceCaptured = False
                                moveMade = True
                                animate = True
                                squareSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [squareSelected]

            # Key Handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when z is pressed
                    gs.undoMove()
                    # when user undo move valid move change, here we could use [ validMoves = gs.getValidMoves() ] which would update the current validMoves after undo
                    moveMade = True
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()  # terminate the ai thinking if we undo
                        AIThinking = False
                    moveUndone = True
                if e.key == p.K_r:  # reset board when 'r' is pressed
                    gs = GameState()
                    validMoves = gs.getValidMoves()
                    squareSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()  # terminate the ai thinking if we undo
                        AIThinking = False
                    moveUndone = True

        # AI move finder
        if not gameOver and not humanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                returnQueue = Queue()  # keep track of data, to pass data between threads
                moveFinderProcess = Process(target=findBestMove, args=(
                    gs, validMoves, returnQueue))  # when processing start we call these process
                # call findBestMove(gs, validMoves, returnQueue) #rest of the code could still work even if the ai is thinking
                moveFinderProcess.start()
                # AIMove = findBestMove(gs, validMoves)
                # gs.makeMove(AIMove)
            if not moveFinderProcess.is_alive():
                AIMove = returnQueue.get()  # return from returnQueue
                if AIMove is None:
                    AIMove = findRandomMoves(validMoves)

                if gs.board[AIMove.endRow][AIMove.endCol] != '--':
                    pieceCaptured = True

                gs.makeMove(AIMove)

                if AIMove.isPawnPromotion:
                    # Show pawn promotion popup and get the selected piece
                    promotion_choice = pawnPromotionPopup(screen, gs)
                    # Set the promoted piece on the board
                    gs.board[AIMove.endRow][AIMove.endCol] = AIMove.pieceMoved[0] + \
                        promotion_choice
                    promote_sound.play()
                    pieceCaptured = False

                # add sound for human move
                if (pieceCaptured or AIMove.isEnpassantMove):
                    # Play capture sound
                    capture_sound.play()
                    # print("capture sound")
                elif not AIMove.isPawnPromotion:
                    # Play move sound
                    move_sound.play()
                    # print("move sound")
                pieceCaptured = False
                AIThinking = False
                moveMade = True
                animate = True
                squareSelected = ()
                playerClicks = []

        if moveMade:
            if countMovesForDraw == 0 or countMovesForDraw == 1 or countMovesForDraw == 2 or countMovesForDraw == 3:
                countMovesForDraw += 1
            if countMovesForDraw == 4:
                positionHistory += gs.getBoardString()
                if previousPos == positionHistory:
                    COUNT_DRAW += 1
                    positionHistory = ""
                    countMovesForDraw = 0
                else:
                    previousPos = positionHistory
                    positionHistory = ""
                    countMovesForDraw = 0
                    COUNT_DRAW = 0
            # Call animateMove to animate the move
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            # genetare new set of valid move if valid move is made
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False

        eval_score = ai._evaluate(gs)
        drawGameState(screen, gs, validMoves, squareSelected, moveLogFont, eval_score)

        if COUNT_DRAW == 1:
            gameOver = True
            text = 'Draw due to repetition'
            drawEndGameText(screen, text)
        if gs.stalemate:
            gameOver = True
            text = 'Stalemate'
            drawEndGameText(screen, text)
        elif gs.checkmate:
            gameOver = True
            text = 'Black wins by checkmate' if gs.whiteToMove else 'White wins by checkmate'
            drawEndGameText(screen, text)

        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs, validMoves, squareSelected, moveLogFont, eval_score):
    drawBoardBorder(screen)
    drawSquare(screen)
    highlightLastMove(screen, gs)
    highlightSquares(screen, gs, validMoves, squareSelected)
    drawPieces(screen, gs.board)
    drawEvalBar(screen, eval_score)
    drawMoveLog(screen, gs, moveLogFont)


def drawSquare(screen):
    global colors
    colors = [p.Color(LIGHT_SQUARE_COLOR), p.Color(DARK_SQUARE_COLOR)]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            p.draw.rect(screen, color, p.Rect(
                col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def highlightSquares(screen, gs, validMoves, squareSelected):
    if squareSelected != ():  # make sure there is a square to select
        row, col = squareSelected
        # Only highlight if the selection is on the board
        if 0 <= row < 8 and 0 <= col < 8:
            # make sure they click their own piece
            if gs.board[row][col][0] == ('w' if gs.whiteToMove else 'b'):
                # highlight selected piece square
                s = p.Surface((SQ_SIZE, SQ_SIZE))
                s.set_alpha(100)
                s.fill(p.Color(MOVE_HIGHLIGHT_COLOR))
                screen.blit(s, (col*SQ_SIZE, row*SQ_SIZE))
                # highlighting valid squares
                s.fill(p.Color(POSSIBLE_MOVE_COLOR))
                for move in validMoves:
                    if move.startRow == row and move.startCol == col:
                        screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))


def drawPieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(
                    col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(0, BOARD_HEIGHT, BOARD_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, (220, 220, 230), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []

    for i in range(0, len(moveLog), 2):
        moveString = f"{i//2 + 1}. {moveLog[i]}"
        if i+1 < len(moveLog):
            moveString += f" {moveLog[i+1]}"
        moveTexts.append(moveString)

    padding = 16
    textY = BOARD_HEIGHT + padding
    textX = padding
    for text in moveTexts[-6:]:
        textObject = font.render(text, True, (40, 40, 40))
        screen.blit(textObject, (textX, textY))
        textY += textObject.get_height() + 8


# animating a move
def animateMove(move, screen, board, clock):
    global colors
    # change in row, col
    deltaRow = move.endRow - move.startRow
    deltaCol = move.endCol - move.startCol
    framesPerSquare = 5  # frames move one square
    # how many frame the animation will take
    frameCount = (abs(deltaRow) + abs(deltaCol)) * framesPerSquare
    # generate all the coordinates
    for frame in range(frameCount + 1):
        # how much does the row and col move by
        row, col = ((move.startRow + deltaRow*frame/frameCount, move.startCol +
                    deltaCol*frame/frameCount))  # how far through the animation
        # for each frame draw the moved piece
        drawSquare(screen)
        drawPieces(screen, board)

        # erase the piece moved from its ending squares
        color = colors[(move.endRow + move.endCol) %
                       2]  # get color of the square
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow *
                           SQ_SIZE, SQ_SIZE, SQ_SIZE)  # pygame rectangle
        p.draw.rect(screen, color, endSquare)

        # draw the captured piece back
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                enPassantRow = move.endRow + \
                    1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol*SQ_SIZE, enPassantRow *
                                   SQ_SIZE, SQ_SIZE, SQ_SIZE)  # pygame rectangle
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(
            col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

        p.display.flip()
        clock.tick(240)


def drawEndGameText(screen, text):
    # create font object with type and size of font you want
    font = p.font.SysFont("Times New Roman", 30, False, False)
    # use the above font and render text (0 ? antialias)
    textObject = font.render(text, True, p.Color('black'))

    # Get the width and height of the textObject
    text_width = textObject.get_width()
    text_height = textObject.get_height()

    # Calculate the position to center the text on the screen
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(
        BOARD_WIDTH/2 - text_width/2, BOARD_HEIGHT/2 - text_height/2)

    # Blit the textObject onto the screen at the calculated position
    screen.blit(textObject, textLocation)

    # Create a second rendering of the text with a slight offset for a shadow effect
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(1, 1))


def drawEvalBar(screen, eval_score):
    bar_x = BOARD_WIDTH
    bar_y = 0
    bar_width = EVAL_BAR_WIDTH
    bar_height = BOARD_HEIGHT

    # Gradient background
    for i in range(bar_height):
        color = [
            int(EVAL_BAR_WHITE[j] + (EVAL_BAR_BLACK[j] - EVAL_BAR_WHITE[j]) * i / bar_height)
            for j in range(3)
        ]
        p.draw.line(screen, color, (bar_x, bar_y + i), (bar_x + bar_width, bar_y + i))

    # Clamp eval_score for display
    eval_clamped = max(min(eval_score, 5), -5)
    white_height = int((0.5 - eval_clamped / 10) * bar_height)
    white_height = max(0, min(bar_height, white_height))

    # Draw split line
    p.draw.line(screen, (255, 255, 255), (bar_x, bar_y + white_height), (bar_x + bar_width, bar_y + white_height), 2)

    # Draw border
    p.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, bar_width, bar_height), 2)

    # Draw eval number
    font = p.font.SysFont("Arial", 18, True, False)
    eval_text = f"{eval_score:+.2f}"
    text_surf = font.render(eval_text, True, (0, 0, 0))
    text_rect = text_surf.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
    screen.blit(text_surf, text_rect)


def drawBoardBorder(screen):
    border_rect = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT)
    p.draw.rect(screen, (60, 60, 60), border_rect, border_radius=16, width=6)


def highlightLastMove(screen, gs):
    if gs.moveLog:
        lastMove = gs.moveLog[-1]
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(120)
        s.fill((255, 255, 0))  # yellow highlight
        screen.blit(s, (lastMove.startCol * SQ_SIZE, lastMove.startRow * SQ_SIZE))
        screen.blit(s, (lastMove.endCol * SQ_SIZE, lastMove.endRow * SQ_SIZE))


# if we import main then main function wont run it will run only while running this file
if __name__ == "__main__":
    main()