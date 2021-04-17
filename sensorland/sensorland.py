#Stefan in Sensorland
import matplotlib.image as img
import numpy as np
import os

class SensorLandGame:
    def __init__(self):
        self.path = os.path.dirname(__file__)

    def get_title_image(self):
        """Get the iconic image of the game

        """
        im = img.imread(os.path.join(self.path, 'images/stefan_in_sensor_land.png'))
        image = np.transpose(im[:, :, :3], (1, 0, 2)) * 255
        return image

    def run_game(self, display, input_control):
        """Run the Game

        """
        print("Implement me")