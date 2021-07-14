import numpy as np
from random import *


class Board:
    """
    A class to represent the tetris board
    """

    def __init__(self, x_size, y_size):
        self.field = np.zeros((x_size, y_size))
        self.back_ground = 0

    def point_in_field(self, x, y):
        """Check that x,y is in field

        :param x: x-position
        :param y: y-position
        :return: True/False
        """
        return 0 <= x < self.field.shape[0] and 0 <= y < self.field.shape[1]

    def clear_element(self, x, y):
        """ Remove Element from board

        :param x: x-position
        :param y: y-position
        :return:
        """
        if self.point_in_field(x, y):
            self.field[x, y] = self.back_ground

    def set_element(self, x, y, index):
        """ Set Element on board

        :param x: x-position
        :param y: y-position
        :param index: value
        :return:
        """
        if self.point_in_field(x, y):
            self.field[x, y] = index

    def position_is_free(self, x, y):
        """Check if the position is free

        :param x: x-position
        :param y: y-position
        :return: True / False
        """
        if self.point_in_field(x, y):
            return self.field[x, y] == self.back_ground
        else:
            if 0 <= x < self.field.shape[0] and y < self.field.shape[1]:
                return True
        return False

    def erase_lines(self, lines):
        """Erase the lines

        :param lines: lines to be removed from the field
        :return:
        """
        for line_id in lines:
            self.field[:, 1:line_id + 1] = self.field[:, :line_id]

    def line_is_complete(self, y):
        """Check if line y is complete

        :param y: line index
        :return: True id complete
        """
        line_complete = True
        for x in range(self.field.shape[0]):
            if self.field[x, y] == self.back_ground:
                line_complete = False
        return line_complete

    def get_complete_lines(self):
        """get list of complete lines

        :return: list of complete lines
        """
        line_ids = []
        for y in range(self.field.shape[1]):
            if self.line_is_complete(y):
                line_ids.append(y)
        return line_ids


