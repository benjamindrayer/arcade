#Class to control the inputs
import pygame
from threading import Thread

class InputControl:

    def __init__(self, input_type=0):
        if type == 0:
            pygame.init()
        self.up = 0
        self.down = 0
        self.left = 0
        self.right = 0
        self.input_type = input_type

    def r(self):
        x = Thread(target=self.check_input())
        x.daemon = True
        x.start()

    def left_key_pressed(self):
        if self.input_type == 0:
            keys = pygame.key.get_pressed()
            return keys[pygame.K_LEFT]

    def right_key_pressed(self):
        if self.input_type == 0:
            keys = pygame.key.get_pressed()
            return keys[pygame.K_RIGHT]

    def up_key_pressed(self):
        if self.input_type == 0:
            keys = pygame.key.get_pressed()
            return keys[pygame.K_UP]

    def down_key_pressed(self):
        if self.input_type == 0:
            keys = pygame.key.get_pressed()
            return keys[pygame.K_DOWN]

    def wait_for_keypressed(self):
        key_pressed = False
        while not key_pressed:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_DOWN] or keys[pygame.K_UP] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                        key_pressed = True
                        print(keys[pygame.K_DOWN], keys[pygame.K_UP], keys[pygame.K_LEFT], keys[pygame.K_RIGHT])

    def check_input(self):
        if self.input_type == 0:
            pygame.init()
        while True:
            if self.input_type == 0:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    self.left = 1
                else:
                    self.left = 0
                if keys[pygame.K_RIGHT]:
                    self.right = 1
                else:
                    self.right = 0
                if keys[pygame.K_UP]:
                    self.up = 1
                else:
                    self.up = 0
                if keys[pygame.K_DOWN]:
                    self.down = 1
                else:
                    self.down = 0
            print("a")
            pygame.time.delay(2000)
