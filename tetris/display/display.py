import numpy as np
import pygame
import time
from .simple_fonts import *

class Display:
    """Display class
    """

    def __init__(self, size_x, size_y, type=0):
        """
        Initializes display of size x,y
        :param size_x:
        :param size_y:
        :param type:
        """
        self.image = np.zeros((size_x, size_y, 3))
        self.type = type
        self.size_x = size_x
        self.size_y = size_y
        self.factor = 8
        if type == 0:
            pygame.init()
            self.scr = pygame.display.set_mode((self.size_x * self.factor, self.size_y * self.factor))
            self.scr.fill((0, 0, 0))

    def set_pixel(self, x, y, color):
        """Set pixel to color

        :param x:
        :param y:
        :param color:
        :return:
        """
        self.image[x, y, 0] = color[0]
        self.image[x, y, 1] = color[1]
        self.image[x, y, 2] = color[2]

    def clear_screen(self, color=None):
        """Sets the whole screen to a given color

        :param color:
        :return:
        """
        if not color:
            self.image[:, :, :] = 0
        else:
            self.image[:, :, 0] = color[0]
            self.image[:, :, 1] = color[1]
            self.image[:, :, 2] = color[2]

    def fade_to_image(self, image):
        """Fading from current image to given image

        :param image:
        :return:
        """
        old_image = np.copy(self.image)
        n_steps = 20
        for i in range(n_steps):
            factor = i/(n_steps-1)
            self.image = old_image*(1-factor) + image*factor
            self.show()
            time.sleep(0.2)

    def write_string(self, message, x, y, foreground=[255, 255, 255], background=[0, 0, 0]):
        """Write a string, starting at position x, y with given fg and bg color

        :param message: the message
        :param x: x-position
        :param y: y-position
        :param foreground: fg color
        :param background: bg color
        :return:
        """
        x_size = len(message) * 4 - 1
        for i in range(x_size):
            self.image[x + i, y, :] = background
            self.image[x + i, y + 1, :] = background
            self.image[x + i, y + 2, :] = background
            self.image[x + i, y + 3, :] = background
            self.image[x + i, y + 4, :] = background

        x_pos = x
        for letter in message:
            char_image = font3x5[letter]
            for i in range(15):
                color = background
                if char_image[i]:
                    color = foreground
                x_image = x_pos + (i % 3)
                y_image = y + int(i/3)
                self.image[x_image, y_image, :] = color
            x_pos = x_pos + 4

    def show(self):
        """Show the current image

        :return:
        """
        if self.type == 0:
            for x in range(self.size_x):
                for y in range(self.size_y):
                    color = (self.image[x, y, 0], self.image[x, y, 1], self.image[x, y, 2])
                    pygame.draw.circle(self.scr, color, ((x+0.5) * self.factor, (y+0.5) * self.factor), self.factor/2-1)
            pygame.display.update()