class Rock:
    """
    A class to represent the tetris elements. It is called "Rock", because I expect
    it to Rock :-)
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rotation_step = 0

    def set_position(self, x, y):
        """Set position of Rock

        :param x:
        :param y:
        :return:
        """
        self.x = x
        self.y = y

    def remove_from_board(self, game_board):
        """Remove the Rock from the board

        :param game_board:
        :return:
        """
        for offset in self.offsets:
            game_board.clear_element(offset[0] + self.x, offset[1] + self.y)

    def place_on_board(self, game_board):
        """Place the Rock on the board

        :param game_board:
        :return:
        """
        can_be_placed = True
        for offset, ind in zip(self.offsets, self.texture):
            if not game_board.position_is_free(offset[0] + self.x, offset[1] + self.y):
                can_be_placed = False
        if can_be_placed:
            for offset, ind in zip(self.offsets, self.texture):
                game_board.set_element(offset[0] + self.x, offset[1] + self.y, ind)
        return can_be_placed

    def move(self, delta_x, delta_y, game_board):
        """Move Rock

        :param game_board:
        :return: True / False
        """
        self.remove_from_board(game_board)
        move_is_ok = True
        for offset in self.offsets:
            if not game_board.position_is_free(self.x + delta_x + offset[0], self.y + delta_y + offset[1]):
                move_is_ok = False
        if move_is_ok:
            self.x = self.x + delta_x
            self.y = self.y + delta_y
        self.place_on_board(game_board)
        return move_is_ok

    def move_horizontal_to(self, x_pos_absolute, game_board):
        """Move the rock absolute in the horizotnal layer

        :param x_pos_absolute: Absolute x-position
        :param game_board:
        :return:
        """
        delta = 1
        if x_pos_absolute < self.x:
            delta = -1
        move_is_ok = True
        while x_pos_absolute != self.x and move_is_ok:
            if delta>0:
                move_is_ok = self.move_right(game_board)
            else:
                move_is_ok = self.move_left(game_board)
        return move_is_ok

    def move_vertical_to(self, y_pos_absolute, game_board):
        """Move the rock absolute in the vertical layer

        :param y_pos_absolute: Absolute y-position
        :param game_board:
        :return:
        """
        move_is_ok = True
        while y_pos_absolute != self.y and move_is_ok:
            move_is_ok = self.move_down(game_board)
        return move_is_ok
    def move_left(self, game_board):
        """Move Rock one element to the left

        :param game_board:
        :return:
        """
        return self.move(-1, 0, game_board)

    def move_right(self, game_board):
        """Move Rock one element to the left

        :param game_board:
        :return:
        """
        return self.move(1, 0, game_board)

    def move_down(self, game_board):
        """Move Rock one element to the left

        :param game_board:
        :return:
        """
        return self.move(0, 1, game_board)

    def rotate(self, game_board):
        """Rotation of a stone in 90° steps

        :param game_board: the game board
        :return:
        """
        self.remove_from_board(game_board)
        self.rotation_step = (self.rotation_step + 1) % 4
        if self.rotation_step == 0:
            if self.check_offsets(self.offsets_0, game_board):
                self.offsets = self.offsets_0.copy()
        elif self.rotation_step == 1:
            if self.check_offsets(self.offsets_1, game_board):
                self.offsets = self.offsets_1.copy()
        elif self.rotation_step == 2:
            if self.check_offsets(self.offsets_2, game_board):
                self.offsets = self.offsets_2.copy()
        else:
            if self.check_offsets(self.offsets_3, game_board):
                self.offsets = self.offsets_3.copy()
        self.place_on_board(game_board)

    def check_offsets(self, offsets, game_board):
        """Check if the offsets are ok == not occupies

        :param offsets: offsets
        :return:
        """
        move_is_ok = True
        for offset in offsets:
            if not game_board.position_is_free(self.x + offset[0], self.y + offset[1]):
                move_is_ok = False
        return move_is_ok


class TetrisOscar(Rock):
    """
    A class to handle the O-Block (2x2)
    """

    def __init__(self, x, y):
        self.offsets = [[0, 0], [1, 0], [1, 1], [0, 1]]
        self.offsets_0 = [[1, 0], [1, 1], [0, 1], [0, 0]]
        self.offsets_1 = [[1, 1], [0, 1], [0, 0], [1, 0]]
        self.offsets_2 = [[0, 1], [0, 0], [1, 0], [1, 1]]
        self.offsets_3 = [[0, 0], [1, 0], [1, 1], [0, 1]]
        self.texture = [5, 5, 5, 5]
        super().__init__(x, y)


class TetrisIndia(Rock):
    """
    A class to handle the I-Block (4x1)
    """

    def __init__(self, x, y):
        self.offsets = [[-1, 0], [0, 0], [1, 0], [2, 0]]
        self.offsets_0 = [[-1, 0], [0, 0], [1, 0], [2, 0]]
        self.offsets_1 = [[0, -3], [0, -2], [0, -1], [0, 0]]
        self.offsets_2 = [[2, 0], [1, 0], [0, 0], [-1, 0]]
        self.offsets_3 = [[0, 0], [0, -1], [0, -2], [0, -3]]
        self.texture = [3, 3, 3, 3]
        super().__init__(x, y)


class TetrisAlpha(Rock):
    """
    A class to handle the A-Block
    """

    def __init__(self, x, y):
        self.offsets = [[0, 0], [-1, 1], [0, 1], [1, 1]]
        self.offsets_0 = [[0, 0], [-1, 1], [0, 1], [1, 1]]
        self.offsets_1 = [[0, 0], [1, 1], [1, 0], [1, -1]]
        self.offsets_2 = [[0, 0], [-1, -1], [0, -1], [1, -1]]
        self.offsets_3 = [[0, 0], [-1, 1], [-1, 0], [-1, -1]]
        self.texture = [4, 4, 4, 4]
        super().__init__(x, y)


class TetrisJuliett(Rock):
    """
    A class to handle the J-Block
    """

    def __init__(self, x, y):
        self.offsets = [[0, 0], [0, 1], [0, 2], [-1, 2]]
        self.offsets_0 = [[0, 0], [0, 1], [0, 2], [-1, 2]]
        self.offsets_1 = [[-1, 1], [0, 1], [1, 1], [1, 2]]
        self.offsets_2 = [[0, 0], [-1, 0], [-1, 1], [-1, 2]]
        self.offsets_3 = [[-1, 1], [-1, 2], [0, 2], [1, 2]]
        self.texture = [1, 1, 1, 1]
        super().__init__(x, y)


class TetrisLima(Rock):
    """
    A class to handle the L-Block
    """

    def __init__(self, x, y):
        self.offsets = [[0, 0], [0, 1], [0, 2], [1, 2]]
        self.offsets_0 = [[0, 0], [0, 1], [0, 2], [1, 2]]
        self.offsets_1 = [[-1, 2], [0, 2], [1, 2], [1, 1]]
        self.offsets_2 = [[0, 0], [1, 0], [1, 1], [1, 2]]
        self.offsets_3 = [[-1, 2], [-1, 1], [0, 1], [1, 1]]
        self.texture = [6, 6, 6, 6]
        super().__init__(x, y)


class TetrisSierra(Rock):
    """
    A class to handle the S-Block
    """

    def __init__(self, x, y):
        self.offsets = [[0, 0], [0, 1], [1, 1], [1, 2]]
        self.offsets_0 = [[0, 0], [0, 1], [1, 1], [1, 2]]
        self.offsets_1 = [[0, 1], [1, 1], [0, 2], [-1, 2]]
        self.offsets_2 = [[1, 2], [1, 1], [0, 1], [0, 0]]
        self.offsets_3 = [[-1, 2], [0, 2], [1, 1], [0, 1]]
        self.texture = [2, 2, 2, 2]
        super().__init__(x, y)


class TetrisZulu(Rock):
    """
    A class to handle the Z-Block
    """

    def __init__(self, x, y):
        self.offsets = [[0, 0], [0, 1], [-1, 1], [-1, 2]]
        self.offsets_0 = [[0, 0], [0, 1], [-1, 1], [-1, 2]]
        self.offsets_1 = [[0, 1], [-1, 1], [0, 2], [1, 2]]
        self.offsets_2 = [[-1, 2], [-1, 1], [0, 1], [0, 0]]
        self.offsets_3 = [[1, 2], [0, 2], [-1, 1], [0, 1]]
        self.texture = [7, 7, 7, 7]
        super().__init__(x, y)


def get_random_block():
    """get a random Teris block

    :return: Tetris block
    """
    block_id = randint(0, 6)
    if block_id == 0:
        return TetrisOscar(2, 1)
    elif block_id == 1:
        return TetrisIndia(2, 1)
    elif block_id == 2:
        return TetrisAlpha(2, 1)
    elif block_id == 3:
        return TetrisJuliett(2, 1)
    elif block_id == 4:
        return TetrisLima(2, 1)
    elif block_id == 5:
        return TetrisSierra(2, 1)
    else:
        return TetrisZulu(2, 1)
