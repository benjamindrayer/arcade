# Class to control the inputs
import keyboard
import time
import serial
import serial.tools.list_ports

INPUT_TYPE_KEYBOARD = 0
INPUT_TYPE_FLEXCHAIN = 1
INPUT_TYPE_BOTH = 2

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
        self.left = 0
        self.right = 0
        self.up = 0
        self.down = 0

    def connect_flexchain(self):
        """Connects to the flexchain serial port, we know that the name of it is
        FC[blablabla]CDC

        :return:
        """
        com_ports = list(serial.tools.list_ports.grep('FC.*CDC'))
        if len(com_ports) >= 1:
            selected_com_port = com_ports[0]
            #TODO Benjamin3er: change the speed to max
            print(selected_com_port)
            self.serial = serial.Serial(selected_com_port[0], baudrate=128000, rtscts=True, timeout=0.5)
            #check if open, return true
            print(self.serial)
            res = self.serial.readlines()
            return self.serial.isOpen()
        print("ERROR: Tryed to connect to Flexchain but failed !")
        return False

    def read_inputs(self):
        """Read the inputs of the keyboard and/or the flexchain

        :return:
        """
        self.left = 0
        self.right = 0
        self.up = 0
        self.down = 0
        #Do the keyboard
        if self.keyboard:
            self.left = keyboard.is_pressed("Left")
            self.right = keyboard.is_pressed("Right")
            self.down = keyboard.is_pressed("Down")
            self.up = keyboard.is_pressed("Up")
        #Do the flexchain
        if self.flex_chain:
            self.serial.write(b'iolr 40\n')
            res = self.serial.readline()
            answer = res.split()
            #TODO Benjamin3er this is ugly and does only work for the single sensor,
            #                 cast as integer and to prober cases
            if len(answer) > 20:
                if answer[0] == b'Read' and answer[1] == b'ISDU' and answer[2] == b'40.0:':
                    if answer[4] == b'0x01':
                        self.up = self.up or True
                    else:
                        self.up = self.up or False                            
                        

    def any_key_pressed(self):
        """Check if any key is pressed

        :return:
        """
        return self.up + self.down + self.right + self.left
