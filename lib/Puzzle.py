import pygame
from pygame.locals import *
from random import choice, shuffle

class PuzzlePieceGroup(object):
    def __init__(self, piece):
        # Initialize a group of puzzle pieces with a single piece
        self.pieces = [piece]

    def is_piece(self):
        # Return False since this is a group of pieces
        return False

    def append(self, piece):
        # Add a piece or group of pieces to this group
        if piece.is_piece():
            self.pieces.append(piece)
            op = self.pieces[0]
            p = piece
            # Adjust the position of the new piece relative to the group
            p.rect.x = op.rect.x + ((p.px - op.px) * 64)
            p.rect.y = op.rect.y + ((p.py - op.py) * 64)
        else:
            for p in piece.pieces:
                self.append(p)

    def is_friend(self, piece):
        # Check if the given piece can be joined with this group
        if piece.is_piece():
            for p in self.pieces:
                if p.is_friend(piece):
                    return True
            return False
        else:
            for p in piece.pieces:
                if self.is_friend(p):
                    return True
            return False

    def is_hit(self, pos):
        # Check if the given position hits any piece in the group
        for p in self.pieces:
            if p.is_hit(pos):
                return True
        return False

    def translate(self, rel):
        # Move all pieces in the group by a relative offset
        for p in self.pieces:
            p.translate(rel)

    def draw(self, dest):
        # Draw all pieces in the group
        for p in self.pieces:
            p.draw(dest)

    def draw_shadow(self, dest, pos=3):
        # Draw shadows for all pieces in the group
        for p in self.pieces:
            p.draw_shadow(dest, pos)

class PuzzlePiece(object):
    def __init__(self, image, shadow, x, y, px, py):
        # Initialize a single puzzle piece with its image, shadow, and position
        self.px = px  # Grid x-coordinate
        self.py = py  # Grid y-coordinate

        self.img = image  # Piece image
        self.rect = self.img.get_rect()
        self.rect.center = (x, y)

        self.simg = shadow  # Shadow image
        self.srect = self.simg.get_rect()
        self.srect.center = (x + 3, y + 3)

    def is_piece(self):
        # Return True since this is a single piece
        return True

    def is_friend(self, piece):
        # Check if the given piece can be joined with this piece
        if not piece.is_piece():
            return piece.is_friend(self)

        # Check adjacency and alignment
        if self.px + 1 == piece.px and self.py == piece.py:
            if abs(piece.rect.x - (self.rect.x + 64)) <= 10 and abs(piece.rect.y - self.rect.y) <= 10:
                return True
        elif self.px - 1 == piece.px and self.py == piece.py:
            if abs(piece.rect.x - (self.rect.x - 64)) <= 10 and abs(piece.rect.y - self.rect.y) <= 10:
                return True
        elif self.px == piece.px and self.py + 1 == piece.py:
            if abs(piece.rect.x - self.rect.x) <= 10 and abs(piece.rect.y - (self.rect.y + 64)) <= 10:
                return True
        elif self.px == piece.px and self.py - 1 == piece.py:
            if abs(piece.rect.x - self.rect.x) <= 10 and abs(piece.rect.y - (self.rect.y - 64)) <= 10:
                return True
        return False

    def is_hit(self, pos):
        # Check if the given position hits this piece
        if self.rect.collidepoint(pos):
            x = pos[0] - self.rect.left
            y = pos[1] - self.rect.top
            col = self.img.get_at((x, y))
            if col[3] == 255:  # Check if the pixel is not transparent
                return True
        return False

    def set_pos(self, x, y):
        # Set the position of the piece
        self.rect.x = x
        self.rect.y = y

    def translate(self, rel):
        # Move the piece by a relative offset
        self.rect.x += rel[0]
        self.rect.y += rel[1]

    def draw(self, dest):
        # Draw the piece on the destination surface
        dest.blit(self.img, self.rect.topleft)

    def draw_shadow(self, dest, pos=3):
        # Draw the shadow of the piece
        self.srect.x = self.rect.x + pos
        self.srect.y = self.rect.y + pos
        dest.blit(self.simg, self.srect.topleft)

