# Stefan in Sensorland
import matplotlib.image as img
import numpy as np
import os
import time
import pygame

GROUND_LEVEL = 31


def get_image_scene(position_x, width_x, image_in):
    """Get section of the image

    :param position_x:
    :param width_x:
    :param image_in:
    :return:
    """
    image_out = np.zeros((width_x, image_in.shape[1], image_in.shape[2]))
    start = position_x % image_in.shape[0]
    stop = start + width_x
    if stop < image_in.shape[0]:
        image_out[:, :, :] = image_in[start:stop, :, :]
    else:
        delta = image_in.shape[0] - start
        image_out[:delta, :, :] = image_in[start:, :, :]
        image_out[delta:, :, :] = image_in[:width_x - delta, :, :]
    return image_out


class SensorLandGame:
    def __init__(self):
        self.path = os.path.dirname(__file__)
        self.display = 0
        self.mountains = 0
        self.input_control = 0
        self.player_y = GROUND_LEVEL
        self.sound_jump = pygame.mixer.Sound('sensorland/sound/jump.wav')

    def get_title_image(self):
        """Get the iconic image of the game

        """
        im = img.imread(os.path.join(self.path, 'images/stefan_in_sensor_land.png'))
        image = np.transpose(im[:, :, :3], (1, 0, 2)) * 255
        return image

    def do_mountains(self, mountains, position):
        """Move the mountains

        :return:
        """
        m = get_image_scene(position, self.display.size_x, mountains)
        self.display.place_sprite(m, 0, 21)

    def do_circuit(self, circuit, position):
        """Move the circuit

        :return:
        """
        m = get_image_scene(position, self.display.size_x, circuit)
        self.display.place_sprite(m, 0, 46)

    def do_sky(self, sky, iteration):
        """

        :param sky:
        :param iteration:
        :return:
        """
        x = int(32 + np.cos(iteration / 60) * 32)
        y = int(32 + np.sin(iteration / 60) * 32)
        self.display.show_image(sky[x:x + 64, y:y + 64, :])

    def run_game(self, display, input_control):
        """Run the Game

        """
        self.display = display
        self.input_control = input_control
        im_arrow_left = img.imread('sensorland/images/stefan_0.png')
        stefan_0 = np.transpose(im_arrow_left, (1, 0, 2)) * 255

        im_arrow_right = img.imread('sensorland/images/stefan_1.png')
        stefan_1 = np.transpose(im_arrow_right, (1, 0, 2)) * 255

        im_arrow_right = img.imread('sensorland/images/stefan_2.png')
        stefan_2 = np.transpose(im_arrow_right, (1, 0, 2)) * 255

        mountains = img.imread('sensorland/images/mountains3.png')
        mountains = np.transpose(mountains, (1, 0, 2)) * 255

        circuit = img.imread('sensorland/images/circuit.png')
        circuit = np.transpose(circuit, (1, 0, 2)) * 255

        sun = img.imread('sensorland/images/sun.png')
        sun = np.transpose(sun, (1, 0, 2)) * 255

        sky = img.imread('sensorland/images/sky2.png')
        sky = np.transpose(sky, (1, 0, 2)) * 255

        pygame.mixer.music.load('sensorland/sound/theme.mp3')
        pygame.mixer.music.play(-1, 0.0)

        running = True
        jumping = False
        jumping_index = 0
        jumping_delta = [-8, -6, -4, -2, -2, -1, -1, 0, 0, 1, 1, 2, 2, 4, 6, 8]
        iteration = 0
        self.player_y = GROUND_LEVEL
        while running:
            self.do_sky(sky, iteration * 1)
            self.do_mountains(mountains, int(iteration * 1))
            self.do_circuit(circuit, iteration*2)
            if not jumping:
                if iteration % 2 == 0:
                    self.display.place_sprite(stefan_0, 5, self.player_y)
                if iteration % 2 == 1:
                    self.display.place_sprite(stefan_1, 5, self.player_y)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LEFT] == 1 and self.player_y == GROUND_LEVEL:
                        jumping = True
                        jumping_index = 0
                        pygame.mixer.Sound.play(self.sound_jump)

            if jumping:
                self.display.place_sprite(stefan_2, 5, self.player_y)
                if jumping_index < len(jumping_delta):
                    self.player_y += jumping_delta[jumping_index]
                    jumping_index += 1
                else:
                    jumping = False
            iteration = iteration + 1
            # show score
            self.display.write_string("SCORE", 1, 0, background=None)
            self.display.write_string("{:8d}".format(iteration), 20, 0, background=None)
            self.display.show()
            time.sleep(0.1)
        print("Implement me")
