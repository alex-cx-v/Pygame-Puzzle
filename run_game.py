import pygame
from pygame.locals import *

from lib.GamePart import GamePart
from lib.MenuPart import MenuPart
from lib.LoadPart import LoadPart
from lib.Config import WINDOW_SIZE

class PygamePuzzle(object):
    def __init__(self):
        # Initialize the game window
        self.screen = pygame.display.set_mode((WINDOW_SIZE), 1)
        pygame.display.set_caption("Pygame Puzzle")  # Set the window title

    def main_loop(self):
        # Main game loop
        clock = pygame.time.Clock()  # Clock to control the frame rate

        cur_part = MenuPart()  # Start with the menu screen

        while 1:
            clock.tick(30)  # Limit the frame rate to 30 FPS

            # Handle events
            for event in pygame.event.get():
                if event.type == QUIT:  # Exit the game if the window is closed
                    return
                cur_part.event(event)  # Pass the event to the current part of the game

            # Update the current part and get the next state
            next = cur_part.update(self.screen)

            if next == 1:  # Transition to the next part
                if isinstance(cur_part, MenuPart):
                    # Transition from the menu to the loading screen
                    user_name = cur_part.user_name
                    cur_part = LoadPart(cur_part.get_motive(), user_name)
                elif isinstance(cur_part, LoadPart):
                    # Transition from the loading screen to the game
                    cur_part = GamePart(cur_part.pieces, cur_part.image, cur_part.user_name)
            elif next == -1:  # Exit or return to the menu
                if isinstance(cur_part, MenuPart):
                    return  # Exit the game
                else:
                    cur_part = MenuPart()  # Return to the menu

            pygame.display.flip()  # Update the display

def main():
    # Initialize pygame and start the game
    pygame.init()

    g = PygamePuzzle()  # Create the game instance
    g.main_loop()  # Start the main loop

if __name__ == '__main__':
    main()  # Run the game if this file is executed directly