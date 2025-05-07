import pygame
from pygame.locals import *

class PieceStream(object):
    def __init__(self, pieces, board_y, board_height):
        # Initialize the piece stream with a list of pieces and its position
        self.pieces = pieces  # List of puzzle pieces
        self.rect = pygame.Rect(685, board_y + (board_height - (96 * 6)) // 2, 96, 96 * 6)  # Stream area
        self.start = 0  # Index of the first piece in the visible page
        self.scroll_box = pygame.Rect(786, self.rect.y, 9, self.rect.height)  # Scroll bar container
        self.scroll = pygame.Rect(786, self.rect.y, 9, self.rect.height)  # Scroll bar
        self.scroll_mod = 0  # Offset for scrolling
        self.scrolling = False  # Whether the stream is being scrolled
        self._update()  # Update the stream to initialize positions

    def _update(self):
        # Update the visible pieces and scroll bar position
        size = len(self.pieces)
        if size <= 6:
            self.start = 0  # Reset start index if fewer than 6 pieces
        else:
            if size - self.start < 6:
                self.start = size - 6  # Adjust start index if fewer pieces remain
        if self.start < 0:
            self.start = 0  # Ensure start index is not negative

        # Calculate scroll bar position and size
        if size <= 6:
            s = 5
            e = 590
        else:
            p = 590.0 / float(size)  # Proportional height of the scroll bar
            s = (self.start * p) + 5
            e = (6.0 * p) + 1

        self.scroll.y = s
        self.scroll.h = e + 150  # Adjust scroll bar height

        # Update the positions of visible pieces
        y = self.rect.y
        for p in self.get_page():
            p.set_pos(self.rect.x, y)
            y += 96

    def down(self, cnt=1):
        # Scroll down by a specified number of pieces
        if self.scrolling:
            return
        self.start += cnt
        self._update()

    def up(self, cnt=1):
        # Scroll up by a specified number of pieces
        if self.scrolling:
            return
        self.start -= cnt
        self._update()

    def get_page(self):
        # Get the current visible page of pieces
        return self.pieces[self.start:][:6]

    def is_scroll_hit(self, pos):
        # Check if the scroll bar or scroll box is clicked
        if self.scroll.collidepoint(pos):
            self.scrolling = True
            self.scroll_mod = pos[1] - self.scroll.top  # Calculate scroll offset
            return True
        else:
            if self.scroll_box.collidepoint(pos):
                # Scroll up or down based on click position
                if pos[1] < self.scroll.top:
                    self.up(6)
                else:
                    self.down(6)
        return False

    def do_scroll(self, pos):
        # Perform scrolling based on mouse position
        p = 590.0 / float(len(self.pieces))  # Proportional scroll step
        self.start = int(round((float(pos[1] - self.scroll_mod) - 5.0) / p))
        self._update()

    def stop_scroll(self):
        # Stop scrolling
        self.scrolling = False

    def remove(self, piece):
        # Remove a piece from the stream
        self.pieces.remove(piece)
        self._update()

    def drop(self, piece):
        # Drop a piece into the stream
        if not piece.is_piece():
            return False
        if self.rect.colliderect(piece.rect):  # Check if the piece is within the stream area
            inserted = False
            for p in self.get_page()[::-1]:
                if p.rect.colliderect(piece.rect):  # Find the correct position to insert
                    self.pieces.insert(self.pieces.index(p), piece)
                    inserted = True
                    break
            if not inserted:
                self.pieces.append(piece)  # Append to the end if no overlap
            self._update()
            return True
        return False

    def get_piece_at(self, pos):
        # Get the piece at a specific position
        if self.scrolling:
            return None
        for p in self.get_page():
            if p.is_hit(pos):  # Check if the position hits a piece
                return p
        return None

    def draw(self, dest):
        # Draw the stream and its pieces
        dest.fill((255, 255, 255), self.scroll)  # Draw the scroll bar

        for p in self.get_page():
            p.draw_shadow(dest)  # Draw the shadow of each piece
            p.draw(dest)  # Draw the piece itself