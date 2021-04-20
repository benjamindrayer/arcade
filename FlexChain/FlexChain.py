from enum import Enum
import matplotlib.image as img
import numpy as np
import os
import time
import pygame
from random import randrange
from leaderboard.leader_board import *


class Dir(Enum):
    STOP = 0
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4
    CRASH = 5


class Pixel:
    def __init__(self, x, y, col):
        self.x = int(x)
        self.y = int(y)
        self.col = col


maxX = 64-1
maxY = 64-1
minX = 0
minY = 12
lengthToWin = (maxY-minY)*(maxX-minY)-1
debugMode = 1
startLength = 3
if debugMode >= 1:
    startLength = 198 #more cheats!
    lengthToWin = startLength+2 #cheat!



class FlexChainGame:
    def __init__(self):
        self.path = os.path.dirname(__file__)
        self.length = 0
        self.movementDir = Dir.STOP
        self.display = 0
        self.input_control = 0
        self.body = [Pixel(maxX / 2, maxY / 2, (0, 30, 255))]
        self.ApplePos = 0
        self.running = True
        self.colorBlue = 0
        self.minBlue = 0
        self.maxBlue = 0
        self.deltaBlue = 0
        self.leaderBoard = LeaderBoard('FlexChain/records.txt')
        self.reInit()

    def reInit(self):
        self.path = os.path.dirname(__file__)
        self.length = startLength
        self.movementDir = Dir.STOP
        self.display = 0
        self.input_control = 0
        self.body = [Pixel(maxX / 2, maxY / 2, (0, 30, 255))]
        self.ApplePos = 0
        self.running = True
        self.colorBlue = 240
        self.minBlue = 80
        self.maxBlue = 255
        self.deltaBlue = 10

        for i in range(1, self.length):
            self.body.append(Pixel(maxX / 2, maxY / 2 + i, (0, 30, 255)))

        if debugMode == 1: print("FlexChainGame set-up and ready to go")

    def drawBorder(self, color, show = False):
        self.colorBlue = self.colorBlue + self.deltaBlue
        if self.colorBlue > self.maxBlue:
            self.colorBlue = self.maxBlue
            self.deltaBlue = self.deltaBlue * -1
        elif self.colorBlue < self.minBlue:
            self.colorBlue = self.minBlue
            self.deltaBlue = self.deltaBlue * -1

        randomCol = False
        if color == (0, 0, 0): randomCol = True

        #print("blue:",self.colorBlue , " delta:", self.deltaBlue)
        self.display.write_string("FLEX CHAIN GAME", 1, 1, [0,int(150-self.colorBlue/2),self.colorBlue])
        if randomCol: color = (randrange(0, 255), randrange(0, 255), randrange(0, 255))
        self.display.write_string("SCORE:", 1, 7, color)
        if randomCol: color = (randrange(0, 255), randrange(0, 255), randrange(0, 255))
        self.display.write_string(str(self.length), 27, 7, color)

        for i in range(minX, maxX+1):
            if randomCol : color = (randrange(0, 255), randrange(0, 255), randrange(0, 255))
            self.display.fill_rectangle(i, i, minY, minY, color)
            if randomCol: color = (randrange(0, 255), randrange(0, 255), randrange(0, 255))
            self.display.fill_rectangle(i, i, maxY, maxY, color)
            if show == True: self.display.show()

        for i in range(minY, maxY):
            if randomCol : color = (randrange(0, 255), randrange(0, 255), randrange(0, 255))
            self.display.fill_rectangle(minX, minX, i, i, color)
            if randomCol: color = (randrange(0, 255), randrange(0, 255), randrange(0, 255))
            self.display.fill_rectangle(maxX, maxX, i, i, color)
            if show == True: self.display.show()

    def finishIt(self):
        self.display.clear_screen([32, 32, 32])
        self.drawBorder((0,0,0),True)
        self.leaderBoard.run_leader_board(self.length, self.display, self.input_control)


    def hitControl(self, x, y):
        if debugMode == 1: print("hitControl ", x, ",", y)
        if x <= minX or y <= minY or x >= maxX or y >= maxY:
            self.iAmDead()
            return

        for i in range(0, self.length):
            if x == self.body[i].x and y == self.body[i].y:
                self.iAmDead()
                print("hit body at [", i, "]", x, y)
                return

        if x == self.ApplePos.x and y == self.ApplePos.y:
            self.eatApple(x, y)

        self.body.insert(0, Pixel(x, y, (0, 30, 255)))
        self.body.pop()

    def eatApple(self, x, y):
        if debugMode == 1: print("yummy, apple!")
        self.length += 1
        self.body.insert(0, Pixel(x, y, (0, 255, 255)))
        if self.length == lengthToWin:
            self.iAmWinner()
        self.newApple()
        self.drawMe()

    def newApple(self):
        if debugMode == 1: print("new Apple...")
        newAppleNotFound = True
        while newAppleNotFound:
            hits = 0
            randX = randrange(minX+1,maxX-1)
            randY = randrange(minY+1,maxY-1)
            for i in range(0, self.length):
                if randX == self.body[i].x and randY == self.body[i].y:
                    hits = hits +1
            if hits == 0:
                newAppleNotFound = False
                self.ApplePos = Pixel(randX, randY, (255, 0, 0))
                if debugMode == 1: print("... done at ", randX, ",", randY)

    def move(self):
        curX = self.body[0].x
        curY = self.body[0].y

        newX = curX
        newY = curY

        if debugMode == 1: print("moving ", self.movementDir)
        if self.movementDir == Dir.UP:
            newY = curY + 1
        elif self.movementDir == Dir.DOWN:
            newY = curY - 1
        elif self.movementDir == Dir.RIGHT:
            newX = curX + 1
        elif self.movementDir == Dir.LEFT:
            newX = curX - 1
        elif self.movementDir == Dir.STOP:
            return
        # else:
        # self.running = False

        self.hitControl(newX, newY)

    def colorMe(self, color):
        for i in range(0, self.length):
            self.body[i].col = color
        self.drawBorder(color)

    def iAmWinner(self):
        self.colorMe((0, 255, 1))
        if debugMode == 1: print("winner")
        self.running = False
        self.drawMe()
        self.display.write_string("WINNER!", 20, 17, [50, 50, 255])
        self.display.show()
        time.sleep(2.0)
        for i in range(0, 64):
            g = i * 4
            if g > 255:
                g = 255
            self.display.clear_screen([0, g, 0])
            self.display.show()
            time.sleep(0.075)
        self.finishIt()

    def iAmDead(self):
        self.colorMe((255, 0, 0))
        self.running = False
        if debugMode == 1: print("crash at", self.body[0].x, ",", self.body[0].y)
        for i in range(0, self.length):
            if debugMode == 2: print("tail [", i, "]", self.body[i].x, ",", self.body[i].y)

        self.drawMe()
        self.display.write_string("s YOU DIED s", 10, 17, [255, 0, 5])
        self.display.show()
        time.sleep(2.0)
        for i in range(0, 64):
            r = i * 4
            if r > 255:
                r = 255
            self.display.clear_screen([r, 0, 0])
            self.display.show()
            time.sleep(0.075)
        self.finishIt()

    def drawMe(self):
        self.display.clear_screen([0, 0, 0])
        self.drawBorder((255, 255, 255))
        # apple
        self.display.fill_rectangle(self.ApplePos.x, self.ApplePos.x, self.ApplePos.y, self.ApplePos.y,
                                    self.ApplePos.col)

        # FlexChain
        for i in range(0, self.length):
            if debugMode == 2: print("drawing [", i, "]", self.body[i].x, ",", self.body[i].y, "(", self.body[i].col[0],
                                 ",", self.body[i].col[1], ",", self.body[i].col[2], ")")
            self.display.fill_rectangle(self.body[i].x, self.body[i].x, self.body[i].y, self.body[i].y,
                                        self.body[i].col)
        self.display.show()

    def get_title_image(self):
        """Get the iconic image of the game

        """
        image = img.imread(os.path.join(self.path, 'images/FlexChainLogo.png'))
        return np.transpose(image[:, :, :3], (1, 0, 2)) * 255

    def button_up(self):
        self.movementDir = Dir.UP

    def button_right(self):
        self.movementDir = Dir.RIGHT

    def button_down(self):
        self.movementDir = Dir.DOWN

    def button_lef(self):
        self.movementDir = Dir.LEFT

    def tick(self):
        self.move()

    def run_game(self, display, input_control):
        self.reInit()
        self.display = display
        self.input_control = input_control
        self.newApple()

        if debugMode == 1: print("starting")
        self.running = True

        self.display.clear_screen([0, 0, 0])

        self.display.write_string("WELCOME...", 7, 20, [50, 50, 255])
        self.display.show()
        self.drawBorder((0,0,0),True)

        if debugMode == 1: print("hello")
        time.sleep(3.0)

        self.display.clear_screen([0, 0, 0])
        self.display.show()
        time.sleep(1.0)

        prescalerCurrentIncrement = 0
        prescalerIncrementMax = 125 #max speed
        incrementPrescalerLimit = prescalerIncrementMax
        self.movementDir = Dir.STOP

        while self.running:
            if self.length - 10 < prescalerIncrementMax:  #increment speed depending on length
                incrementPrescalerLimit = prescalerIncrementMax - self.length /2
            else:
                incrementPrescalerLimit = 50

            prescalerCurrentIncrement = prescalerCurrentIncrement + 1

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if input_control.up_key_pressed() == 1 and self.movementDir != Dir.UP:
                        if debugMode == 1: print("up")
                        self.movementDir = Dir.DOWN
                    elif input_control.down_key_pressed() == 1 and self.movementDir != Dir.STOP and self.movementDir != Dir.DOWN:
                        if debugMode == 1: print("down")
                        self.movementDir = Dir.UP
                    elif input_control.left_key_pressed() == 1 and self.movementDir != Dir.RIGHT:
                        if debugMode == 1: print("left")
                        self.movementDir = Dir.LEFT
                    elif input_control.right_key_pressed() == 1 and self.movementDir != Dir.LEFT:
                        if debugMode == 1: print("right")
                        self.movementDir = Dir.RIGHT
                # else:
                # self.running = False
                # if debug == 1: print("end")

            time.sleep(0.001)

            if prescalerCurrentIncrement > incrementPrescalerLimit:
                if debugMode == 2: print("tick (inc = ",incrementPrescalerLimit,")")
                self.tick()

                if debugMode == 2: print("draw")
                self.drawMe()
                self.display.show()

                prescalerCurrentIncrement = 0

    time.sleep(2.0)