# Stefan in Sensorland
import matplotlib.image as img
import numpy as np
import os
import pygame
from tetris.game.tetris_engine import *
from tetris.game.textures import *
from display.display import *
from leaderboard.leader_board import *
from controls.input_control import *
from shutdown.shutdown import ShutDown
import time

#Anchor of the board
GAME_BOARD_X = 4
GAME_BOARD_Y = 1
POS_X_TEXT = 39
POS_Y_TEXT = 20

def number_to_string(n):
    """Convert number to string

    :param n:
    :return:
    """
    return "{:6d}".format(n)


def score_from_lines(n):
    """Compute score from deleted lines

    :param n: number of deleted lines
    :return:
    """
    if n == 1:
        return 100
    if n == 2:
        return 250
    if n == 3:
        return 500
    if n == 4:
        return 800
    return 0


class Tetris:

    def __init__(self):
        self.path = os.path.dirname(__file__)
        self.display = 0
        self.input_control = 0
        self.color_map = COLOR_MAPS[0]
        self.sound_rotate = pygame.mixer.Sound('tetris/sound/rotation.wav')
        self.sound_landing = pygame.mixer.Sound('tetris/sound/block_landed.wav')
        self.sound_game_over = pygame.mixer.Sound('tetris/sound/game_over.wav')
        self.sound_line_clear = pygame.mixer.Sound('tetris/sound/line_clear.wav')
        self.sound_four_lines_clear = pygame.mixer.Sound('tetris/sound/line_clear.wav')

    def get_title_image(self):
        """Get the iconic image of the game

        """
        image = img.imread(os.path.join(self.path, 'images/logo.png'))
        return np.transpose(image[:, :, :3], (1, 0, 2)) * 255

    def run_game(self, display, input_control):
        """Run the Game

        """
        leader_board = LeaderBoard('tetris/records.txt')
        self.display = display
        self.input_control = input_control
        score = 0
        lines = 0
        level = 0
        self.color_map = COLOR_MAPS[0]
        game_board = Board(10, 20)
        preview = Board(6, 5)
        self.display.clear_screen([0, 0, 0])

        pygame.mixer.music.load('tetris/sound/theme.mp3')
        pygame.mixer.music.play(-1, 0.0)

        block_current = get_random_block()
        block_next = get_random_block()
        block_current.set_position(5, 0)
        block_current.place_on_board(game_board)
        block_next.place_on_board(preview)
        iterations = 0
        running = True
        enable_rotation = True
        while running:
            time.sleep(0.005)
            if input_control.flex_chain:
                position = input_control.get_xy_position()
                if position[0] >= 0:
                    target_x = round((position[0]-3) * 10 / 16)  # This is ugly !!!
                    target_x = max(min(target_x, 9), 0)
                    block_current.move_horizontal_to(target_x, game_board)
                if position[1] >= 16:
                    block_current.move_down(game_board)
                if 0 <= position[1] <= 7 and enable_rotation:
                    pygame.mixer.Sound.play(self.sound_rotate)
                    block_current.rotate(game_board)
                    enable_rotation = False
                if 7 < position[1] or position[1] < 0:
                    enable_rotation = True
                if input_control.button_a_pressed == 1:
                    input_control.button_a_pressed = 0
                    block_current.move_vertical_to(20, game_board)
                    iterations = 0
                if input_control.button_shutdown_pressed_long:
                    shut = ShutDown()
                    shut.run_game(self.display, self.input_control)
                if input_control.button_b_pressed:
                    return

            events = pygame.event.get()
            if input_control.keyboard:
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            block_current.move_left(game_board)
                        elif event.key == pygame.K_RIGHT:
                            block_current.move_right(game_board)
                        elif event.key == pygame.K_UP:
                            pygame.mixer.Sound.play(self.sound_rotate)
                            block_current.rotate(game_board)
                        elif event.key == pygame.K_DOWN:
                            block_current.move_down(game_board)
                        elif event.key == pygame.K_SPACE:
                            block_current.move_vertical_to(20, game_board)
                            iterations = 0
                        elif event.key == pygame.K_q:
                            return
                        elif event.key == pygame.K_ESCAPE:
                            shut = ShutDown()
                            shut.run_game(self.display, self.input_control)

            self.display_game_board(game_board, GAME_BOARD_X, GAME_BOARD_Y)
            self.display_game_board(preview, 41, 1)
            ok = True
            if iterations == 0:
                enable_rotation = True
                if not block_current.move_down(game_board):
                    pygame.mixer.Sound.play(self.sound_landing)
                    complete_lines = game_board.get_complete_lines()
                    if len(complete_lines):
                        if len(complete_lines) == 4:
                            pygame.mixer.Sound.play(self.sound_four_lines_clear)
                        else:
                            pygame.mixer.Sound.play(self.sound_line_clear)
                        # animate the deletion of the lines
                        self.delete_lines_animation(game_board, complete_lines)
                        # delete the lines
                        game_board.erase_lines(complete_lines)
                    new_lines = len(complete_lines)
                    lines = lines + new_lines
                    score = score + score_from_lines(new_lines)
                    level = int(lines / 10)
                    self.color_map = COLOR_MAPS[level % len(COLOR_MAPS)]
                    block_next.remove_from_board(preview)
                    block_current = block_next
                    block_current.set_position(5, 0)
                    ok = block_current.place_on_board(game_board)
                    block_next = get_random_block()
                    block_next.place_on_board(preview)
                # Update score etc:
                self.display_score_etc(score, lines, level)
            self.display.show()
            iterations = (iterations + 1) % (20 - min(19, level*2))
            if not ok:
                pygame.mixer.music.pause()
                pygame.mixer.Sound.play(self.sound_game_over)
                self.fill_board_animation(game_board)
                running = False
                self.display.fill_rectangle(11, 30, 20, 36, [0, 0, 0])
                self.display.write_string("GAME", 13, 22)
                self.display.write_string("OVER", 13, 29)
                self.display.show()
                time.sleep(3)
        # high score
        pygame.mixer.music.load('tetris/sound/highscore.mp3')
        pygame.mixer.music.play(-1, 0.0)
        self.display.clear_screen()
        image = img.imread(os.path.join(self.path, 'images/high_score.png'))
        image = np.transpose(image[:, :, :3], (1, 0, 2)) * 255
        self.display.fade_to_image(image)
        self.display.write_string("HIGH SCORE", 13, 10, [50, 50, 255])
        leader_board.run_leader_board(score, self.display, self.input_control)
        time.sleep(0.5)
        wait_for_key_pressed = True
        while wait_for_key_pressed:
            events = pygame.event.get()
            if input_control.keyboard:
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            wait_for_key_pressed = False
                        if event.key == pygame.K_RIGHT:
                            wait_for_key_pressed = False
                        if event.key == pygame.K_UP:
                            wait_for_key_pressed = False
                        if event.key == pygame.K_DOWN:
                            wait_for_key_pressed = False
                        if event.key == pygame.K_SPACE:
                            wait_for_key_pressed = False
            
            if input_control.flex_chain:
                if input_control.there_is_any_detection():
                    wait_for_key_pressed = False
            time.sleep(0.1)
        pygame.mixer.music.pause()


    def display_game_board(self, game_board, offset_x, offset_y):
        """Display the game board on the screen

        :param board: the gameboard
        :param screen: the display handler
        :param offset_x: anchor x of the display
        :param offset_y: anchor y of the display
        """
        #Color the border
        color_border = [50, 50, 50]
        scale = 3
        self.display.draw_rectangle(offset_x, offset_x + game_board.field.shape[0]*scale+1,
                                    offset_y, offset_y + game_board.field.shape[1]*scale+1, color_border)

        for xb in range(game_board.field.shape[0]):
            for yb in range(game_board.field.shape[1]):
                x = xb * scale + offset_x + 1
                y = yb * scale + offset_y + 1
                color = self.color_map[game_board.field[xb, yb]]
                self.display.fill_rectangle(x, x+2, y, y+2, color)

    def display_score_etc(self, score, lines, level):
        """Display the score, lines and levels

        :param score:
        :param lines:
        :param level:
        :return:
        """
        self.display.write_string("SCORE", POS_X_TEXT+4, POS_Y_TEXT)
        self.display.write_string(number_to_string(score), POS_X_TEXT, POS_Y_TEXT + 6)
        self.display.write_string("LINES", POS_X_TEXT+4, POS_Y_TEXT+13)
        self.display.write_string(number_to_string(lines), POS_X_TEXT, POS_Y_TEXT + 19)
        self.display.write_string("LEVEL", POS_X_TEXT+4, POS_Y_TEXT+26)
        self.display.write_string(number_to_string(level), POS_X_TEXT, POS_Y_TEXT + 32)

    def delete_lines_animation(self, game_board, line_ids):
        """Animate the cleare lines by disappearing

        :param game_board: the game board
        :param line_ids: the lines to be erased
        :return:
        """
        for x in range(game_board.field.shape[0]):
            for y in line_ids:
                game_board.clear_element(x, y)
            self.display_game_board(game_board, GAME_BOARD_X, GAME_BOARD_Y)
            time.sleep(0.02)

    def fill_board_animation(self, game_board):
        """Fill the board with the current color pallette

        :param game_board: the game board
        :return:
        """
        for y in range(game_board.field.shape[1]):
            for x in range(game_board.field.shape[0]):
                col_ind = int(8 - abs((y % 14) - 7))
                game_board.set_element(x, game_board.field.shape[1] - (y + 1), col_ind)
            self.display_game_board(game_board, GAME_BOARD_X, GAME_BOARD_Y)
            self.display.show()
            time.sleep(0.05)

