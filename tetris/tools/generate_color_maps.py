# Generate color maps for the tetris stones
from matplotlib import pyplot as plt
from matplotlib import cm


def print_color_map(index, identifier):
    col_map = cm.get_cmap(identifier)
    print("#" + identifier)
    print("COLOR_MAP_{:d} = {{".format(index))
    print("0: [20, 20, 20],")
    for i in range(8):
        color = col_map((i + 1) / 9)
        print("{:d}: [{:d}, {:d}, {:d}],".format(i + 1, int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)))
    print("}")


color_maps = ['winter', 'autumn', 'spring', 'summer', 'cool', 'Wistia', 'terrain', 'brg', 'jet', 'plasma',
              'gist_rainbow', 'gist_earth']
for index, ident in enumerate(color_maps):
    print_color_map(index, ident)

print("COLOR_MAPS = [")
for i in range(len(color_maps)):
    print("COLOR_MAP_{:d},".format(i))
print("]")
