"""
Alan M Jackson

A version of the Towers of Hanoi puzzle
"""


import curses
import curses.textpad

_DEFAULT_TOWERS = 3
_DEFAULT_RINGS = 5

DOWN_KEY = 258
UP_KEY = 259
LEFT_KEY = 260
RIGHT_KEY = 261

T = 0   # top coordinate of bounding box
B = 1   # bottom coordinate of bounding box
Y = 0   # Y part of coordinate
X = 1   # X part of coordinate


class Game:

    def __init__(self, towers=_DEFAULT_TOWERS, rings=_DEFAULT_RINGS):

        self.towers = towers
        self.rings = rings
        self.board = [[] for x in range(self.towers)]
        self.won = False

        for i in range(1, self.rings + 1):
            self.board[0].append(i)


    def move(self, source_tower, destination_tower):

        if source_tower != destination_tower:

            if len(self.board[destination_tower]) == 0 or \
                self.board[source_tower][0] < self.board[destination_tower][0]:

                ring = self.board[source_tower].pop(0)
                self.board[destination_tower].insert(0, ring)

            else:
                raise ValueError("Cannot put a ring on top of a smaller ring.")

            if destination_tower == self.towers - 1 and len(self.board[destination_tower]) == self.rings:
                self.won = True


    def get_top_ring(self, tower_index):

        if len(self.board[tower_index]) > 0:
            return self.board[tower_index][0]
        else:
            return None



class GameUI:


    def __init__(self, screen, game, debug=True):
        self.tower_width = 6
        self.board_width = game.towers * self.tower_width
        self.screen = screen
        self.current_tower = 0
        self.screen_height, self.screen_width = screen.getmaxyx()
        self._DEBUG_SCR = screen.subwin(self.screen_height - 12, 0)
        self.banner_box = ((0, 0),(3, self.board_width))   #(y,x) coords of top left & bottom right of bounding box
        self.ring_box = ((self.banner_box[B][Y], 0), (self.banner_box[B][Y] + 3, self.board_width))
        self.tower_box = ((self.ring_box[B][Y], 0), (self.ring_box[B][Y] + game.rings + 3, self.board_width))
        self.select_box =((self.tower_box[B][Y], 0), (self.tower_box[B][Y] + 3, self.board_width)) 
        self._debug = debug




    def show_message(self, message):
        self.screen.addstr(message)
        self.screen.refresh()


    def show_message_box(self, message):
        msg_str = "=" * self.board_width + "\n"
        msg_str += message.center(self.board_width) + "\n"
        msg_str += "=" * self.board_width + "\n"
        self.show_message(msg_str)


    def DEBUG(self, msg, wait=False):
        if self._debug:
            y, x = self._DEBUG_SCR.getyx()
            max_y, max_x = self._DEBUG_SCR.getmaxyx()

            if y >= max_y - 3:
                self._DEBUG_SCR.clear()
                self._DEBUG_SCR.move(0, 0)


            self._DEBUG_SCR.addstr(str(msg) + "\n")
            self._DEBUG_SCR.refresh()

            if wait:
                self._DEBUG_SCR.getch()

    def pause(self):
        self.screen.getch()



def show_board(game, ui):

    display_str = ""
    board_display = [["|" for y in range(game.towers)] for x in range(game.rings + 1)]

    for tower_index in range(len(game.board)):
        height = len(game.board[tower_index])

        for ring_index in range(height):
            offset = game.rings + 1 - height
            board_display[offset + ring_index][tower_index] = game.board[tower_index][ring_index]


    display_str += "\n"
    for row in board_display:
        row_str = " "
        for item in row:
            row_str += str(item).center(ui.tower_width - 1) + " "

        display_str += row_str + "\n"

    tower_bases = " "
    tower_base_str = "+".center(ui.tower_width - 1, "-")
    for i in range(game.towers):
        tower_bases += tower_base_str + " "

    display_str += tower_bases + "\n"

    ui.screen.move(ui.tower_box[T][Y], ui.tower_box[T][X])
    ui.screen.addstr(display_str)
    ui.screen.refresh()



def highlight_tower(ui, tower):
    ui.screen.addstr(ui.select_box[T][Y], ui.select_box[T][X], " " * ui.board_width)
    ui.screen.addstr(ui.select_box[T][Y], tower * ui.tower_width + 1, "=" * (ui.tower_width - 1))
    ui.screen.refresh()


def show_ring(ui, ring):

    
    if ring == None:
        for y in range(ui.ring_box[T][Y], ui.ring_box[B][Y]):
            ui.screen.move(y, 0)
            ui.screen.clrtoeol()

    else:
        y = int( (ui.ring_box[T][Y] + ui.ring_box[B][Y]) / 2 )
        ring_str = str(ring).center(ui.board_width + 1)
        ui.screen.addstr(y, 0, ring_str)
        box_margin = int((ui.board_width - ui.tower_width) / 2) + 1
        curses.textpad.rectangle(ui.screen, ui.ring_box[T][Y], ui.ring_box[T][X] + box_margin, 
                                 ui.ring_box[B][Y] - 1, ui.ring_box[B][X] - box_margin)

    ui.screen.refresh()






