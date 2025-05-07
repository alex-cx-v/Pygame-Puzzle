import pygame
from pygame.locals import *
from os import path, listdir

class Loader:
    def __init__(self):      
        # Initialize paths for images, motives, and fonts
        self.img_path = path.join("data", "img")  # Path to general images
        self.motive_path = path.join("data", "motive")  # Path to puzzle motives
        self.font_path = path.join("data", "fnt")  # Path to font files
   
    def load_image(self, filename):
        # Load an image from the img_path directory
        return pygame.image.load(path.join(self.img_path, filename))

    def load_motive(self, filename):
        # Load and scale a puzzle motive image
        file_path = path.join(self.motive_path, filename)
        img = pygame.image.load(file_path)
    
        if filename.lower().endswith('.png'):
            img = img.convert_alpha()  # Preserve transparency for PNG files
        else:
            img = img.convert()  # Optimize for display without transparency
    
        return pygame.transform.smoothscale(img, (640, 512))  # Resize to fit the board

    def list_motives(self):
        # List all available puzzle motive files (JPG and PNG) in the motive_path directory
        return [f for f in listdir(self.motive_path) if f.lower().endswith(('.jpg', '.png'))]

    def load_font_black(self, size):
        # Load the "Black" font with the specified size
        return pygame.font.Font(path.join(self.font_path, "FixelDisplay-Black.otf"), size)

    def load_font_medium(self, size):
        # Load the "Medium" font with the specified size
        return pygame.font.Font(path.join(self.font_path, "FixelDisplay-Medium.otf"), size)