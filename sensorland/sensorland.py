# Stefan in Sensorland
import matplotlib.image as img
import numpy as np
import os
import time
import pygame
import random
from leaderboard.leader_board import *

GROUND_LEVEL = 31
NUMBER_OF_CIRCUIT_ELEMENTS = 23     #Number of parts to combine the circuits
#Values for the color transformation of the circuit
CIRCUIT_RED_VALUES = [9, 126, 210]
CIRCUIT_TARGET_VALUES = [[[9, 94, 42], [126, 152, 63], [210, 192, 42]],
                         [[24, 94, 213], [126, 152, 63], [210, 192, 42]],
                         [[213, 64, 24], [126, 152, 63], [210, 192, 42]],
                         [[0, 0, 0], [126, 152, 63], [210, 192, 42]],
                         [[213, 24, 148], [126, 152, 63], [210, 192, 42]],
                         [[9, 94, 42], [126, 152, 63], [210, 192, 42]]
                         ]


def load_and_transpose_image(path_to_image):
    """Load and transpose image, scale it to range 0,...,255

    :param path_to_image: path to image
    :return:
    """
    image_raw = img.imread(path_to_image)
    return np.transpose(image_raw, (1, 0, 2)) * 255


def transform_color(image, red_values, target_values):
    """Do a color transformation of an image based on its red values
    It would be better if the image was gray-scale and we could color
    it with the uniqe gray values, but Wunschkonzert ist Mittwochs ;-)

    :param image: original image
    :param red_values: key values
    :param target_values: triplets that hav the soecified red value are colored with
                          these values
    :return: colorized image
    """
    image_transformed = image.copy()
    image_red = image[:, :, 0]
    for key, target in zip(red_values, target_values):
        image_transformed[:, :, 0][image_red == key] = target[0]
        image_transformed[:, :, 1][image_red == key] = target[1]
        image_transformed[:, :, 2][image_red == key] = target[2]
    return image_transformed


class Circuit:
    """Class to handle the random circuit of sensor land

    """

    def __init__(self):
        """
        Init the circuit
        """
        self.elements = []
        self.max_element_size = 64
        for i in range(NUMBER_OF_CIRCUIT_ELEMENTS):
            element = load_and_transpose_image('sensorland/images/circuit_{:d}.png'.format(i))
            self.elements.append(element)
            self.max_element_size = max(self.max_element_size, element.shape[0])
            self.y = element.shape[1]
        self.position = 0
        self.image = np.zeros((self.max_element_size * 3, self.y, 4))
        self.generate_image()

    def scroll(self, delta=1):
        """Scroll the image further

        :param delta: scroll by delta steps
        :return:
        """
        if delta>0:
            self.image[:-delta, :, :] = self.image[delta:, :, :]
            self.position -= delta
            if self.position <= 2 * self.max_element_size:
                self.generate_image()

    def generate_image(self):
        """Fill the image with random circuit elements

        :return:
        """
        while self.position <= 2*self.max_element_size:
            index = random.randint(0, len(self.elements)-1)
            new_element = self.elements[index]
            delta = new_element.shape[0]
            self.image[self.position:self.position+delta, :, :] = new_element[:,:,:]
            self.position += delta

