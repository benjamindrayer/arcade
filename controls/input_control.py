# Class to control the inputs
import time
from threading import Thread
import serial
import serial.tools.list_ports
import numpy as np

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

# Defines, where to look for entries of the process data
# [2, 5] means byte 2 bit 5
N_BYTES_PD = 6
Y_VALUES_PD = [[0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7], [1, 0], [1, 1], [1, 2], [1, 3], [1, 4], [1, 5],
               [1, 6], [1, 7], [2, 0], [2, 1], [2, 2], [2, 3], [2, 4]]
X_VALUES_PD = [[2, 5], [2, 6], [2, 7], [3, 0], [3, 1], [3, 2], [3, 3], [3, 4], [3, 5], [3, 6], [3, 7], [4, 0], [4, 1],
               [4, 2], [4, 3], [4, 4], [4, 5], [4, 6], [4, 7], [5, 0]]
BUTTON_A_PD = [[0, 0]]
BUTTON_B_PD = [[0, 0]]
BUTTON_SHUTDOWN_PD = [[0, 0]]
N_BEAMS = 20

SHUT_DOWN_TIME_THRESH = 3

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
        # Controls from flexchain
        self.pd_bytes = np.zeros((N_BYTES_PD, 1), dtype=np.uint8)
        self.light_grid_y = np.zeros((N_BEAMS, 1), dtype=np.uint8)
        self.light_grid_x = np.zeros((N_BEAMS, 1), dtype=np.uint8)
        self.x_pos = -1
        self.y_pos = -1
        self.button_a = 0
        self.button_a_pressed = 0
        self.button_a_released = 0
        self.button_b = 0
        self.button_b_pressed = 0
        self.button_b_released = 0
        self.button_shutdown = 0
        self.button_shutdown_pressed = 0
        self.button_shutdown_released = 0
        self.button_shutdown_pressed_long = 0
        self.button_shutdown_pressed_time = 0
        # Run thread to check for inputs
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
            # Clear events if they were read out
            if self.input_was_read:
                self.events = []
                self.input_was_read = False
            # Do the flexchain
            if self.flex_chain:
                self.serial.write(b'iolr 40\n')
                res = self.serial.readline()
                answer = res.split()
                # Process the process data
                if len(answer) > 20:
                    if answer[0] == b'Read' and answer[1] == b'ISDU' and answer[2] == b'40.0:':
                        for byte_id in range(N_BYTES_PD):
                            self.pd_bytes[byte_id] = int(answer[4 + byte_id], 16)  # cast PD from string to int
                        #Read x/y
                        for beam_id in range(N_BEAMS):
                            self.light_grid_y[beam_id] = (self.pd_bytes[Y_VALUES_PD[beam_id][0]] >> Y_VALUES_PD[beam_id][1]) & 1
                            self.light_grid_x[beam_id] = (self.pd_bytes[X_VALUES_PD[beam_id][0]] >> X_VALUES_PD[beam_id][1]) & 1
                        #Read button A
                        button_a_value = (self.pd_bytes[BUTTON_A_PD[0][0]] >> BUTTON_A_PD[0][1]) & 1 
                        if self.button_a == 0 and button_a_value == 1:
                            self.button_a_pressed = 1
                        if self.button_a == 1 and button_a_value == 0:
                            self.button_a_released = 1
                        self.button_a = button_a_value
                        #Read button B
                        button_b_value = (self.pd_bytes[BUTTON_B_PD[0][0]] >> BUTTON_B_PD[0][1]) & 1
                        if self.button_b == 0 and button_b_value == 1:
                            self.button_b_pressed = 1
                        if self.button_b == 1 and button_b_value == 0:
                            self.button_b_released = 1
                        self.button_b = button_b_value
                        #Read button Shutdown
                        button_shutdown_value = (self.pd_bytes[BUTTON_SHUTDOWN_PD[0][0]] >> BUTTON_SHUTDOWN_PD[0][1]) & 1
                        if self.button_shutdown_value == 0 and button_shutdown_value == 1:
                            self.button_shutdown_pressed = 1
                            self.button_shutdown_pressed_time = time.time()
                        if self.button_shutdown_value == 1 and button_shutdown_value == 0:
                            self.button_shutdown_released = 1
                        if button_shutdown_value == 1:
                            current_time = time.time()
                            if current_time - self.button_shutdown_pressed_time > SHUT_DOWN_TIME_THRESH:
                                self.button_shutdown_pressed_long = 1
                        self.button_shutdown = button_shutdown_value
            time.sleep(0.01)


    def there_is_any_detection(self):
        """ Check if there was any detection 

        :return: True/False
        """
        for i in range(N_BEAMS):
            if self.light_grid_x[i] > 0 or self.light_grid_y[i] > 0:
                return True
            if self.button_a > 0:
                return True
        return False
        

    def wait_for_key_pressed(self):
        """Wait for a keypress event

        :return:
        """
        while not self.there_is_any_detection():
            time.sleep(0.3)

    def get_xy_position(self):
        """Compute the averaged position in the lightgrid

        :return: [x, y]
        """
        x = y = nx = ny = 0
        for i in range(N_BEAMS):
            if self.light_grid_y[i]:
                ny += 1
                y += i
            if self.light_grid_x[i]:
                nx += 1
                x += i
        x_res = y_res = -1
        if nx > 0:
            x_res = x / nx
        if ny > 0:
            y_res = y / ny
        return [x_res, y_res]