# Constants for edge types
PEG = 0
HOLE = 1
EDGE = 2

# Constants for edge positions
TOP = 0
RIGHT = 1
BOTTOM = 2
LEFT = 3

class PuzzleFactory(object):
    def __init__(self, image, mask_image, bevel_image, shadow_image):
        # Initialize the puzzle factory with images for pieces and edges
        self.img = (pygame.Surface((640 + 32, 512 + 32), pygame.SRCALPHA)).convert_alpha()
        self.img.fill((0, 0, 0, 0))
        self.img.blit(image, (16, 16))

        self.mask_img = mask_image  # Mask for cutting pieces
        self.bevel_img = bevel_image  # Bevel effect for pieces
        self.shadow_img = shadow_image  # Shadow effect for pieces

        self._setup_edges()  # Generate random edges for the puzzle

    def _setup_edges(self):
        # Generate random edges for all puzzle pieces
        self.edges = []
        for y in range(8):
            row = []
            self.edges.append(row)
            for x in range(10):
                # Set top edge
                if y == 0:
                    top = EDGE
                else:
                    if self.edges[y - 1][x][BOTTOM] == PEG:
                        top = HOLE
                    else:
                        top = PEG
                # Set bottom edge
                if y == 7:
                    bottom = EDGE
                else:
                    bottom = choice((PEG, HOLE))
                # Set left edge
                if x == 0:
                    left = EDGE
                else:
                    if self.edges[y][x - 1][RIGHT] == PEG:
                        left = HOLE
                    else:
                        left = PEG
                # Set right edge
                if x == 9:
                    right = EDGE
                else:
                    right = choice((PEG, HOLE))
                row.append((top, right, bottom, left))

    def _make_form(self, img, edges):
        # Create a piece form based on its edges
        top, right, bottom, left = edges

        res = (pygame.Surface((96, 96), pygame.SRCALPHA)).convert_alpha()
        res.fill((0, 0, 0, 0))

        center = pygame.Rect(32, 32, 32, 32)
        top_r = pygame.Rect(16 + 96 * top, 0, 64, 32)
        bottom_r = pygame.Rect(16 + 96 * bottom, 64, 64, 32)
        right_r = pygame.Rect(64 + 96 * right, 32, 32, 32)
        left_r = pygame.Rect(0 + 96 * left, 32, 32, 32)

        res.blit(img, center, center)
        res.blit(img, (16, 0), top_r)
        res.blit(img, (16, 64), bottom_r)
        res.blit(img, (0, 32), left_r)
        res.blit(img, (64, 32), right_r)
        return res

    def _make_piece(self, px, py):
        # Create a single puzzle piece at the given grid position
        r = pygame.Rect(px * 64, py * 64, 96, 96)
        src = self.img.subsurface(r)

        mask = self._make_form(self.mask_img, self.edges[py][px])
        bevel = self._make_form(self.bevel_img, self.edges[py][px])
        shadow = self._make_form(self.shadow_img, self.edges[py][px])

        dest = (pygame.Surface((96, 96), pygame.SRCALPHA)).convert_alpha()
        dest.fill((0, 0, 0, 0))

        for y in range(96):
            for x in range(96):
                m = mask.get_at((x, y))
                if m[3] == 255:  # Only copy pixels within the mask
                    dest.set_at((x, y), src.get_at((x, y)))

        dest.blit(bevel, (0, 0))

        return PuzzlePiece(dest, shadow, 40 + 64 * px, 40 + 64 * py, px, py)

    def get_pieces(self):
        # Generate and return all puzzle pieces
        p = []
        for y in range(8):
            for x in range(10):
                p.append(self._make_piece(x, y))
        shuffle(p)  # Shuffle the pieces randomly
        return p