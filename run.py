# Top Level Menu of the Arcade
import matplotlib.image as img
import numpy as np
from display.display import *
from controls.input_control import *
# Import the games
from sensorland.sensorland import SensorLandGame
from tetris.tetris import Tetris
from FlexChain.FlexChain import FlexChainGame
import time

DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 64

print("INput control ok")
im_arrow_left = img.imread('images/left_arrow.png')
im_arrow_left = np.transpose(im_arrow_left, (1, 0, 2)) * 255

im_arrow_right = img.imread('images/right_arrow.png')
im_arrow_right = np.transpose(im_arrow_right, (1, 0, 2)) * 255

screen = Display(DISPLAY_WIDTH, DISPLAY_HEIGHT, display_type=DISPLAY_TYPE_BOTH)

pygame.init()
input_control = InputControl(input_type=INPUT_TYPE_BOTH)
pygame.display.set_caption('Stefan')

awesome_games = [SensorLandGame(), Tetris(), FlexChainGame()]

# Do the selection menu only left and right are required
game_index = 0
raw_index = 0
iterations = 0
screen.show()
show_arrows = True
running = True
while running:
    iterations += 1
    selected_game = awesome_games[game_index]
    screen.show_image(selected_game.get_title_image())
    if iterations % 5 == 0:
        show_arrows = not show_arrows
    if show_arrows:
        screen.place_sprite(im_arrow_left, 0, 25)
        screen.place_sprite(im_arrow_right, 53, 25)
    screen.show()
    time.sleep(0.1)
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    if input_control.flex_chain:
        position = input_control.get_xy_position()
        if 0 <= position[0] <= 19:
            delta = (position[0]-9.5)/15
            raw_index += delta
            if raw_index < 0:
                raw_index = len(awesome_games) - 0.0001
            if raw_index > len(awesome_games) - 0.0001:
                raw_index = 0
        game_index = int(raw_index)
        if 0 <= position[1] <= 3 or 16 <= position[1] <= 19 or input_control.button_a:
            selected_game.run_game(screen, input_control=input_control)

    if input_control.keyboard:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game_index -= 1
                    if game_index < 0:
                        game_index = len(awesome_games) - 1
                if event.key == pygame.K_RIGHT:
                    game_index += 1
                    if game_index >= len(awesome_games):
                        game_index = 0
                if event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    running = False
                
                raw_index = game_index
                if event.key == pygame.K_DOWN or event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                    time.sleep(0.2)
                    selected_game.run_game(screen, input_control=input_control)
