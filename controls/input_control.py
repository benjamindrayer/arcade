# Class to control the inputs
import time
from threading import Thread
import serial
import serial.tools.list_ports
import keyboard

INPUT_TYPE_KEYBOARD = 0
INPUT_TYPE_FLEXCHAIN = 1
INPUT_TYPE_BOTH = 2

EVENT_UP_PRESSED = 0
EVENT_UP_RELEASED = 1
EVENT_LEFT_PRESSED = 2
EVENT_LEFT_RELEASED = 3
EVENT_DOWN_PRESSED = 4
EVENT_DOWN_RELEASED = 5
EVENT_RIGHT_PRESSED = 6
EVENT_RIGHT_RELEASED = 7

class InputControl:

    def __init__(self, input_type=INPUT_TYPE_KEYBOARD):
        """Inits the input control. It start a background thread, that updates the current inputs.
        Right now it is only the keyboard, but soon it will also be the sensor grid bus.

        :param input_type: type of the input keyboard, flexchain or both
        """
        self.flex_chain = (input_type == INPUT_TYPE_BOTH) or (input_type == INPUT_TYPE_FLEXCHAIN)
        self.keyboard = (input_type == INPUT_TYPE_BOTH) or (input_type == INPUT_TYPE_KEYBOARD)
        self.serial = 0
        if self.flex_chain:
            if self.connect_flexchain():
                print("Connected to flexchain")     
            else:
                self.flex_chain = False
        self.events = []
        self.input_was_read = False

        self.left = 0
        self.right = 0
        self.up = 0
        self.down = 0
        #Run thread to check for inputs
        t = Thread(target=self.read_inputs, daemon=True)
        t.start()

    def connect_flexchain(self):
        """Connects to the flexchain serial port, we know that the name of it is
        FC[blablabla]CDC

        :return:
        """
        com_ports = list(serial.tools.list_ports.grep('FC.*CDC'))
        if len(com_ports) >= 1:
            selected_com_port = com_ports[0]
            print(selected_com_port)
            self.serial = serial.Serial(selected_com_port[0], baudrate=128000, rtscts=True, timeout=0.5)
            #check if open, return true
            print(self.serial)
            _ = self.serial.readlines()
            return self.serial.isOpen()
        print("ERROR: Tryed to connect to Flexchain but failed !")
        return False


    def read_inputs(self):
        """Read the inputs of the keyboard and/or the flexchain

        :return:
        """
        while True:
            #Clear events if they were read out
            if self.input_was_read:
                self.events = []
                self.input_was_read = False
            # Do the flexchain
            if self.flex_chain:
                self.serial.write(b'iolr 40\n')
                res = self.serial.readline()
                answer = res.split()
                # TODO Benjamin3er this is ugly and does only work for the single sensor,
                #                 cast as integer and to proper cases
                if len(answer) > 20:
                    if answer[0] == b'Read' and answer[1] == b'ISDU' and answer[2] == b'40.0:':
                        if answer[4] == b'0x01':
                            if self.up == 0:
                                self.events.append(EVENT_UP_PRESSED)
                                self.up = 1
                        else:
                            if self.up == 1:
                                self.events.append(EVENT_UP_RELEASED)
                                self.up = 0
            # Do the keyboard
            if self.keyboard:
                if keyboard.is_pressed("Left"):
                    if self.left == 0:
                        self.events.append(EVENT_LEFT_PRESSED)
                        self.left = 1
                else:
                    if self.left == 1:
                        self.events.append(EVENT_LEFT_RELEASED)
                        self.left = 0
                if keyboard.is_pressed("Right"):
                    if self.right == 0:
                        self.events.append(EVENT_RIGHT_PRESSED)
                        self.right = 1
                else:
                    if self.right == 1:
                        self.events.append(EVENT_RIGHT_RELEASED)
                        self.right = 0
                if keyboard.is_pressed("Up"):
                    if self.up == 0:
                        self.events.append(EVENT_UP_PRESSED)
                        self.up = 1
                else:
                    if self.up == 1:
                        self.events.append(EVENT_UP_RELEASED)
                        self.up = 0
                if keyboard.is_pressed("Down"):
                    if self.down == 0:
                        self.events.append(EVENT_DOWN_PRESSED)
                        self.down = 1
                else:
                    if self.down == 1:
                        self.events.append(EVENT_DOWN_RELEASED)
                        self.down = 0
            time.sleep(0.01)

    def get_events(self):
        """Get the list of events and trigger a delete of the list

        :return:
        """
        result = self.events.copy()
        self.input_was_read = True
        return result

    def any_key_pressed(self):
        """Check if any key is pressed

        :return:
        """
        return self.up + self.down + self.right + self.left
