from enum import Enum
import matplotlib.image as img
import numpy as np
import os
import time
import pygame
from random import randrange

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

maxX = 64
maxY = 64
lengthToWin = 20 #maxY*maxX-1
debug = 0

class FlexChainGame:
    def __init__(self):
        self.reInit()


    def reInit(self):
        self.path = os.path.dirname(__file__)
        self.length = 3
        self.dir = Dir.STOP
        self.display = 0
        self.input_control = 0
        self.tail = [Pixel(maxX / 2, maxY / 2, (0,30,255))]
        self.ApplePos = 0
        self.running = True

        for i in range(1, self.length):
            self.tail.append(Pixel(maxX / 2, maxY / 2 + i, (0,30,255)))

        if debug == 1: print("FlexChainGame set-up and ready to go")

    def hitControl(self,x,y):
        if debug == 1: print("hitControl ",x,",",y)
        if x < 0 or y < 0 or x>=maxX or y>=maxY:
            self.iAmDead()
            return

        for i in range(0,self.length):
            if x == self.tail[i].x and y == self.tail[i].y:
                self.iAmDead()
                print("hit body at [",i,"]",x,y)
                return

        if x == self.ApplePos.x and y == self.ApplePos.y:
            self.eatApple(x,y)

        self.tail.insert(0, Pixel(x,y, (0,30,255)))
        self.tail.pop()

    def eatApple(self,x,y):
        if debug == 1: print("yummy, apple!")
        self.length+=1
        self.tail.insert(0,Pixel(x,y,(0,255,255)))
        if self.length == lengthToWin:
            self.iAmWinner()
        self.newApple()
        self.drawMe()

    def newApple(self):
        if debug == 1: print("new Apple...")
        newAppleNotFound = True
        while newAppleNotFound:
            randX = randrange(maxX)
            randY = randrange(maxY)
            for i in range(0,self.length):
                if randX == self.tail[i].x and randY == self.tail[i].y:
                    newAppleNotFound = True
                else:
                    newAppleNotFound = False
                    self.ApplePos = Pixel(randX, randY, (255,0,0))
                    if debug == 1: print("... done at ",randX,",",randY)

    def move(self):
        curX = self.tail[0].x
        curY = self.tail[0].y

        newX = curX
        newY = curY

        print("moving ",self.dir)
        if self.dir == Dir.UP:
            newY = curY+1
        elif self.dir == Dir.DOWN:
            newY = curY-1
        elif self.dir ==  Dir.RIGHT:
            newX = curX+1
        elif self.dir ==  Dir.LEFT:
            newX = curX-1
        elif self.dir ==  Dir.STOP:
            return
        #else:
            #self.running = False

        self.hitControl(newX, newY)


    def colorMe(self, color):
        for i in range(0,self.length):
            self.tail[i].col = color

    def iAmWinner(self):
        self.colorMe((0,255,1))
        self.display.write_string("WINNER", 13, 10, [50, 50, 255])
        print("winner")
        self.drawMe()
        time.sleep(5.0)

    def iAmDead(self):
        self.colorMe((255,0,0))
        self.running = False
        self.display.write_string("YOU DIED", 13, 10, [255, 0, 5])
        print("crash at",self.tail[0].x, ",",self.tail[0].y)
        for i in range(0,self.length):
            print("tail [",i,"]",self.tail[i].x,",",self.tail[i].y)
        self.drawMe()
        time.sleep(5.0)

    def drawMe(self):
        self.display.clear_screen([0, 0, 0])

        #apple
        self.display.fill_rectangle(self.ApplePos.x, self.ApplePos.x, self.ApplePos.y, self.ApplePos.y , self.ApplePos.col)

        #FlexChain
        for i in range(0,self.length):
             #print("drawing [",i,"]",self.tail[i].x,",",self.tail[i].y,"(",self.tail[i].col[0],",",self.tail[i].col[1],",",self.tail[i].col[2],")")
             self.display.fill_rectangle(self.tail[i].x, self.tail[i].x , self.tail[i].y, self.tail[i].y , self.tail[i].col)
        self.display.show()


    def get_title_image(self):
        """Get the iconic image of the game

        """
        image = img.imread(os.path.join(self.path, 'images/FlexChainLogo.png'))
        return np.transpose(image[:, :, :3], (1, 0, 2)) * 255

    def button_up(self):
        self.dir = Dir.UP

    def button_right(self):
         self.dir = Dir.RIGHT

    def button_down(self):
        self.dir = Dir.DOWN

    def button_lef(self):
        self.dir = Dir.LEFT

    def tick(self):
        self.move()

    def run_game(self, display, input_control):
        self.reInit()
        self.display = display
        self.input_control = input_control
        self.newApple()

        if debug == 1: print("starting")
        self.running = True

        self.display.clear_screen([0, 0, 0])

        self.display.write_string("RUN", 13, 10, [50, 50, 255])
        self.display.show()

        if debug == 1: print("hello")
        time.sleep(2.0)

        self.display.clear_screen([0, 0, 0])
        self.display.show()
        time.sleep(1.0)

        increment = 0
        inc_max = 125
        cur_max = inc_max
        self.dir = Dir.STOP

        while self.running:
            if self.length - 10 < inc_max:
                cur_max = inc_max - self.length*2
            else:
                cur_max = 50

            increment=increment+1

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if input_control.up_key_pressed() == 1:
                        if debug == 1: print("up")
                        self.dir = Dir.DOWN
                    elif input_control.down_key_pressed() == 1:
                        if debug == 1: print("down")
                        self.dir = Dir.UP
                    elif input_control.left_key_pressed() == 1:
                        if debug == 1: print("left")
                        self.dir = Dir.LEFT
                    elif input_control.right_key_pressed() == 1:
                        if debug == 1: print("right")
                        self.dir = Dir.RIGHT
                   # else:
                       # self.running = False
                       # if debug == 1: print("end")

            time.sleep(0.001)

            if increment > cur_max:
                if debug == 1: print("tick")
                self.tick()

                if debug == 1: print("draw")
                self.drawMe()
                self.display.show()

                increment = 0



    time.sleep(5.0)