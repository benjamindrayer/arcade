#class to handle the leaderboard
import os
import pygame
import time

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

class LeaderBoard:

    def __init__(self, file_name):
        self.file_name = file_name
        self.leader_board = self.load_leader_board()
        self.fg_color = [255, 255, 255]
        self.bg_color = [0, 0, 0]

    def run_leader_board(self, score, display, input_controls):
        """ Run the leader bord part

        :param score: the score from the game
        :return:
        """
        LEADER_BOARD_X = 10
        index_board = self.insert_score_in_leader_board(score)
        for index, leader in enumerate(self.leader_board):
            message = '{:3s} {:6d}'.format(leader[0], leader[1])
            display.write_string(message, LEADER_BOARD_X, 18 + index * 8, foreground=self.fg_color, background=self.bg_color)
        display.show()
        # 4. Edit mode if score changed
        if index_board >= 0:
            image_copy = display.image.copy()
            entry_x = 0
            running = True
            iteration = 0
            while running:
                pygame.time.delay(100)
                display.show_image(image_copy)
                char_name = list(self.leader_board[index_board][0])
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
                self.leader_board[index_board][0] = ''.join(char_name)
                iteration = iteration + 1
                # Print name
                if iteration % 2 == 0:
                    display.write_string(self.leader_board[index_board][0], LEADER_BOARD_X, 18 + index_board * 8, foreground=self.fg_color, background=self.bg_color)
                else:
                    display.write_string('_', LEADER_BOARD_X + 4 * entry_x, 18 + index_board * 8, foreground=self.fg_color, background=self.bg_color)
                display.show()
        # 5. Save file
        self.save_leader_board()
        time.sleep(5)

    def load_leader_board(self):
        """load the leader board
        :return:
        """
        leader_board = []
        with open(self.file_name, "r") as file:
            for line in file:
                parts = line.split(':')
                leader_board.append(['{:.3s}'.format(parts[0]), int(parts[1])])
        return leader_board

    def save_leader_board(self):
        """Save the leader board to the txt file

        :return:
        """
        with open(self.file_name, "w") as file:
            for leader in self.leader_board:
                file.write("{:s}:{:d}\n".format(leader[0], leader[1]))

    def insert_score_in_leader_board(self, score):
        """Update the high score with the new score

        :param score: new score
        :return:
        """
        update_index = -1
        for index, leader in enumerate(self.leader_board):
            if leader[1] < score:
                update_index = index
                break
        if update_index >= 0:
            self.leader_board.insert(update_index, ['   ', score])
            self.leader_board.pop(-1)
            return update_index
        return update_index