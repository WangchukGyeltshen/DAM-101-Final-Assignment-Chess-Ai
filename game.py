import os
import pygame
from pygame.locals import *
from piece import Piece
from chess import Chess
from utils import Utils

class Game:
    def __init__(self):
        # screen dimensions
        screen_width = 640
        screen_height = 750
        # flag to know if game menu has been showed
        self.menu_showed = False
        # flag to set game loop
        self.running = True
        # base folder for program resources
        self.resources = "res"
 
        # initialize game window
        pygame.display.init()
        # initialize font for text
        pygame.font.init()

        # create game window
        self.screen = pygame.display.set_mode([screen_width, screen_height])

        # title of window
        window_title = "Chess"
        # set window caption
        pygame.display.set_caption(window_title)

        # get location of game icon
        icon_src = os.path.join(self.resources, "chess_icon.png")
        # load game icon
        icon = pygame.image.load(icon_src)
        # set game icon
        pygame.display.set_icon(icon)
        # update display
        pygame.display.flip()
        # set game clock
        self.clock = pygame.time.Clock()


    def start_game(self):
        """Function containing main game loop""" 
        # chess board offset
        self.board_offset_x = 0
        self.board_offset_y = 50
        self.board_dimensions = (self.board_offset_x, self.board_offset_y)
        
        # get location of chess board image
        board_src = os.path.join(self.resources, "board.png")
        # load the chess board image
        self.board_img = pygame.image.load(board_src).convert()

        # get the width of a chess board square
        square_length = self.board_img.get_rect().width // 8

        # initialize list that stores all places to put chess pieces on the board
        self.board_locations = []

        # calculate coordinates of the each square on the board
        for x in range(0, 8):
            self.board_locations.append([])
            for y in range(0, 8):
                self.board_locations[x].append([self.board_offset_x+(x*square_length), 
                                                self.board_offset_y+(y*square_length)])

        # get location of image containing the chess pieces
        pieces_src = os.path.join(self.resources, "pieces.png")
        # create class object that handles the gameplay logic
        self.chess = Chess(self.screen, pieces_src, self.board_locations, square_length)

        # game loop
        while self.running:
            self.clock.tick(5)
            # poll events
            for event in pygame.event.get():
                # get keys pressed
                key_pressed = pygame.key.get_pressed()
                # check if the game has been closed by the user
                if event.type == pygame.QUIT or key_pressed[K_ESCAPE]:
                    # set flag to break out of the game loop
                    self.running = False
                elif key_pressed[K_SPACE]:
                    self.chess.reset()
            
            winner = self.chess.winner

            if self.menu_showed == False:
                self.menu()
            elif len(winner) > 0:
                self.declare_winner(winner)
            else:
                self.game()
            
            

            # for testing mechanics of the game
            #self.game()
            #self.declare_winner(winner)

            # update display
            pygame.display.flip()
            # update events
            pygame.event.pump()

        # call method to stop pygame
        pygame.quit()
    

    def menu(self):
        """Method to show game menu"""
        # Background color
        bg_color = (255, 255, 255)
        self.screen.fill(bg_color)

        # Colors
        black_color = (0, 0, 0)
        white_color = (255, 255, 255)

        # Create buttons for "Play as White" and "Play as Black"
        white_btn = pygame.Rect(200, 300, 200, 50)
        black_btn = pygame.Rect(200, 400, 200, 50)

        # Draw buttons
        pygame.draw.rect(self.screen, black_color, white_btn)
        pygame.draw.rect(self.screen, black_color, black_btn)

        # Fonts
        big_font = pygame.font.SysFont("comicsansms", 50)
        small_font = pygame.font.SysFont("comicsansms", 20)

        # Texts
        welcome_text = big_font.render("Chess", False, black_color)
        white_btn_label = small_font.render("Play as White", True, white_color)
        black_btn_label = small_font.render("Play as Black", True, white_color)

        # Display texts
        self.screen.blit(welcome_text, 
                         ((self.screen.get_width() - welcome_text.get_width()) // 2, 150))
        self.screen.blit(white_btn_label, 
                         (white_btn.x + (white_btn.width - white_btn_label.get_width()) // 2, 
                          white_btn.y + (white_btn.height - white_btn_label.get_height()) // 2))
        self.screen.blit(black_btn_label, 
                         (black_btn.x + (black_btn.width - black_btn_label.get_width()) // 2, 
                          black_btn.y + (black_btn.height - black_btn_label.get_height()) // 2))

        # Handle input
        util = Utils()
        if util.left_click_event():
            mouse_coords = util.get_mouse_event()

            # Check if "Play as White" button is clicked
            if white_btn.collidepoint(mouse_coords[0], mouse_coords[1]):
                self.chess.player_color = "white"
                self.menu_showed = True

            # Check if "Play as Black" button is clicked
            elif black_btn.collidepoint(mouse_coords[0], mouse_coords[1]):
                self.chess.player_color = "black"
                self.menu_showed = True


    def game(self):
        # background color
        color = (0,0,0)
        # set backgound color
        self.screen.fill(color)
        
        # show the chess board
        self.screen.blit(self.board_img, self.board_dimensions)

        # call self.chess. something
        self.chess.play_turn()
        # draw pieces on the chess board
        self.chess.draw_pieces()


    def declare_winner(self, winner):
        # background color
        bg_color = (255, 255, 255)
        # set background color
        self.screen.fill(bg_color)
        # black color
        black_color = (0, 0, 0)
        # coordinates for play again button
        reset_btn = pygame.Rect(250, 300, 140, 50)
        # show reset button
        pygame.draw.rect(self.screen, black_color, reset_btn)

        # white color
        white_color = (255, 255, 255)
        # create fonts for texts
        big_font = pygame.font.SysFont("comicsansms", 50)
        small_font = pygame.font.SysFont("comicsansms", 20)

        # text to show winner
        text = winner + " wins!" 
        winner_text = big_font.render(text, False, black_color)

        # create text to be shown on the reset button
        reset_label = "Play Again"
        reset_btn_label = small_font.render(reset_label, True, white_color)

        # show winner text
        self.screen.blit(winner_text, 
                      ((self.screen.get_width() - winner_text.get_width()) // 2, 
                      150))
        
        # show text on the reset button
        self.screen.blit(reset_btn_label, 
                      ((reset_btn.x + (reset_btn.width - reset_btn_label.get_width()) // 2, 
                      reset_btn.y + (reset_btn.height - reset_btn_label.get_height()) // 2)))

        # get pressed keys
        key_pressed = pygame.key.get_pressed()
        # 
        util = Utils()

        # check if left mouse button was clicked
        if util.left_click_event():
            # call function to get mouse event
            mouse_coords = util.get_mouse_event()

            # check if reset button was clicked
            if reset_btn.collidepoint(mouse_coords[0], mouse_coords[1]):
                # change button behavior as it is hovered
                pygame.draw.rect(self.screen, white_color, reset_btn, 3)
                
                # change menu flag
                self.menu_showed = False
            # check if enter or return key was pressed
            elif key_pressed[K_RETURN]:
                self.menu_showed = False
            # reset game
            self.chess.reset()
            # clear winner
            self.chess.winner = ""