def get_image_scene(position_x, width_x, image_in):
    """Get section of the image

    :param position_x: position of the runner
    :param width_x: width of the screen
    :param image_in: input image
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


def compute_mask(sprite):
    """Compute foreground mask; pixel that are covered by the sprite

    :param sprite: sprite input
    :return: mask
    """
    mask = np.zeros((sprite.shape[0], sprite.shape[1]))
    indices_fg = sprite[:, :, 3] > 0
    mask[indices_fg] = 1
    return mask


def add_mask(mask, offset_x, offset_y, field):
    """

    :param mask:
    :param offset_x:
    :param offset_y:
    :param field:
    :return:
    """
    for xm in range(mask.shape[0]):
        for ym in range(mask.shape[1]):
            x = xm + offset_x
            y = ym + offset_y
            if 0 <= x < field.shape[0] and 0 <= y < field.shape[1]:
                field[x, y] += mask[xm, ym]


def check_collision(player, obstacles, max_x, max_y):
    """Check the collision between the player and the list of obstacles in the area
       0:max_x, 0:max_y

    :param player:
    :param obstacles:
    :param max_x:
    :param max_y:
    :return:
    """
    field = np.zeros((max_x, max_y))
    add_mask(player.mask, player.x, player.y, field)
    for obstacle in obstacles:
        add_mask(obstacle.mask, obstacle.x, obstacle.y, field)
        max_val = np.max(field[:])
        if max_val > 1:
            return True
    return False


class Player:
    def __init__(self, x, y, sprites_running, sprite_jumping, sprite_standing, sprite_dead):
        """

        :param x:
        :param y:
        """
        self.parabola = [-8, -6, -4, -2, -1, -1, -1, -1, 0, 0, 1, 1, 1, 1, 2, 4, 6, 8]
        self.is_jumping = False
        self.is_dead = False
        self.is_running = False
        self.parabola_position = 0
        self.x = x
        self.y = y
        # Load jump sound
        self.sound_jump = pygame.mixer.Sound('sensorland/sound/jump.wav')
        # Init the sprites
        self.sprite_jumping = sprite_jumping
        self.sprite_running = sprites_running
        self.sprite_running_id = 0
        self.sprite_standing = sprite_standing
        self.sprite_dead = sprite_dead
        self.sprite = sprite_standing
        # Init the masks
        self.mask_jumping = compute_mask(self.sprite_jumping)
        self.mask_running = [compute_mask(sprite) for sprite in self.sprite_running]
        self.mask = self.mask_running[self.sprite_running_id]

    def jump(self):
        """

        :return:
        """
        if not self.is_jumping:
            self.is_jumping = True
            pygame.mixer.Sound.play(self.sound_jump)

    def die(self):
        """

        :return:
        """
        self.is_dead = True
        self.sprite = self.sprite_dead

    def update(self, iteration):
        """

        :return:
        """
        # check dead ? dead ?
        if self.is_dead:
            self.sprite = self.sprite_dead
            return
        # if jumping do jump sprite
        if self.is_jumping:
            self.sprite = self.sprite_jumping
            self.mask = self.mask_jumping
            self.y = self.y + self.parabola[self.parabola_position]
            self.parabola_position += 1
            if self.parabola_position >= len(self.parabola):
                self.parabola_position = 0
                self.is_jumping = False
        # Animate running
        else:
            if iteration % 5 == 0:
                self.sprite_running_id = (self.sprite_running_id + 1) % len(self.sprite_running)
            self.sprite = self.sprite_running[self.sprite_running_id]
            self.mask = self.mask_running[self.sprite_running_id]


def create_stefan():
    """ Function that initializes Stefan

    :return: Player Stefan
    """
    stefan_0 = load_and_transpose_image('sensorland/images/stefan_0.png')
    stefan_1 = load_and_transpose_image('sensorland/images/stefan_1.png')
    stefan_jumping = load_and_transpose_image('sensorland/images/stefan_jumping.png')
    stefan_dead = load_and_transpose_image('sensorland/images/stefan_dead.png')
    stefan_standing = load_and_transpose_image('sensorland/images/stefan_standing.png')
    return Player(5, GROUND_LEVEL, [stefan_0, stefan_1], stefan_jumping, stefan_standing, stefan_dead)


class Element:
    def __init__(self, sprite, x, y):
        """Initial element with its sprite and position

        :param sprite:
        :param x:
        :param y:
        """
        self.sprite = sprite.copy()
        self.x = x
        self.y = y
        self.mask = compute_mask(self.sprite)

    def is_alive(self):
        """Check if the element is still on the screen or could be removed

        :return:
        """
        if self.x + self.sprite.shape[0] < 0:
            return False
        return True

    def move_relative(self, delta_x, delta_y):
        """Move Element relative to the current position

        :param delta_x:
        :param delta_y:
        :return:
        """
        self.x += delta_x
        self.y += delta_y


def get_obstacle():
    """Get a new obstacle

    :return: An obstacle
    """
    n_obstacles = 5
    obstacle_id = random.randint(0, n_obstacles-1)
    if obstacle_id == 0:
        image = load_and_transpose_image('sensorland/images/resistor.png')
        spawn_pos = [69, 35]
    elif obstacle_id == 1:
        image = load_and_transpose_image('sensorland/images/capacitor_0.png')
        spawn_pos = [69, 38]
    elif obstacle_id == 2:
        image = load_and_transpose_image('sensorland/images/voltage_regulator.png')
        spawn_pos = [70, 38]
    elif obstacle_id == 3:
        image = load_and_transpose_image('sensorland/images/led_red.png')
        spawn_pos = [68, 36]
    else:
        image = load_and_transpose_image('sensorland/images/led_green.png')
        spawn_pos = [68, 36]
    return Element(image, spawn_pos[0], spawn_pos[1])

SENSORLAND_SPEED = [2, 3, 4, 5, 6, 7]
SENSORLAND_ITERATION_INC = [1, 2, 3, 4, 5, 6]
SENSORLAND_END_OF_ROAD = [1000, 2000, 5000, 10000, 20000, 50000]

class SensorLandGame:
    def __init__(self):
        self.path = os.path.dirname(__file__)
        self.display = 0
        self.mountains = 0
        self.input_control = 0
        self.player_y = GROUND_LEVEL
        self.circuit = Circuit()
        self.score = 0

    def get_title_image(self):
        """Get the iconic image of the game

        """
        im = img.imread('sensorland/images/stefan_in_sensor_land.png')
        image = np.transpose(im[:, :, :3], (1, 0, 2)) * 255
        return image

    def do_mountains(self, mountains, position):
        """Move the mountains

        :return:
        """
        m = get_image_scene(position, self.display.size_x, mountains)
        self.display.place_sprite(m, 0, 21)

    def do_circuit(self, rel_movement, level_id=0):
        """Move the circuit

        :return:
        """
        self.circuit.scroll(rel_movement)
        m = self.circuit.image[0:64, :, :]
        m = transform_color(m, CIRCUIT_RED_VALUES, CIRCUIT_TARGET_VALUES[level_id])
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

    def do_level(self, level_id):
        """Execute a certain level, the speed etc. is configured above and
        accessed via the level id

        :param level_id: id of the currenct level
        :return: True -> Stefan is still running
                 False -> Stefan crushed with sth.
        """
        # Ready Player 1
        mountains = img.imread('sensorland/images/mountains3.png')
        mountains = np.transpose(mountains, (1, 0, 2)) * 255
        sky = img.imread('sensorland/images/sky2.png')
        sky = np.transpose(sky, (1, 0, 2)) * 255
        stefan = create_stefan()
        min_peace_time = 40
        remaining_peace_time = 10
        obstacles = []
        running = True
        iteration = 0
        speed = SENSORLAND_SPEED[level_id]
        iteration_increment = SENSORLAND_ITERATION_INC[level_id]
        level_end = SENSORLAND_END_OF_ROAD[level_id]
        #Game Loop
        while running:
            remaining_peace_time -= 1
            remaining_level = level_end-iteration
            if remaining_level <= 0:
                running = False
            if remaining_peace_time == 0 and remaining_level > (100 * iteration_increment):
                remaining_peace_time = min_peace_time
                obstacle = get_obstacle()
                obstacles.append(obstacle)
            dead_obstacles = []
            for obst in obstacles:
                obst.move_relative(-speed, 0)
                if not obst.is_alive():
                    dead_obstacles.append(obst)
            for obst in dead_obstacles:
                obstacles.remove(obst)
            self.do_sky(sky, iteration * 1)
            self.do_mountains(mountains, int(iteration * 1))
            self.do_circuit(speed, level_id)
            for obst in obstacles:
                self.display.place_sprite(obst.sprite, obst.x, obst.y)
            # Jump
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_UP] == 1:
                        stefan.jump()
            # Move
            stefan.update(iteration)
            # Check collision
            stefan_is_dead = check_collision(stefan, obstacles, self.display.size_x, self.display.size_y)
            if stefan_is_dead:
                stefan.die()
                running = False
            self.display.place_sprite(stefan.sprite, stefan.x, stefan.y)

            iteration += iteration_increment
            self.score += iteration_increment
            # show score
            self.display.write_string("SCORE", 1, 0, background=None)
            self.display.write_string("{:8d}".format(self.score), 20, 0, background=None)
            # show next speed
            if remaining_level < (100 * iteration_increment):
                self.display.write_string("NEXT LEVEL", 10, 30, background=None)
            self.display.show()
            time.sleep(0.02)
        if stefan_is_dead:
            time.sleep(1)
            return False
        return True

    def run_game(self, display, input_control):
        """Run the Game

        """
        self.display = display
        self.input_control = input_control
        leader_board = LeaderBoard('sensorland/records.txt')

        mountains = img.imread('sensorland/images/mountains3.png')
        mountains = np.transpose(mountains, (1, 0, 2)) * 255

        sky = img.imread('sensorland/images/sky2.png')
        sky = np.transpose(sky, (1, 0, 2)) * 255

        # Ready Player 1
        stefan = create_stefan()
        # wait for 1st keypress
        wait_for_start = True
        while wait_for_start:
            self.do_sky(sky, 0)
            self.do_mountains(mountains, 0)
            self.do_circuit(0)
            self.display.place_sprite(stefan.sprite, stefan.x, stefan.y)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_UP] == 1:
                        wait_for_start = False
            time.sleep(0.1)
            self.display.show()

        pygame.mixer.music.load('sensorland/sound/theme.mp3')
        pygame.mixer.music.play(-1, 0.0)

        #Execute the different levelz
        alive = self.do_level(level_id=0)
        if alive:
            alive = self.do_level(level_id=1)

        time.sleep(1)
        self.display.clear_screen()
        score_image = img.imread(os.path.join(self.path, 'images/high_score.png'))
        score_image = np.transpose(score_image[:, :, :3], (1, 0, 2)) * 255
        self.display.fade_to_image(score_image)
        self.display.write_string("HIGH SCORE", 13, 5, [236, 173, 42], background=None)
        leader_board.fg_color = [0, 255, 255]
        leader_board.bg_color = None
        leader_board.run_leader_board(self.score, self.display, self.input_control)
        time.sleep(1)
        #todo wait for keypressed
        time.sleep(3.01)
        pygame.mixer.music.pause()
