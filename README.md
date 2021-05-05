# arcade
- Super awesome games

### How to make it run

```
python run.py
```

Make sure that you use python3, pygame version 2 and keyboard is installed
```
pip3 install pygame
pip3 install keyboard
```
### How to make it run on a raspberry pi with a 64x64 RGB-Led display ?

The submodule for the rgb lib was added the following way
```
git submodule add -b master https://github.com/hzeller/rpi-rgb-led-matrix
```
After checking out the repo You have tp init and update the submodule
```
git submodule init
git submodule update
```
Then gp to the rpi-rgb-led-matrix directory and compile
```
cd rpi-rgb-led-matrix
make -C examples-api-use
```