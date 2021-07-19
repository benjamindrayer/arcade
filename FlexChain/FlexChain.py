from enum import Enum
import matplotlib.image as img
import numpy as np
import os
import time
import pygame
from random import randrange
from leaderboard.leader_board import *

#simple enum to avoid using 1 for up. yay, so efficient!
class Dir(Enum):
    STOP = 0
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4
    CRASH = 5

#helper for a pixel. why so complicated?
class Pixel:
    def __init__(self, x, y, col):
        self.x = int(x)
        self.y = int(y)
        self.col = col


maxX = 64-1  #coordinates
maxY = 64-1  #coordinates
minX = 0     #coordinates
minY = 12    #last coordinates
lengthToWin = (maxY-minY)*(maxX-minY)-1  #TODO may be a bit hard to reach.
debugMode = 0  #enable if you want to get to know stuff. or cheat
startLength = 3 #too short?
if debugMode >= 1: #these aren't the cheats you were looking for
    startLength = 198 #cheat!
    lengthToWin = startLength+2 #more cheats!



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
        """
        yeah. uhm. uh.
        init all the stuf you can find
        """
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

        #init the first flexchain body
        for i in range(1, self.length):
            self.body.append(Pixel(maxX / 2, maxY / 2 + i, (0, 30, 255)))

        if debugMode == 1: print("FlexChainGame set-up and ready to go")

    def drawBorder(self, color, show = False):
        """
        draw a border and title and stats.
        color (0,0,0) makes random stuff
        show = True makes boring animations.
        """
        #the title is wobbling between blueish and greenish. here is where the magic happens.
        self.colorBlue = self.colorBlue + self.deltaBlue
        if self.colorBlue > self.maxBlue:
            self.colorBlue = self.maxBlue
            self.deltaBlue = self.deltaBlue * -1
        elif self.colorBlue < self.minBlue:
            self.colorBlue = self.minBlue
            self.deltaBlue = self.deltaBlue * -1

        randomCol = False
        if color == (0, 0, 0): randomCol = True

        #add some text stuff
        #print("blue:",self.colorBlue , " delta:", self.deltaBlue)
        self.display.write_string("FLEX CHAIN GAME", 1, 1, [0,int(150-self.colorBlue/2),self.colorBlue])
        if randomCol: color = (randrange(0, 255), randrange(0, 255), randrange(0, 255))
        self.display.write_string("SCORE:", 1, 7, color)
        if randomCol: color = (randrange(0, 255), randrange(0, 255), randrange(0, 255))
        self.display.write_string(str(self.length), 27, 7, color)

        #horizonzal borders
        for i in range(minX, maxX+1):
            if randomCol : color = (randrange(0, 255), randrange(0, 255), randrange(0, 255))
            self.display.fill_rectangle(i, i, minY, minY, color)
            if randomCol: color = (randrange(0, 255), randrange(0, 255), randrange(0, 255))
            self.display.fill_rectangle(i, i, maxY, maxY, color)
            if show == True: self.display.show()

        #draw some more borders
        for i in range(minY, maxY):
            if randomCol : color = (randrange(0, 255), randrange(0, 255), randrange(0, 255))
            self.display.fill_rectangle(minX, minX, i, i, color)
            if randomCol: color = (randrange(0, 255), randrange(0, 255), randrange(0, 255))
            self.display.fill_rectangle(maxX, maxX, i, i, color)
            if show == True: self.display.show()

    def finishIt(self):
        """ we're done. get us out here
        but first: show the leader board"""
        self.display.clear_screen([32, 32, 32])
        self.drawBorder((0,0,0),True)
        self.leaderBoard.run_leader_board(self.length, self.display, self.input_control)


    def hitControl(self, x, y):
        """
        check if the flexchain is about to eat an apple, itself or the border.
        last two aren't good actually

        make a small step forward if not dead
        (or a big leap for flex-chain-kind)
        """
        if debugMode == 1: print("hitControl ", x, ",", y)

        #check borders
        if x <= minX or y <= minY or x >= maxX or y >= maxY:
            self.iAmDead()
            return

        #check self-hit
        for i in range(0, self.length):
            if x == self.body[i].x and y == self.body[i].y:
                self.iAmDead()
                print("hit body at [", i, "]", x, y)
                return

        #check if eating an apple
        if x == self.ApplePos.x and y == self.ApplePos.y:
            self.eatApple(x, y)

        #move to the next bit
        self.body.insert(0, Pixel(x, y, (0, 30, 255)))
        #delete last body segment as if we were moving... haha, what a hoax.
        self.body.pop()

    def eatApple(self, x, y):
        """
        an apple a day keeps the doctor away
        (disclaimer: only works on dr. med.)
        """
        if debugMode == 1: print("yummy, apple!")
        self.length += 1 #increase length
        #TODO currently inserting a green apple at the apple sposition to the flexchain body. better just skip deleting the last part of the body once for faster growth
        self.body.insert(0, Pixel(x, y, (0, 255, 255)))

        #congratulations, you've won. maybe
        if self.length == lengthToWin:
            self.iAmWinner()

        #produce more apples
        self.newApple()
        self.drawMe()

    def newApple(self):
        """ apple tree (factory). kind of"""
        if debugMode == 1: print("new Apple...")
        newAppleNotFound = True

        #just hit random as often as required without putting the new apple on the body of the flexchain
        while newAppleNotFound:
            hits = 0
            randX = randrange(minX+1,maxX-1)
            randY = randrange(minY+1,maxY-1)
            for i in range(0, self.length):
                if randX == self.body[i].x and randY == self.body[i].y:
                    hits = hits +1 #check if the body was hit at least once

            if hits == 0: #and grow an apple if not.
                newAppleNotFound = False
                self.ApplePos = Pixel(randX, randY, (255, 0, 0))
                if debugMode == 1: print("... done at ", randX, ",", randY)

    def move(self):
        """
        move a step forward
        """
        curX = self.body[0].x
        curY = self.body[0].y

        newX = curX
        newY = curY

        if debugMode == 1: print("moving ", self.movementDir)

        #check the direction and get the next field
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

        # check if the next field is valid or an apple. executes step if valid
        self.hitControl(newX, newY)

    def colorMe(self, color):
        """
        color the flexchain new... red, blue, pink... whatever
        """
        for i in range(0, self.length):
            self.body[i].col = color
        self.drawBorder(color)

    def iAmWinner(self):
        """
        i aM tHe bEsT!1!1!
        """
        self.colorMe((0, 255, 1))
        if debugMode == 1: print("winner")
        self.running = False
        self.drawMe()
        self.display.write_string("WINNER", 20, 17, [50, 50, 255])
        self.display.write_string("WINNER", 20, 24, [50,255, 50])
        self.display.write_string("CHICKEN", 20, 31, [0, 50, 255])
        self.display.write_string("DINNER!", 20, 38, [50, 255, 50])
        self.display.show()
        time.sleep(4.0)
        for i in range(0, 64):
            g = i * 4
            if g > 255:
                g = 255
            self.display.clear_screen([0, g, 0])
            self.display.show()
            time.sleep(0.075)
        self.finishIt()

    def iAmDead(self):
        """
        Rand oder selbst gefresse. tot. schade.
        """
        self.colorMe((255, 0, 0))
        self.running = False
        if debugMode == 1: print("crash at", self.body[0].x, ",", self.body[0].y)
        for i in range(0, self.length):
            if debugMode == 2: print("tail [", i, "]", self.body[i].x, ",", self.body[i].y)

        self.drawMe()
        self.display.write_string("s YOU DIED s", 10, 17, [255, 0, 5])
        self.display.show()
        time.sleep(2.0)
        for i in range(0, 32):
            r = i * 8
            if r > 255:
                r = 255
            self.display.clear_screen([r, 0, 0])
            self.display.show()
            time.sleep(0.075)
        self.finishIt()

    def drawMe(self):
        """
        Zeichnet den Rand, die Score, den Titel, den Apfel und die FlexChain neu

        """
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

        #begrüßung anzeigen
        self.display.write_string("WELCOME...", 7, 20, [50, 50, 255])
        self.display.show()
        self.drawBorder((0,0,0),True) #(0,0,0),True = bunt und mit effekt

        if debugMode == 1: print("hello")
        time.sleep(3.0)

        self.display.clear_screen([0, 0, 0])
        self.display.show()
        time.sleep(1.0)

        #prescaler initialisieren für flüssige eingabe aber langsame bewegung
        prescalerCurrentIncrement = 0
        prescalerIncrementMax = 20 #max speed
        incrementPrescalerLimit = prescalerIncrementMax
        self.movementDir = Dir.STOP

        while self.running:

            #prescaler Limit neu setzen anhand der Länge der Schlange
            if self.length - 10 < prescalerIncrementMax:  #increment speed depending on length
                incrementPrescalerLimit = prescalerIncrementMax - self.length /2
            else:
                incrementPrescalerLimit = 20

            #prescaler incrementieren
            prescalerCurrentIncrement = prescalerCurrentIncrement + 1


            #check input
            #TODO vergleich mit zu letzt gelaufener richtung (nach 1 schritt) und nicht mit aktuellem Parameter
            events = pygame.event.get()
            move_threshold = 1.0
            if input_control.flex_chain:
                position = input_control.get_xy_position()
                if position[0] >= 0 and position[1] >= 0:
                    x_dir = position[0] - (N_BEAMS-1)/2
                    y_dir = position[1] - (N_BEAMS-1)/2
                    if abs(x_dir) > abs(y_dir):
                        if x_dir < -move_threshold and self.movementDir != Dir.RIGHT:
                            self.movementDir = Dir.LEFT
                        if x_dir > move_threshold and self.movementDir != Dir.LEFT:
                            self.movementDir = Dir.RIGHT
                    else:
                        if y_dir < -move_threshold and self.movementDir != Dir.UP:
                            self.movementDir = Dir.DOWN
                        if y_dir > move_threshold and self.movementDir != Dir.DOWN:
                            self.movementDir = Dir.UP

            if input_control.keyboard:
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP and self.movementDir != Dir.UP:
                            if debugMode == 1: print("up")
                            self.movementDir = Dir.DOWN
                        elif event.key == pygame.K_DOWN and self.movementDir != Dir.DOWN:
                            if debugMode == 1: print("down")
                            self.movementDir = Dir.UP
                        elif event.key == pygame.K_LEFT and self.movementDir != Dir.RIGHT:
                            if debugMode == 1: print("left")
                            self.movementDir = Dir.LEFT
                        elif event.key == pygame.K_RIGHT and self.movementDir != Dir.LEFT:
                            if debugMode == 1: print("right")
                            self.movementDir = Dir.RIGHT

            time.sleep(0.001)

            #prescaler testen und ggf. einen Game-Tick ausführen
            if prescalerCurrentIncrement > incrementPrescalerLimit:
                if debugMode == 2: print("tick (inc = ",incrementPrescalerLimit,")")
                self.tick()

                if debugMode == 2: print("draw")
                self.drawMe()
                self.display.show()

                prescalerCurrentIncrement = 0

    #ende
    time.sleep(2.0)
