#Stefan in Sensorland
import matplotlib.image as img
import numpy as np
import os
import time
import pygame

GROUND_LEVEL = 31

class SensorLandGame:
    def __init__(self):
        self.path = os.path.dirname(__file__)
        self.display = 0
        self.mountains = 0
        self.input_control = 0
        self.player_y = GROUND_LEVEL

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
        start = position % mountains.shape[0]
        stop = start + 64
        if stop < mountains.shape[0]:
            self.mountains = mountains[start:stop, :, :]
        else:
            delta = mountains.shape[0] - start
            self.mountains[:delta] = mountains[start:, :, :]
            #TODO use display property, do not hardcode 64
            self.mountains[delta:64] = mountains[:64-delta, :, :]
        self.display.place_sprite(self.mountains, 0, 21)

    def do_circuit(self, circuit, position):
        """Move the mountains

        :return:
        """
        start = position % circuit.shape[0]
        stop = start + 64
        if stop < circuit.shape[0]:
            self.temp = circuit[start:stop, :, :]
        else:
            delta = circuit.shape[0] - start
            self.temp[:delta] = circuit[start:, :, :]
            #TODO use display property, do not hardcode 64
            self.temp[delta:64] = circuit[:64-delta, :, :]
        self.display.place_sprite(self.temp, 0, 46)


    def do_sky(self, sky, iteration):
        """

        :param sky:
        :param iteration:
        :return:
        """
        x = int(32 + np.cos(iteration/60) * 32)
        y = int(32 + np.sin(iteration/60) * 32)
        self.display.show_image(sky[x:x+64, y:y+64, :])

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

        mountains = img.imread('sensorland/images/mountains.png')
        mountains = np.transpose(mountains, (1, 0, 2)) * 255

        circuit = img.imread('sensorland/images/circuit.png')
        circuit = np.transpose(circuit, (1, 0, 2)) * 255

        sun = img.imread('sensorland/images/sun.png')
        sun = np.transpose(sun, (1, 0, 2)) * 255

        sky = img.imread('sensorland/images/sky2.png')
        sky = np.transpose(sky, (1, 0, 2)) * 255

        running = True
        jumping = False
        jumping_index = 0
        jumping_delta = [-8, -6, -4, -2, -2, -1, -1, 0, 0, 1, 1, 2, 2, 4, 6, 8]
        iteration = 0
        self.player_y = GROUND_LEVEL
        while running:
#            self.display.show_image(sun)
            self.do_sky(sky, iteration*1)
            self.do_mountains(mountains, int(iteration/2))
            self.do_circuit(circuit, iteration)
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
            if jumping:
                self.display.place_sprite(stefan_2, 5, self.player_y)
                if jumping_index < len(jumping_delta):
                    self.player_y += jumping_delta[jumping_index]
                    jumping_index += 1
                else:
                    jumping = False
            iteration = iteration + 1
            self.display.show()
            time.sleep(0.1)
        print("Implement me")