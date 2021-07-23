# arcade
- Super awesome games

### How to make it run

```
python run.py
```

On the raspberry:
 - Setup the pi: 
Install the raspberrian OS.
Clone this repository:
```
git clone https://github.com/benjamindrayer/arcade.git
```
After checking out the repo You have to init and update the submodule
```
cd arcade
git submodule init
git submodule update
```
Then gp to the rpi-rgb-led-matrix directory and compile
```
cd rpi-rgb-led-matrix
make -C examples-api-use
```
Build the lib and install it with the following commands:
```
sudo apt-get update && sudo apt-get install python3-dev python3-pillow -y
make build-python PYTHON=python3
sudo make install-python PYTHON=python3
```
make sure you have installed the following packages:
```
sudo apt-get install libatlas-base-dev
sudo apt-get install libsdl2-mixer-2.0-0
sudo python3 -m pip install -U numpy
sudo python3 -m pip install matplotlib
sudo python3 -m pip install -U pygame
sudo python3 -m pip install pyserial
```

```
sudo python3 run.py
```

### How to make it run on a raspberry pi with a 64x64 RGB-Led display ?

The submodule for the rgb lib was added the following way
```
git submodule add -b master https://github.com/hzeller/rpi-rgb-led-matrix
```
How to autostart the script after booting:
edit the /etc/profile/
```
sudo nano /etc/profile
```
At the end of the file add the folling:
```
cd /home/pi/Development/arcade
sudo python3 run.py
```

