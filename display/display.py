import numpy as np
import pygame
import time
from .simple_fonts import *
import importlib
from PIL import Image

rgbmatrix_installed = importlib.util.find_spec("rgbmatrix")
if rgbmatrix_installed:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions

DISPLAY_TYPE_SCREEN = 0
DISPLAY_TYPE_LED = 1
DISPLAY_TYPE_BOTH = 2


class Display:
    """Display class
    """

    def __init__(self, size_x, size_y, display_type=DISPLAY_TYPE_SCREEN):
        """
        Initializes display of size x,y
        :param size_x:
        :param size_y:
        :param display_type: 0 -> Display on screen
                             1 -> Display on LED-matrix
                             2 -> Use both
        """
        self.image = np.zeros((size_x, size_y, 3))
        self.size_x = size_x
        self.size_y = size_y
        self.factor = 8
        self.use_screen = (display_type == DISPLAY_TYPE_SCREEN) or (display_type == DISPLAY_TYPE_BOTH)
        self.use_led = ((display_type == DISPLAY_TYPE_LED) or (display_type == DISPLAY_TYPE_BOTH)) \
                       and rgbmatrix_installed
        if self.use_screen:
            pygame.init()
            self.scr = pygame.display.set_mode((self.size_x * self.factor, self.size_y * self.factor))
            self.scr.fill((0, 0, 0))
        if self.use_led:
            options = RGBMatrixOptions()
            options.rows = 64
            options.cols = 64
            options.chain_length = 1
            options.parallel = 2
            options.scan_mode = 1
            options.multiplexing = 0
            options.hardware_mapping = 'regular'  # If you have an Adafruit HAT: 'adafruit-hat'
            options.disable_hardware_pulsing = True
            options.gpio_slowdown = 4
            options.drop_privileges = False
            #        options.limit_refresh_rate_hz = 80
            #        options.row_address_type = self.args.led_row_addr_type
            #        options.multiplexing = self.args.led_multiplexing
            options.pwm_bits = 11
            options.brightness = 100
            options.pwm_lsb_nanoseconds = 130
            #        options.led_rgb_sequence = self.args.led_rgb_sequence
            #        options.pixel_mapper_config = self.args.led_pixel_mapper
            #        options.panel_type = self.args.led_panel_type
            self.matrix = RGBMatrix(options=options)

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

    def fill_rectangle(self, x_low, x_high, y_low, y_high, color):
        """Set rectangle to color

        """
        self.image[x_low:x_high + 1, y_low:y_high + 1, 0] = color[0]
        self.image[x_low:x_high + 1, y_low:y_high + 1, 1] = color[1]
        self.image[x_low:x_high + 1, y_low:y_high + 1, 2] = color[2]

    def draw_rectangle(self, x_low, x_high, y_low, y_high, color):
        """draw a rectangle

        """
        self.image[x_low:x_high + 1, y_low, :] = color
        self.image[x_low:x_high + 1, y_high, :] = color
        self.image[x_low, y_low:y_high + 1, :] = color
        self.image[x_high, y_low:y_high + 1, :] = color

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
            factor = i / (n_steps - 1)
            self.image = old_image * (1 - factor) + image * factor
            self.show()
            time.sleep(0.2)

    def show_image(self, image):
        """Showing an image

        :param image: the image
        :return:
        """
        self.image = image.copy()

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
            if background:
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
                y_image = y + int(i / 3)
                if color:
                    self.image[x_image, y_image, :] = color
            x_pos = x_pos + 4

    def place_sprite(self, sprite, x_anchor, y_anchor):
        """Place a sprite at image position (x_anchor, y_anchor)

        """
        for i in range(sprite.shape[0]):
            for j in range(sprite.shape[1]):
                x = x_anchor + i
                y = y_anchor + j
                if 0 <= x < self.size_x and 0 <= y < self.size_y:
                    # Check for transparency
                    if sprite[i, j, 3] > 0:
                        self.image[x, y, :] = sprite[i, j, :3]

    def show(self):
        """Show the current image

        :return:
        """
        if self.use_screen:
            for x in range(self.size_x):
                for y in range(self.size_y):
                    color = (self.image[x, y, 0], self.image[x, y, 1], self.image[x, y, 2])
                    pygame.draw.circle(self.scr, color, ((x + 0.5) * self.factor, (y + 0.5) * self.factor),
                                       self.factor / 2 - 1)
            #                    pygame.draw.rect(self.scr, color, pygame.Rect(x* self.factor, y* self.factor, self.factor, self.factor) )
            pygame.display.update()
        if self.use_led:
            # TODO drayebe: change on vsync
            tmp = np.flipud(self.image)
            self.matrix.SetImage(Image.fromarray(tmp.astype('uint8'), 'RGB'), 0, 0)
