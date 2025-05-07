import pygame
from pygame.locals import *
import pygame_gui

from lib.Loader import Loader
from lib.Puzzle import PuzzleFactory    
from lib.Config import WINDOW_SIZE

class LoadPart(object):
    def __init__(self, filename, user_name="Guest"):
        # Initialize the loading screen for cutting puzzle pieces
        self.ui_manager = pygame_gui.UIManager(WINDOW_SIZE)  # UI manager for handling events
        self.loader = Loader()  # Resource loader
        self.back_color = (50, 50, 50)  # Background color

        # Load the puzzle image and related assets
        self.image = self.loader.load_motive(filename).convert_alpha()  # Puzzle image
        mask_image = self.loader.load_image("piece_mask.png").convert_alpha()  # Mask for pieces
        bevel_image = self.loader.load_image("piece_bevel.png").convert_alpha()  # Bevel effect
        shadow_image = self.loader.load_image("piece_shadow.png").convert_alpha()  # Shadow effect
        self.pf = PuzzleFactory(self.image, mask_image, bevel_image, shadow_image)  # Puzzle factory

        self.fnt = self.loader.load_font_black(30)  # Font for rendering text

        # Initialize variables for cutting pieces
        self.pieces = []  # List to store generated puzzle pieces
        self.px = 0  # Current x-coordinate for cutting
        self.py = 0  # Current y-coordinate for cutting

        # Progress bar and its container
        self.bar = pygame.Rect(0, 0, 400, 20)  # Progress bar
        self.bar.center = (400, 470)
        self.box = pygame.Rect(0, 0, 404, 24)  # Progress bar container
        self.box.center = (400, 470)

        self.next_part = 0  # Indicator for transitioning to the next game state
        self.user_name = user_name  # Player's username

    def event(self, event):
        # Handle user input events
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:  # Exit the loading screen
                self.next_part = -1

    def get_next(self):
        # Generate the next puzzle piece
        self.pieces.append(self.pf._make_piece(self.px, self.py))  # Create a piece at (px, py)
        self.px += 1
        if self.px == 10:  # Move to the next row after 10 pieces
            self.px = 0
            self.py += 1
            if self.py == 8:  # Transition to the next state after all pieces are created
                self.next_part = 1

    def update(self, screen):
        # Update the loading screen and render progress
        self.get_next()  # Generate the next piece
        screen.fill(self.back_color)  # Fill the background

        # Render the progress text
        txt = self.fnt.render("Cutting pieces %d/80" % len(self.pieces), True, (255, 255, 255))  
        txtr = txt.get_rect()
        txtr.center = (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 - 50)  # Move text slightly higher
        screen.blit(txt, txtr.topleft)

        # Update and render the progress bar
        self.box.center = (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2)  # Adjust vertical position of the container
        self.bar.w = int(round((len(self.pieces) / 80.0) * (self.box.width - 4)))  # Calculate progress width
        self.bar.topleft = (self.box.left + 2, self.box.top + 2)  # Align progress bar inside the container

        pygame.draw.rect(screen, (255, 255, 255), self.box, 1)  # Draw the progress bar container
        pygame.draw.rect(screen, (255, 255, 255), self.bar)  # Fill the progress bar

        return self.next_part  # Return the next game state