# Class to control the inputs
import keyboard
import threading
import time


class InputControl:

    def __init__(self, input_type=0):
        """Inits the input control. It start a background thread, that updates the current inputs.
        Right now it is only the keyboard, but soon it will also be the sensor grid bus.

        :param input_type:
        """
        self.input_type = input_type
        self.left = 0
        self.right = 0
        self.up = 0
        self.down = 0
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()  # Start the execution

    def run(self):
        """Run and poll the keyboard inputs, obviously this could be more
        elegant with a simple callback from the keyboard, but the communication
        with the sensor grid will also be more like this. At least I assume it :-)

        :return:
        """
        while True:
            if self.input_type == 0:
                self.left = keyboard.is_pressed("Left")
                self.right = keyboard.is_pressed("Right")
                self.down = keyboard.is_pressed("Down")
                self.up = keyboard.is_pressed("Up")
            time.sleep(0.01)

    def any_key_pressed(self):
        """Check if any key is pressed

        :return:
        """
        return self.up + self.down + self.right + self.left
