import pygame
from game.tetris import *
from game.textures import *
from display.display import *
import matplotlib.image as img
import time

# TODO: Ending screens 1, 2 and 3
# TODO: Sound
# TODO: Proper class to handle the control
# TODO: Rotation at the wall
# TODO: Play again option
# TODO: Score for moving the block downwards fast

COLOR = COLOR_MAPS[0]

#Anchor of the board
GAME_BOARD_X = 4
GAME_BOARD_Y = 1


def show_splash_screen():
    # reading png image file
    im = img.imread('images/logo_background.png')
    image = np.transpose(im[:, :, :3], (1, 0, 2)) * 255
    screen.fade_to_image(image)
    im = img.imread('images/logo.png')
    image = np.transpose(im[:, :, :3], (1, 0, 2)) * 255
    screen.fade_to_image(image)
    time.sleep(2)
    screen.write_string("PRESS KEY", 10, 45)
    screen.show()
    running = True
    while running:
        pygame.time.delay(100)
        for eventr in pygame.event.get():
            if eventr.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and eventr.type == pygame.KEYDOWN:
            running = False
        if keys[pygame.K_RIGHT] and eventr.type == pygame.KEYDOWN:
            running = False
        if keys[pygame.K_UP] and eventr.type == pygame.KEYDOWN:
            running = False
        if keys[pygame.K_DOWN] and eventr.type == pygame.KEYDOWN:
            running = False
    screen.clear_screen()
    screen.show()


def display_board(board, screen, offset_x, offset_y):
    """Display the game board on the screen

    :param board: the gameboard
    :param screen: the display handler
    :param offset_x: anchor x of the display
    :param offset_y: anchor y of the display
    """
    #Color the border
    color_border = [50, 50, 50]
    scale = 3
    for x in range(board.field.shape[0]*scale+2):
        screen.set_pixel(x + offset_x, offset_y, color_border)
        screen.set_pixel(x + offset_x, offset_y+board.field.shape[1]*scale+1, color_border)
    for y in range(board.field.shape[1]*scale+2):
        screen.set_pixel(offset_x, y + offset_y, color_border)
        screen.set_pixel(offset_x+board.field.shape[0]*scale+1, y + offset_y, color_border)

    for xb in range(board.field.shape[0]):
        for yb in range(board.field.shape[1]):
            x = xb * scale + offset_x + 1
            y = yb * scale + offset_y + 1
            color = COLOR[board.field[xb, yb]]
            screen.set_pixel(x + 0, y, color)
            screen.set_pixel(x + 1, y, color)
            screen.set_pixel(x + 2, y, color)
            screen.set_pixel(x + 0, y + 1, color)
            screen.set_pixel(x + 1, y + 1, color)
            screen.set_pixel(x + 2, y + 1, color)
            screen.set_pixel(x + 0, y + 2, color)
            screen.set_pixel(x + 1, y + 2, color)
            screen.set_pixel(x + 2, y + 2, color)
    screen.show()


def number_to_string(n):
    """Convert number to string

    :param n:
    :return:
    """
    return "{:6d}".format(n)


def score_from_lines(n):
    if n == 1:
        return 100
    if n == 2:
        return 250
    if n == 3:
        return 500
    if n == 4:
        return 800
    return 0

def get_next_char(character):
    i = ord(character)
    i += 1
    if i == 91:
        i = 48
    if i == 33:
        i = 65
    if i == 58:
        i = 32
    return chr(i)

def get_prev_char(character):
    i = ord(character)
    i -= 1
    if i == 64:
        i = 32
    if i == 47:
        i = 90
    if i == 31:
        i = 57
    return chr(i)

def delete_lines_animation(game_board, line_ids, width):
    for x in range(width):
        for y in line_ids:
            game_board.clear_element(x, y)
        display_board(game_board, screen, GAME_BOARD_X, GAME_BOARD_Y)
        time.sleep(0.02)

def fill_board_animation(game_board, screen):
    for y in range(game_board.field.shape[1]):
        for x in range(game_board.field.shape[0]):
            col_ind = int(8-abs((y % 14) - 7))
            game_board.set_element(x, game_board.field.shape[1]-(y+1), col_ind)
        display_board(game_board, screen, GAME_BOARD_X, GAME_BOARD_Y)
        time.sleep(0.05)


