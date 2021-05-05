#Class to control the inputs
import keyboard

class InputControl:

    def __init__(self, input_type=0):
        self.input_type = input_type

    def left_key_pressed(self):
        if self.input_type == 0:
            return keyboard.is_pressed("Left")

    def right_key_pressed(self):
        if self.input_type == 0:
            return keyboard.is_pressed("Right")

    def up_key_pressed(self):
        if self.input_type == 0:
            return keyboard.is_pressed("Up")

    def down_key_pressed(self):
        if self.input_type == 0:
            return keyboard.is_pressed("Down")

    def wait_for_up_key_pressed(self):
        if self.input_type == 0:
            keyboard.wait("Up")