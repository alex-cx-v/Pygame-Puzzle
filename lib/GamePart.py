import pygame
from pygame.locals import *
import pygame_gui

from lib.Loader import Loader
from lib.PieceStream import PieceStream
from lib.Board import Board
from lib.Puzzle import PuzzlePieceGroup
from lib.ScoreTable import ScoreTable
from random import shuffle, choice, randint
from lib.Config import WINDOW_SIZE

class GamePart(object):
    def __init__(self, pieces, orgimg, user_name="Guest"):
        # Initialize game components and UI elements
        self.loader = Loader()  # Resource loader
        self.back_color = (50, 50, 50)  # Background color
        self.board_color = (40, 40, 40)  # Board area color
        self.stream_color = (40, 40, 40)  # Stream area color

        # UI manager and exit button
        self.ui_manager = pygame_gui.UIManager(WINDOW_SIZE)
        self.exit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((WINDOW_SIZE[0] - 150, 10), (120, 40)),  
            text='Exit',
            manager=self.ui_manager
        )

        # Initialize the board and shuffle puzzle pieces
        self.board = Board(orgimg)
        shuffle(pieces)
        self.stream = PieceStream(pieces, self.board.r.y, self.board.r.height)

        # Floating pieces and game state variables
        self.floating = []  # Pieces currently being moved
        self.selected = None  # Currently selected piece
        self.scrolling = False  # Whether the stream is being scrolled
        self.next_part = 0  # Indicator for the next game state
        self.game_completed = False  # Whether the puzzle is completed

        # Score tracking
        self.score_table = ScoreTable(user_name=user_name)

    def event(self, event):
        # Handle user input and UI events
        self.ui_manager.process_events(event)

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.exit_button:
                    self.next_part = -1  # Exit the game

        if event.type == KEYDOWN:
            # Handle keyboard input for navigation and exit
            if event.key == K_ESCAPE:
                self.next_part = -1
            elif event.key == K_DOWN:
                self.stream.down()
            elif event.key == K_UP:
                self.stream.up()
            elif event.key == K_PAGEDOWN:
                self.stream.down(6)
            elif event.key == K_PAGEUP:
                self.stream.up(6)
        elif event.type == MOUSEBUTTONDOWN:
            # Handle mouse button press
            self._handle_mouse_down(event)
        elif event.type == MOUSEBUTTONUP:
            # Handle mouse button release
            self._handle_mouse_up(event)
        elif event.type == MOUSEMOTION:
            # Handle mouse movement
            self._handle_mouse_motion(event)

    def _handle_mouse_down(self, event):
        # Handle mouse button press for selecting or interacting with pieces
        if event.button == 1:  # Left click
            self.selected = None
            self.scrolling = False
            if self.stream.is_scroll_hit(event.pos):  # Check if scroll bar is clicked
                self.scrolling = True
            else:
                # Check if a floating piece is clicked
                for p in self.floating[::-1]:
                    if p.is_hit(event.pos):
                        self.selected = p
                        break
                if self.selected:
                    # Move the selected piece to the top of the floating list
                    self.floating.remove(self.selected)
                    self.floating.append(self.selected)
                else:
                    # Select a piece from the stream
                    self.selected = self.stream.get_piece_at(event.pos)
                    if self.selected:
                        self.stream.remove(self.selected)
                        self.floating.append(self.selected)
        elif event.button == 3:  # Right click
            # Split a group of pieces into individual pieces
            sel = None
            for p in self.floating[::-1]:
                if p.is_hit(event.pos):
                    if not p.is_piece():
                        sel = p
                        break
            if sel:
                self.floating.remove(sel)
                for p in sel.pieces:
                    p.rect.x += randint(3, 10) * choice((1, -1))
                    p.rect.y += randint(3, 10) * choice((1, -1))
                    self.floating.append(p)
        elif event.button == 4:  # Scroll up
            self.stream.up()
        elif event.button == 5:  # Scroll down
            self.stream.down()

    def _handle_mouse_up(self, event):
        # Handle mouse button release for dropping pieces
        if self.scrolling:
            self.scrolling = False
            self.stream.stop_scroll()
        elif self.selected:
            # Try to drop the selected piece onto the board
            if self.board.drop(self.selected):
                self.floating.remove(self.selected)
                if self.selected.is_piece():
                    self.score_table.add_piece_score()
                else:
                    self.score_table.add_piece_score(len(self.selected.pieces))
            elif self.stream.drop(self.selected):
                # Drop the piece back into the stream
                self.floating.remove(self.selected)
            else:
                # Check if the selected piece can be grouped with another piece
                friend = None
                for f in self.floating:
                    if f == self.selected:
                        continue
                    if f.is_friend(self.selected):
                        friend = f
                        break
                if friend:
                    if not friend.is_piece():
                        friend.append(self.selected)
                        self.floating.remove(self.selected)
                    else:
                        # Create a new group of pieces
                        ppg = PuzzlePieceGroup(friend)
                        ppg.append(self.selected)
                        self.floating.remove(self.selected)
                        self.floating.remove(friend)
                        self.floating.append(ppg)

        self.selected = None

    def _handle_mouse_motion(self, event):
        # Handle mouse movement for dragging pieces or scrolling
        if self.scrolling:
            self.stream.do_scroll(event.pos)
        elif self.selected:
            self.selected.translate(event.rel)

    def update(self, screen): 
        # Update the game state and render the screen
        screen.fill(self.back_color)  # Fill the background

        # Draw the board and stream areas
        pygame.draw.rect(screen, self.board_color, self.board.r)
        pygame.draw.rect(screen, self.stream_color, self.stream.rect)

        # Draw the board, stream, and floating pieces
        self.board.draw(screen)
        self.stream.draw(screen)
        for p in self.floating:
            p.draw_shadow(screen)
            p.draw(screen)

        # Check if the puzzle is completed
        if len(self.board.pieces) == 80 and not self.game_completed:
            self.game_completed = True
            self.score_table.mark_completed()  # Mark the puzzle as completed
            self.score_table.apply_time_bonus()  # Apply a time bonus to the score

        # Draw the score and time
        self._draw_score(screen)

        # Display a completion message if the puzzle is finished
        if self.game_completed:
            completion_text = self.loader.load_font_black(30).render(
                "Puzzle Completed!", True, (0, 255, 0)
            )
            completion_rect = completion_text.get_rect(
                center=(self.board.r.centerx, self.board.r.bottom + 35)  
            )
            pygame.draw.rect(screen, (0, 0, 0), completion_rect.inflate(10, 10))  
            screen.blit(completion_text, completion_rect.topleft)

        # Update and draw the UI
        self.ui_manager.update(1 / 30)
        self.ui_manager.draw_ui(screen)

        return self.next_part  # Return the next game state

    def _draw_score(self, screen):
        # Draw the score, elapsed time, and bonus message
        font = self.loader.load_font_medium(20)

        # Display the current score
        score_text = font.render(f"Score: {self.score_table.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(topleft=(20, 10))
        pygame.draw.rect(screen, (0, 0, 0), score_rect.inflate(4, 4))  
        screen.blit(score_text, score_rect.topleft)

        # Display the elapsed time
        elapsed_time = self.score_table.get_elapsed_time()
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        time_text = font.render(f"Time: {minutes:02}:{seconds:02}", True, (255, 255, 255))
        time_rect = time_text.get_rect(topleft=(20, score_rect.bottom + 10))
        pygame.draw.rect(screen, (0, 0, 0), time_rect.inflate(4, 4))  
        screen.blit(time_text, time_rect.topleft)

        # Display the bonus message
        _, bonus_message = self.score_table.calculate_time_bonus()
        bonus_text = font.render(f"{bonus_message}", True, (255, 255, 255))
        bonus_rect = bonus_text.get_rect(topleft=(20, time_rect.bottom + 10))
        pygame.draw.rect(screen, (0, 0, 0), bonus_rect.inflate(4, 4))  
        screen.blit(bonus_text, bonus_rect.topleft)

    def __del__(self):
        # Save the best score and clean up resources when the game ends
        if self.game_completed:  
            self.score_table.save_best_score()
        self.score_table.close()