import pygame
from pygame.locals import *
import pygame_gui

from lib.Loader import Loader
from lib.UserDatabase import UserDatabase  
from lib.Leaderboard import Leaderboard  
from lib.Config import WINDOW_SIZE

class MenuPart(object):
    def __init__(self):
        # Initialize the menu screen
        self.loader = Loader()  # Resource loader
        self.back_color = (50, 50, 50)  # Background color
        self.ui_manager = pygame_gui.UIManager(WINDOW_SIZE)  # UI manager for handling events

        # Load fonts for rendering text
        self.fnt_black = self.loader.load_font_black(28)  
        self.fnt_medium = self.loader.load_font_medium(14)  

        # Create UI buttons
        self.exit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((WINDOW_SIZE[0] - 130, 10), (120, 40)),  
            text='Exit',
            manager=self.ui_manager
        )

        # Define the area for displaying puzzle motives
        self.motive_width = 300  
        self.motive_height = 250  
        self.motive_r = pygame.Rect(780 - self.motive_width - 50, 225, self.motive_width, self.motive_height)  

        # Render the "Select motive" text
        self.txt = self.fnt_black.render("Select motive:", True, (255, 255, 255))
        self.txtr = self.txt.get_rect()
        self.txtr.center = (self.motive_r.centerx, self.motive_r.top - 40)  

        # Create navigation buttons for selecting motives
        self.left_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.motive_r.left - 60, self.motive_r.centery - 15), (50, 30)),
            text='<',
            manager=self.ui_manager
        )
        self.right_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.motive_r.right + 10, self.motive_r.centery - 15), (50, 30)),
            text='>',
            manager=self.ui_manager
        )
        self.select_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                (self.motive_r.centerx - 50, self.motive_r.bottom + 20),  
                (100, 30)  
            ),
            text='Select',
            manager=self.ui_manager
        )
        
        # Initialize the user database and leaderboard
        self.db = UserDatabase()
        self.user_name = self.db.get_last_user() or "Guest"  # Get the last user or default to "Guest"
        self.leaderboard = Leaderboard(self.db)  # Leaderboard for displaying top scores

        # Create input field for entering a username
        self.name_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(
                (20 + (300 - 160) // 2, 130 + 60 + len(self.leaderboard.entries) * 40 + 40),  
                (160, 30)
            ),
            manager=self.ui_manager
        )
        self.name_input.set_text_length_limit(15)  # Limit the username length
        self.name_input.set_text("")  

        # Create buttons for saving and selecting profiles
        self.save_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((20 + (300 - 110) // 2, 130 + 60 + len(self.leaderboard.entries) * 40 + 40 + 30 + 20), (110, 30)),  
            text='Save Profile',
            manager=self.ui_manager
        )
        self.select_profile_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((20 + (300 - 110) // 2, 130 + 60 + len(self.leaderboard.entries) * 40 + 40 + 30 + 20 + 30 + 20), (110, 30)),  
            text='Select Profile',
            manager=self.ui_manager
        )

        self.next_part = 0  # Indicator for transitioning to the next game state
        self.error_message = ""  # Error message for invalid inputs

        # Load and prepare puzzle motives
        self._make_motives()
        self.motive_idx = 0  # Index of the currently selected motive

    def fix_text(self, txt):
        # Format the motive filename into a readable title
        return " ".join(txt.split(".")[0].split("_"))

    def _make_motives(self):
        # Load and scale all available puzzle motives
        l = self.loader.list_motives()
        self.motives = []
        for f in l:
            try:
                i = self.loader.load_motive(f)
                i = pygame.transform.smoothscale(i, (self.motive_width, self.motive_height))
                self.motives.append((i, f, self.fnt_medium.render(self.fix_text(f), True, (255, 255, 255))))
            except:
                pass

    def event(self, event):
        # Handle user input and UI events
        self.ui_manager.process_events(event)

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.exit_button:
                    self.next_part = -1  # Exit the menu
                elif event.ui_element == self.left_button:
                    # Navigate to the previous motive
                    self.motive_idx -= 1
                    if self.motive_idx < 0:
                        self.motive_idx = len(self.motives) - 1
                elif event.ui_element == self.right_button:
                    # Navigate to the next motive
                    self.motive_idx += 1
                    if self.motive_idx == len(self.motives):
                        self.motive_idx = 0
                elif event.ui_element == self.select_button:
                    # Select the current motive and validate the username
                    name = self.name_input.get_text().strip()
                    if not name:  
                        name = self.db.get_last_user() or "Guest"  
                    if self.db.user_exists(name):
                        self.user_name = name
                        self.error_message = ""  
                        self.next_part = 1  # Proceed to the next part
                    else:
                        self.db.add_user(name)
                        self.user_name = name
                        self.error_message = ""  
                        self.next_part = 1  
                elif event.ui_element == self.save_button:
                    # Save a new username
                    name = self.name_input.get_text().strip()
                    if not name:
                        self.error_message = "Error: Name cannot be empty!"
                    elif self.db.user_exists(name):
                        self.error_message = f"Error: User '{name}' already exists!"
                    else:
                        self.db.add_user(name)
                        self.user_name = name
                        self.error_message = ""  
                elif event.ui_element == self.select_profile_button:
                    # Select an existing profile
                    name = self.name_input.get_text().strip()
                    if not name:
                        self.error_message = "Error: Name cannot be empty!"
                    elif not self.db.user_exists(name):
                        self.error_message = f"Error: User '{name}' does not exist!"
                    else:
                        self.user_name = name
                        self.error_message = ""  

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                self.next_part = -1  # Exit the menu

    def get_motive(self):
        # Return the filename of the currently selected motive
        return self.motives[self.motive_idx][1]

    def update(self, screen):
        # Update the menu screen and render its components
        self.leaderboard.refresh()  # Refresh the leaderboard
        screen.fill(self.back_color)  # Fill the background

        if not len(self.motives):
            print("Error: No motives found.")
            return -1

        # Define the leaderboard area
        leaderboard_rect = pygame.Rect(15, 130, 300, 60 + len(self.leaderboard.entries) * 40)

        # Update the positions of input fields and buttons
        self.name_input.set_relative_position(
            (leaderboard_rect.centerx - self.name_input.rect.width // 2, leaderboard_rect.bottom + 40)
        )
        self.save_button.set_relative_position(
            (leaderboard_rect.centerx - self.save_button.rect.width // 2, leaderboard_rect.bottom + 40 + 40 + 20)
        )
        self.select_profile_button.set_relative_position(
            (leaderboard_rect.centerx - self.select_profile_button.rect.width // 2, leaderboard_rect.bottom + 40 + 40 + 20 + 30 + 20)
        )

        # Render the selected motive
        screen.blit(self.motives[self.motive_idx][0], self.motive_r.topleft)

        # Render the "Select motive" text
        pygame.draw.rect(screen, (0, 0, 0), self.txtr.inflate(10, 10))
        screen.blit(self.txt, self.txtr.topleft)

        # Render the greeting message
        greeting = self.fnt_black.render(f"Hello, {self.user_name}!", True, (255, 255, 255))
        greeting_rect = greeting.get_rect(topleft=(20, 130 - 40 - 20))
        pygame.draw.rect(screen, (0, 0, 0), greeting_rect.inflate(10, 10))
        screen.blit(greeting, greeting_rect.topleft)

        # Render the leaderboard
        self.leaderboard.draw(screen, self.fnt_medium, leaderboard_rect.x, leaderboard_rect.y)

        # Render the title of the selected motive
        t = self.motives[self.motive_idx][2]
        tr = t.get_rect()
        tr.center = (self.motive_r.centerx, self.select_button.rect.bottom + 30)
        pygame.draw.rect(screen, (0, 0, 0), tr.inflate(10, 10))
        screen.blit(t, tr.topleft)

        # Render any error messages
        if self.error_message:
            error_text = self.fnt_medium.render(self.error_message, True, (255, 0, 0))
            error_rect = error_text.get_rect(center=(WINDOW_SIZE[0] // 2, 30))
            pygame.draw.rect(screen, (0, 0, 0), error_rect.inflate(10, 10))
            screen.blit(error_text, error_rect.topleft)

        # Update and render the UI
        self.ui_manager.update(1 / 30)
        self.ui_manager.draw_ui(screen)

        return self.next_part  # Return the next game state