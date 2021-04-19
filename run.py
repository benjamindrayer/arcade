#Top Level Menu of the Arcade
import matplotlib.image as img
import numpy as np
from display.display import *
from controls.input_control import *
#Import the games
from sensorland.sensorland import SensorLandGame
from tetris.tetris import Tetris
from FlexChain.FlexChain import FlexChainGame

#TODO true alpha in images
#TODO splash screen
#TODO input controls
#TODO tetris: play again
#TODO ssil: everything :-)
#

DISPLAY_WITH = 64
DISPLAY_HEIGHT = 64

input_control = InputControl()

im_arrow_left = img.imread('images/left_arrow.png')
im_arrow_left = np.transpose(im_arrow_left, (1, 0, 2)) * 255

im_arrow_right = img.imread('images/right_arrow.png')
im_arrow_right = np.transpose(im_arrow_right, (1, 0, 2)) * 255

screen = Display(DISPLAY_WITH, DISPLAY_HEIGHT)
pygame.init()
pygame.display.set_caption('Stefan')

awesome_games = [SensorLandGame(), Tetris(), FlexChainGame()]

#Do the selection menu only left and right are required
game_index = 0
iterations = 0
screen.show()
show_arrows = True
#Init display
running = True
while running:
    iterations += 1
    selected_game = awesome_games[game_index]
    screen.show_image(selected_game.get_title_image())
    if iterations % 5 == 0:
        show_arrows = not show_arrows
    if show_arrows:
        screen.place_sprite(im_arrow_left, 0, 25)
        screen.place_sprite(im_arrow_right, 55, 25)
    screen.show()
    pygame.time.delay(100)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if input_control.left_key_pressed() == 1:
        game_index -= 1
        if game_index < 0:
            game_index = len(awesome_games) - 1

    if input_control.right_key_pressed() == 1:
        game_index += 1
        if game_index >= len(awesome_games):
            game_index = 0


    if input_control.up_key_pressed() == 1:
        selected_game.run_game(screen, input_control=input_control)
