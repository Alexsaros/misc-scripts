import numpy as np
import msvcrt
import random
import copy
import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle


def init_map_ground():
    map_empty = np.zeros([map_width, map_height], dtype=str)
    for y in range(len(map_empty[0])):
        for x in range(len(map_empty)):
            map_empty[x, y] = '·'
    return map_empty


screen = curses.initscr()
curses.noecho()
curses.cbreak()
screen.keypad(True)

map_width = 10
map_height = 5

map_window = curses.newwin(map_height, map_width*3, 0, 0)
char_window = curses.newpad(100, 100)

curses.start_color()
curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_RED)

while True:
    c = screen.getch()
    if c == ord('q'):
        break
    map_empty = init_map_ground()
    for y in range(len(map_empty[0])):
        for x in range(len(map_empty)):
            map_window.addstr(y, x*3+1, map_empty[x, y])
    char_window.addstr(0, 0, "This is a test string. This is a test string. This is a test string. This is a test string. This is a test string. This is a test string. This is a test string. This is a test string. This is a test string. This is a test string. This is a test string. ")
    screen.addstr(0, 0, "Enter IM message: (hit Ctrl-G to send)", curses.color_pair(1))

    editwin = curses.newwin(5, 30, 2, 1)

    screen.refresh()
    map_window.refresh()
    char_window.refresh(0, 0, 0, map_width*3+3, map_height, 40)


curses.nocbreak()
screen.keypad(False)
curses.echo()

curses.endwin()