def load_leader_board(file_name):
    """load the leader board from the file name

    :param file_name:
    :return:
    """
    leader_board = []
    with open(file_name, "r") as file:
        for line in file:
            parts = line.split(':')
            leader_board.append(['{:.3s}'.format(parts[0]), int(parts[1])])
    return leader_board


def save_leader_board(leader_board, file_name):
    """Save the leader board to the txt file

    :param high_score: current leader board
    :param file_name: file name of the leader board
    :return:
    """
    with open(file_name, "w") as file:
        for leader in leader_board:
            file.write("{:s}:{:d}\n".format(leader[0], leader[1]))


def update_leader_board(score, leader_board):
    """Update the high score with the new score

    :param score: new score
    :param leader_board: leader board
    :return:
    """
    update_index = -1
    for index, leader in enumerate(leader_board):
        if leader[1] < score:
            update_index = index
            break
    if update_index >= 0:
        leader_board.insert(update_index, ['   ', score])
        leader_board.pop(-1)
        return update_index
    return update_index


def run_leader_board(score):
    """ Run the leader bord part

    :param score: the score from the game
    :return:
    """
    #1. Load file
    HIGH_SCORE_FILE = "records.txt"
    leader_board = load_leader_board(HIGH_SCORE_FILE)
    #2. update leader board
    index_board = update_leader_board(score, leader_board)
    #3. show the current leader board
    screen.clear_screen()
    im = img.imread('images/high_score.png')
    image = np.transpose(im[:, :, :3], (1, 0, 2)) * 255
    screen.fade_to_image(image)
    screen.write_string("HIGH SCORE", 13, 10, [50, 50, 255])
    LEADER_BOARD_X = 10
    for index, leader in enumerate(leader_board):
        message = '{:3s} {:6d}'.format(leader[0], leader[1])
        screen.write_string(message, LEADER_BOARD_X, 18 + index * 8)
    screen.show()
    #4. Edit mode if score changed
    if index_board >= 0:
        entry_x = 0
        running = True
        iteration = 0
        while running:
            pygame.time.delay(100)
            char_name = list(leader_board[index_board][0])
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT] and event.type == pygame.KEYDOWN:
                    if entry_x > 0:
                        entry_x -= 1
                if keys[pygame.K_RIGHT] and event.type == pygame.KEYDOWN:
                    if entry_x >= 2:
                        running = False
                        iteration = 1
                    if entry_x < 2:
                        entry_x += 1
                if keys[pygame.K_UP] and event.type == pygame.KEYDOWN:
                    char_name[entry_x] = get_next_char(char_name[entry_x])
                if keys[pygame.K_DOWN] and event.type == pygame.KEYDOWN:
                    char_name[entry_x] = get_prev_char(char_name[entry_x])
            leader_board[index_board][0] = ''.join(char_name)
            iteration = iteration + 1
            # Print name
            if iteration % 2 == 0:
                screen.write_string(leader_board[index_board][0], LEADER_BOARD_X, 18 + index_board * 8)
            else:
                screen.write_string('_', LEADER_BOARD_X + 4 * entry_x, 18 + index_board * 8)
            screen.show()
    #5. Save file
    save_leader_board(leader_board, HIGH_SCORE_FILE)
    time.sleep(5)


DISPLAY_WITH = 64
DISPLAY_HEIGHT = 64
screen = Display(DISPLAY_WITH, DISPLAY_HEIGHT)
pygame.init()
pygame.display.set_caption('TeTris')
show_splash_screen()

running = True
score = 0
lines = 0
level = 0
game_board = Board(10, 20)
preview = Board(6, 5)
POS_X_SCORE_TEXT = 43
POS_Y_SCORE_TEXT = 20
POS_X_SCORE_NUMBER = POS_X_SCORE_TEXT-4
POS_Y_SCORE_NUMBER = POS_Y_SCORE_TEXT + 6