def hide_top_ring(ui, game, tower):

    x = ui.tower_width * tower + int(ui.tower_width / 2) + ui.tower_box[T][X]
    y = game.rings - len(game.board[tower]) + 2 + ui.tower_box[T][Y]

    ui.screen.addstr(y, x, "|")
    ui.screen.refresh()


def input_move(game, ui):

    highlight_tower(ui, ui.current_tower)

    source_tower = None
    while source_tower == None:

        command_chr = ui.screen.getch()
        if command_chr == UP_KEY or command_chr == ord("k"):
            
            if len(game.board[ui.current_tower]) > 0:
                source_tower = ui.current_tower
                show_ring(ui, game.get_top_ring(source_tower))
                hide_top_ring(ui, game, source_tower)
            
        elif command_chr == LEFT_KEY or command_chr == ord("h"):

            if ui.current_tower > 0 :
                ui.current_tower -= 1
                highlight_tower(ui, ui.current_tower)

        elif command_chr == RIGHT_KEY or command_chr == ord("l"):

            if ui.current_tower < game.towers - 1:
                ui.current_tower += 1
                highlight_tower(ui, ui.current_tower)


    destination_tower = None
    while destination_tower == None:

        command_chr = ui.screen.getch()
        if command_chr == DOWN_KEY or command_chr == ord("j"):
            destination_tower = ui.current_tower
            show_ring(ui, None)

        elif command_chr == LEFT_KEY or command_chr == ord("h"):

            if ui.current_tower > 0 :
                ui.current_tower -= 1
                highlight_tower(ui, ui.current_tower)

        elif command_chr == RIGHT_KEY or command_chr == ord("l"):

            if ui.current_tower < game.towers - 1:
                ui.current_tower += 1
                highlight_tower(ui, ui.current_tower)

    return (source_tower, destination_tower)


def show_banner(ui):
    ui.screen.addstr(ui.banner_box[T][Y], ui.banner_box[T][X], "Hanoi".center(ui.board_width))
    ui.screen.refresh()


def show_splash_screen(screen):

    splash_screen = screen.subwin(20, 55, 2, 5)

    left = 2
    splash_screen.addstr(1, left, "Hanoi".center(50))
    splash_screen.addstr(10, left, "Move the discs from the left to the right tower.".center(50))
    splash_screen.addstr(11, left, "You can't put a big disc on top of a smaller one.".center(50))
    splash_screen.addstr(13, left, "Use LEFT and RIGHT arrow keys to select a tower.".center(50))
    splash_screen.addstr(14, left, "Use UP and DOWN to pick up and place a disc.".center(50))
    splash_screen.addstr(17, left, "Press any key to continue...".center(50))

    splash_screen.border()


    #Mucking about trying out different curses lines
    x = 12
    y = 4
    splash_screen.addch(y,    x+2, curses.ACS_PLUS)
    splash_screen.addch(y+1,  x+2, curses.ACS_PLUS)
    splash_screen.addch(y+1,  x+1, curses.ACS_HLINE)
    splash_screen.addch(y+1,  x+3, curses.ACS_HLINE)
    splash_screen.addch(y+2,  x+2, curses.ACS_BTEE)
    splash_screen.addch(y+2,  x,   curses.ACS_HLINE)
    splash_screen.addch(y+2,  x+1, curses.ACS_HLINE)
    splash_screen.addch(y+2,  x+3, curses.ACS_HLINE)
    splash_screen.addch(y+2,  x+4, curses.ACS_HLINE)

    x = 24
    splash_screen.addch(y,   x+2, curses.ACS_VLINE)
    splash_screen.addch(y+1, x+2, curses.ACS_VLINE)
    splash_screen.addch(y+2, x+2, curses.ACS_BTEE)
    splash_screen.addch(y+2, x,   curses.ACS_HLINE)
    splash_screen.addch(y+2, x+1, curses.ACS_HLINE)
    splash_screen.addch(y+2, x+3, curses.ACS_HLINE)
    splash_screen.addch(y+2, x+4, curses.ACS_HLINE)

    x = 36
    splash_screen.addch(y,   x+2, curses.ACS_VLINE)
    splash_screen.addch(y+1, x+2, curses.ACS_VLINE)
    splash_screen.addch(y+2, x+2, curses.ACS_BTEE)
    splash_screen.addch(y+2, x,   curses.ACS_HLINE)
    splash_screen.addch(y+2, x+1, curses.ACS_HLINE)
    splash_screen.addch(y+2, x+3, curses.ACS_HLINE)
    splash_screen.addch(y+2, x+4, curses.ACS_HLINE)



    screen.getch()
    screen.clear()
    screen.refresh()


def main(stdscr):

    curses.curs_set(0)
    show_splash_screen(stdscr)

    game = Game()
    ui = GameUI(stdscr, game)

    show_banner(ui)

    while not game.won:
        show_board(game, ui)

        source_tower, destination_tower = input_move(game, ui)

        try:
            game.move(source_tower, destination_tower)
        except ValueError as e:
            ui.show_message(e)

    show_board(game, ui)


    ui.show_message_box("You Won")
    ui.pause()


if __name__ == '__main__':
    curses.wrapper(main)
