import pygame
from pygame.locals import *

class Board(object):
    def __init__(self, orgimg):
        # Initialize the board with a rectangular area, an empty list of pieces, and the original image
        self.r = pygame.Rect(20, 167, 640, 512)  # Defines the board's rectangular area
        self.pieces = []  # List to store pieces placed on the board
        self.orgimg = orgimg  # Original image to display when the board is complete
   
    def drop(self, piece):
        # Handles dropping a piece or a group of pieces onto the board
        if piece.is_piece():  # Check if the object is a single piece
            if self.r.colliderect(piece.rect):  # Check if the piece is within the board's area
                destx = self.r.x + (64 * piece.px) - 16  # Calculate the target x-coordinate
                desty = self.r.y + (64 * piece.py) - 16  # Calculate the target y-coordinate
                # Check if the piece is close enough to snap into position
                if abs(piece.rect.x - destx) <= 10 and abs(piece.rect.y - desty) <= 10:
                    piece.set_pos(destx, desty)  # Snap the piece into position
                    self.pieces.append(piece)  # Add the piece to the board
                    return True
            return False
        else:
            # If the object is a group of pieces, recursively drop each piece
            res = False
            for p in piece.pieces:
                res = self.drop(p)
            return res
       
    def draw(self, dest):
        # Draw the board and its pieces onto the destination surface
        for p in self.pieces:
            p.draw_shadow(dest, 1)  # Draw shadows for each piece
        if len(self.pieces) == 80:  # If all pieces are placed, draw the original image
            dest.blit(self.orgimg, self.r.topleft)
        else:
            for p in self.pieces:
                p.draw(dest)  # Draw each piece individually