POS_X_LINE_TEXT = POS_X_SCORE_TEXT
POS_Y_LINE_TEXT = POS_Y_SCORE_NUMBER + 10
POS_X_LINE_NUMBER = POS_X_SCORE_TEXT-4
POS_Y_LINE_NUMBER = POS_Y_LINE_TEXT + 6

POS_X_LEVEL_TEXT = POS_X_SCORE_TEXT
POS_Y_LEVEL_TEXT = POS_Y_LINE_NUMBER + 10
POS_X_LEVEL_NUMBER = POS_X_SCORE_TEXT-4
POS_Y_LEVEL_NUMBER = POS_Y_LEVEL_TEXT + 6

screen.write_string("SCORE", POS_X_SCORE_TEXT, POS_Y_SCORE_TEXT)
screen.write_string("LINES", POS_X_LINE_TEXT, POS_Y_LINE_TEXT)
screen.write_string("LEVEL", POS_X_LEVEL_TEXT, POS_Y_LEVEL_TEXT)

score_string = number_to_string(score)
screen.write_string(score_string, POS_X_SCORE_NUMBER, POS_Y_SCORE_NUMBER)
level_string = number_to_string(level)
screen.write_string(level_string, POS_X_LEVEL_NUMBER, POS_Y_LEVEL_NUMBER)
lines_string = number_to_string(lines)
screen.write_string(lines_string, POS_X_LINE_NUMBER, POS_Y_LINE_NUMBER)

block_current = get_random_block()
block_next = get_random_block()
block_current.set_position(5, 0)
block_current.place_on_board(game_board)
block_next.place_on_board(preview)
iterations = 0
while running:
    pygame.time.delay(10)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and event.type == pygame.KEYDOWN:
            block_current.move_left(game_board)
        if keys[pygame.K_RIGHT] and event.type == pygame.KEYDOWN:
            block_current.move_right(game_board)
        if keys[pygame.K_UP] and event.type == pygame.KEYDOWN:
            block_current.rotate(game_board)
        if keys[pygame.K_DOWN] and event.type == pygame.KEYDOWN:
            block_current.move_down(game_board)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_DOWN]:
        block_current.move_down(game_board)
    display_board(game_board, screen, GAME_BOARD_X, GAME_BOARD_Y)
    display_board(preview, screen, 41, 1)
    iterations = (iterations + 1) % (20 - min(19, level))
    ok = True
    if iterations == 0:
        if not block_current.move_down(game_board):
            complete_lines = game_board.get_complete_lines()
            if len(complete_lines):
                #animate the deletion of the lines
                delete_lines_animation(game_board, complete_lines, 10)
                #delete the lines
                game_board.erase_lines(complete_lines)
            new_lines = len(complete_lines)
            lines = lines + new_lines
            score = score + score_from_lines(new_lines)
            level = int(lines / 10)
            COLOR = COLOR_MAPS[level % len(COLOR_MAPS)]
            block_next.remove_from_board(preview)
            block_current = block_next
            block_current.set_position(5, 0)
            ok = block_current.place_on_board(game_board)
            block_next = get_random_block()
            block_next.place_on_board(preview)
            # Update score etc:
            score_string = number_to_string(score)
            screen.write_string(score_string, POS_X_SCORE_NUMBER, POS_Y_SCORE_NUMBER)
            level_string = number_to_string(level)
            screen.write_string(level_string, POS_X_LEVEL_NUMBER, POS_Y_LEVEL_NUMBER)
            lines_string = number_to_string(lines)
            screen.write_string(lines_string, POS_X_LINE_NUMBER, POS_Y_LINE_NUMBER)
    if not ok:
        fill_board_animation(game_board, screen)
        running = False
        screen.fill_rectangle(11, 30, 20, 36, [0, 0, 0])
        screen.write_string("GAME", 13, 22)
        screen.write_string("OVER", 13, 29)
        screen.show()
        time.sleep(5)
# high score
screen.clear_screen()
#im = img.imread('images/game_over.png')
#image = np.transpose(im[:, :, :3], (1, 0, 2)) * 255
#screen.fade_to_image(image)
#time.sleep(1)
run_leader_board(score)
pygame.quit()
