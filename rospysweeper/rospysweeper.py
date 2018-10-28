from random import randint
from numpy import *
import curses
import curses.textpad
from curses import wrapper
import rospy
from sensor_msgs.msg import Joy
from std_msgs.msg import String

# input variables
dim_x = input("please insert number of cols:")
dim_y = input("please insert number of rows:")
n_mines = input("please insert number of mines:")

# curses stuff
stdscr = curses.initscr()
curses.start_color()
curses.init_pair(1, curses.COLOR_RED, curses.COLOR_CYAN)
curses.noecho()
curses.cbreak()
stdscr.keypad(1)
curses.curs_set(0)

# graphics params
color_separator = '.'
color_closed = curses.ACS_CKBOARD
color_empty = ' '
color_mine = 'X'
color_flag = 'F'
color_cursor = '*'

# states:
state_playing = 0
state_finished = 1
game_state = state_playing
move = None

# params:
board_top = 0
board_left = 0
mine_id = 9
wall_id = 10

# data
data = []
current_row = current_col = 0
neighbors = [[0, 1], [0, -1], [1, 0], [-1, 0], [-1, -1], [1, 1], [1, -1], [-1, 1]]

# UI
playing_commands = "Move: arrow keys  -  Flag: 'B'  -  Open:A  -  Quit:'X'  -  Restart: 'Y'"
finished_commands = "Quit: 'X'  -  Restart: 'Y'"


def game_update():

    global current_row, current_col, game_state, move

    newrow, newcol = current_row, current_col
    stdscr.refresh()

    # while game_state == state_finished and c not in [ord('r'), ord('R'), ord('q'), ord('Q')]:
        # c = stdscr.getch()

    if move == "right":

        newrow, newcol = current_row, current_col + 1

    elif move == "left":

        newrow, newcol = current_row, current_col - 1

    elif move == "up":

        newrow, newcol = current_row - 1, current_col

    elif move == "down":

        newrow, newcol = current_row + 1, current_col

    elif move == "flag":

        if data[current_row][current_col].color in [color_closed, color_flag]:
            newcolor = color_flag if data[current_row][current_col].color != color_flag else color_closed
            data[current_row][current_col].color = newcolor
            setCell(current_row, current_col, newcolor, curses.A_BLINK)

    elif move == "reveal":

        if data[current_row][current_col].mine_count == mine_id:

            game_over(False)
            game_state = state_finished
            log(finished_commands)

        else:
            reveal_cell(current_row, current_col)

    elif move == "quit":

       rospy.is_shutdown()

    elif move == "restart":

        init_board()

    if game_state == state_playing:
        moveCurrentCell(newrow, newcol)

def callback(joy_data):

    global move

    stdscr.refresh()

    if joy_data.buttons[0] == 1:

        move = "reveal"

    elif joy_data.buttons[1] == 1:

        move = "flag"

    elif joy_data.buttons[2] == 1:

        move = "quit"

    elif joy_data.buttons[3] == 1:

        move = "restart"

    elif joy_data.axes[6] == 1.0:

        move = "left"

    elif joy_data.axes[6] == -1.0:

        move = "right"

    elif joy_data.axes[7] == 1.0:

        move = "up"

    elif joy_data.axes[7] == -1.0:

        move = "down"

    elif joy_data.axes[6] == -0.0 or joy_data.axes[7] == -0.0:

        move = " "


    game_update()

"""Firstly, we generate the game board"""


def spawn_table(dim_x, dim_y, n_mines):

    table = create_table(dim_x, dim_y)
    table = add_mines(table, n_mines, dim_x, dim_y)
    table = generate_tiles(table, dim_x, dim_y)
    return table


def create_table(dim_x, dim_y):

    table = [[wall_id for j in range(dim_x + 2)] for i in range(dim_y + 2)]

    for i in range(1, dim_y + 1):

        for j in range(1, dim_x + 1):

            table[i][j] = 0

    return table


def add_mines(table, n_mines, dim_x, dim_y):

    for i in range(n_mines):

        is_mine = False

        while not is_mine:

            x = randint(1, dim_x + 1)
            y = randint(1, dim_y + 1)

            if table[y][x] != mine_id:
                table[y][x] = mine_id
                is_mine = True

    return table


def generate_tiles(table, dim_x, dim_y):

    for i in range(1, dim_y + 1):

        for j in range(1, dim_x + 1):

            if table[i][j] != mine_id:

                neighboring_cells = array(table)[i - 1: i + 2, j - 1: j + 2].tolist()
                table[i][j] = sum(t.count(mine_id) for t in neighboring_cells)

    return array(table)[1: dim_y + 1, 1: dim_x + 1].tolist()


"""Next, we convert the game board into OOP"""


class Tile(object):

    def __init__(self, color, mine_count):

        self.color, self.mine_count = color, mine_count


def validate_boundaries(row, col):

    global dim_x
    global dim_y

    if row < 0 or row >= dim_y or col < 0 or col >= dim_x:

        return False

    return True


def init_data(table):

    global dim_x
    global dim_y
    global data
    global n_mines

    # build 2D matrix of class "Tile"
    data = []
    for i in range(dim_y):

        row = []
        for j in range(dim_x):

            row.append(Tile(color_closed, table[i][j]))

        data.append(row)


def init_board():

    global game_state
    global dim_x
    global dim_y
    global n_mines

    table = spawn_table(dim_x, dim_y, n_mines)
    stdscr.clear()
    init_data(table)

    for i in range(dim_y):

        for j in range(dim_x):

            setCell(i, j, data[i][j].color)

        stdscr.addch(i, board_left + dim_x * 2, color_separator, curses.A_DIM)
        moveCurrentCell(0, 0)
        game_state = state_playing
        log(playing_commands)


def setCell(row, col, val, state = curses.A_DIM):

    if val == color_flag:

        state = curses.A_REVERSE

    stdscr.addch(board_top + row, board_left + col * 2, color_separator, curses.A_DIM)
    stdscr.addch(board_top + row, board_left + col * 2 + 1, val, state)


def moveCurrentCell(newrow, newcol):

    global current_row, current_col

    if not validate_boundaries(newrow, newcol):
        return

    val = data[current_row][current_col].color
    newval = color_cursor

    setCell(current_row, current_col, val)

    stdscr.addch(board_top + newrow, board_left + newcol * 2 + 1, newval, curses.color_pair(1))
    current_row, current_col = newrow, newcol


def reveal_cell(row, col):

    d = data[row][col].mine_count + ord('0')

    if d == ord('0'):

        d = color_empty

    setCell(row, col, d)
    data[row][col].color = d

    if d == color_empty:

        for n in neighbors:

            r, c = row + n[0], col + n[1]

            if not validate_boundaries(r,c):
                continue

            if data[r][c].color == color_closed:

                reveal_cell(r,c)


def game_over(hasWon):

    if not hasWon:

        for r in range(dim_y):

            for c in range(dim_x):

                if data[r][c].mine_count == mine_id:

                    setCell(r, c, color_mine, curses.A_REVERSE)


def log(s):

    log_row = board_top * 2 + dim_y
    stdscr.addstr(log_row, 0, len(playing_commands) * " ")
    stdscr.addstr(log_row, 0, s)





def main(stdscr):

    init_board()
    rospy.init_node('JoystickReader')
    rospy.Subscriber("joy", Joy, callback)

    rospy.spin()








wrapper(main)












