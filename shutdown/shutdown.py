import matplotlib.image as img
import numpy as np
import os
import time
import pygame
import random
from leaderboard.leader_board import *
from controls.input_control import *


class ShutDown:
    def __init__(self):
        self.path = os.path.dirname(__file__)
        self.display = 0
        self.mountains = 0
        self.input_control = 0

    def get_title_image(self):
        """Get the iconic image of the game

        """
        im = img.imread('shutdown/images/shutdown.png')
        image = np.transpose(im[:, :, :3], (1, 0, 2)) * 255
        return image

    def run_game(self, display=0, input_control=0):
        """Run the game, in this case shut the fuck down

        :param display:
        :param input_control:
        :return:
        """
        pygame.mixer.music.pause()
        sound_shutdown = pygame.mixer.Sound('shutdown/sound/winxpshutdown.mp3')
        pygame.mixer.Sound.play(sound_shutdown)
        im = img.imread('shutdown/images/shutdown_win.png')
        image = np.transpose(im[:, :, :3], (1, 0, 2)) * 255
        display.show_image(image)
        display.show()
        time.sleep(3)
        os.system("shutdown -h now")