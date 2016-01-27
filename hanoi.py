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

WHITE_ON_BLACK = 0
RED_ON_BLACK = 1
BLACK_ON_BLACK = 2


#The Model in an MVC pattern - can be used without a view, implements the game logic.
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


#The View - Stateless, can show a game state and get user input.
#Can be used independently of the controller. 
class GameView:

    top_margin = 2
    left_margin = 10
    tower_margin = 5        #The space between towers
    selection_margin = 1
    pillar_extension = 1    #Height that the pillar extends above the top ring.
    base_extension = 1      #The width the base extends wider than the largest ring on each side.
    min_ring_width = 5      #Width of the smallest ring
    ring_scaling = 2
    ring_height = 1


    def __init__(self, screen, game, debug=True):

        #Set up colours
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_BLACK)

        self.rings = game.rings
        self.tower_width = game.rings * GameView.ring_scaling + 1 + \
            (GameView.min_ring_width - 3) + GameView.base_extension * 2

        self.board_width = game.towers * self.tower_width
        self.screen = screen
        self.current_tower = 0
        self.screen_height, self.screen_width = screen.getmaxyx()
        self.__DEBUG_SCR = screen.subwin(self.screen_height - 12, 0)

        x = GameView.left_margin
        self.banner_box = ((0, x),(3, x + self.board_width))   #(y,x) coords of top left & bottom right of bounding box
        self.ring_box = ((self.banner_box[B][Y], x), (self.banner_box[B][Y] + 3, x + self.board_width))
        self.tower_box = ((self.ring_box[B][Y] + GameView.selection_margin, 
                           x + GameView.selection_margin), 
                          (self.ring_box[B][Y] + GameView.selection_margin + game.rings + 3, 
                            x + self.board_width))

        self.board_height = self.tower_box[B][Y]
        self.select_box =((self.tower_box[B][Y], x), (self.tower_box[B][Y] + 3, x + self.board_width)) 

        self.__debug = debug




    def show_message(self, message):
        self.screen.addstr(message)
        self.screen.refresh()


    def show_message_box(self, message):

        y = GameView.top_margin
        x = GameView.left_margin
        height = 10
        width = 50

        msg_screen = self.screen.derwin(height, width, y, x)

        #clear the area
        msg_screen.clear()

        msg_screen.addstr(3, 0, message.center(width))

        curses.textpad.rectangle(self.screen,
                                 y - 1, x - 1, y + height,  x + width)




    def DEBUG(self, msg, wait=False):
        if self.__debug:
            y, x = self.__DEBUG_SCR.getyx()
            max_y, max_x = self.__DEBUG_SCR.getmaxyx()

            if y >= max_y - 3:
                self.__DEBUG_SCR.clear()
                self.__DEBUG_SCR.move(0, 0)


            self.__DEBUG_SCR.addstr(str(msg) + "\n")
            self.__DEBUG_SCR.refresh()

            if wait:
                self.__DEBUG_SCR.getch()

    def pause(self):
        self.screen.getch()


    def show_splash_screen(self):
        screen = self.screen

        msg_box = screen.subwin(20, 55, GameView.top_margin, GameView.left_margin)

        left = 2
        msg_box.addstr(1, left, "Hanoi".center(50))
        msg_box.addstr(10, left, "Move the discs from the left to the right tower.".center(50))
        msg_box.addstr(11, left, "You can't put a big disc on top of a smaller one.".center(50))
        msg_box.addstr(13, left, "Use LEFT and RIGHT arrow keys to select a tower.".center(50))
        msg_box.addstr(14, left, "Use UP and DOWN to pick up and place a disc.".center(50))
        msg_box.addstr(17, left, "Press any key to continue...".center(50))

        msg_box.border()

        x = 12
        y = 4
        msg_box.addch(y,    x+2, curses.ACS_PLUS)
        msg_box.addch(y+1,  x+2, curses.ACS_PLUS)
        msg_box.addch(y+1,  x+1, curses.ACS_HLINE)
        msg_box.addch(y+1,  x+3, curses.ACS_HLINE)
        msg_box.addch(y+2,  x+2, curses.ACS_BTEE)
        msg_box.addch(y+2,  x,   curses.ACS_HLINE)
        msg_box.addch(y+2,  x+1, curses.ACS_HLINE)
        msg_box.addch(y+2,  x+3, curses.ACS_HLINE)
        msg_box.addch(y+2,  x+4, curses.ACS_HLINE)

        x = 24
        msg_box.addch(y,   x+2, curses.ACS_VLINE)
        msg_box.addch(y+1, x+2, curses.ACS_VLINE)
        msg_box.addch(y+2, x+2, curses.ACS_BTEE)
        msg_box.addch(y+2, x,   curses.ACS_HLINE)
        msg_box.addch(y+2, x+1, curses.ACS_HLINE)
        msg_box.addch(y+2, x+3, curses.ACS_HLINE)
        msg_box.addch(y+2, x+4, curses.ACS_HLINE)

        x = 36
        msg_box.addch(y,   x+2, curses.ACS_VLINE)
        msg_box.addch(y+1, x+2, curses.ACS_VLINE)
        msg_box.addch(y+2, x+2, curses.ACS_BTEE)
        msg_box.addch(y+2, x,   curses.ACS_HLINE)
        msg_box.addch(y+2, x+1, curses.ACS_HLINE)
        msg_box.addch(y+2, x+3, curses.ACS_HLINE)
        msg_box.addch(y+2, x+4, curses.ACS_HLINE)



        screen.getch()
        screen.clear()
        screen.refresh()


    def show_test_screen(self):
        screen = self.screen

        y = 5
        x = 5

        screen.addch(y+2, 25, curses.ACS_VLINE)

        curses.textpad.rectangle(screen, y+3, 24, y+4, 26)
        screen.addch(y+3, 25, curses.ACS_BTEE)
        curses.textpad.rectangle(screen, y+4, 23, y+5, 27)
        screen.addch(y+4, 24, curses.ACS_BTEE)
        screen.addch(y+4, 26, curses.ACS_BTEE)
        curses.textpad.rectangle(screen, y+5, 22, y+6, 28)
        screen.addch(y+5, 23, curses.ACS_BTEE)
        screen.addch(y+5, 27, curses.ACS_BTEE)
        curses.textpad.rectangle(screen, y+6, 21, y+7, 29)
        screen.addch(y+6, 22, curses.ACS_BTEE)
        screen.addch(y+6, 28, curses.ACS_BTEE)
        curses.textpad.rectangle(screen, y+7, 20, y+8, 30)
        screen.addch(y+7, 21, curses.ACS_BTEE)
        screen.addch(y+7, 29, curses.ACS_BTEE)

        #base
        screen.hline(y+8, 19, curses.ACS_HLINE, 13)
        screen.addch(y+8, 20, curses.ACS_BTEE)
        screen.addch(y+8, 30, curses.ACS_BTEE)

        screen.attrset(curses.color_pair(1))
        curses.textpad.rectangle(screen, y, 17, y+9, 33)
        screen.attrset(curses.color_pair(0))

        screen.getch()
        screen.clear()
        screen.refresh()


    def show_banner(self):
        self.screen.addstr(self.banner_box[T][Y], self.banner_box[T][X], 
                           "Hanoi".center(self.board_width))
        self.screen.refresh()


    def get_tower_bounding_box(self, tower_index):
        #Coords of top left of bounding box
        tl_y = self.tower_box[T][Y]
        tl_x = self.tower_box[T][X] + tower_index * (self.tower_width + GameView.tower_margin)

        #Coords of bottom right of bounding box
        br_y = tl_y + self.rings * GameView.ring_height + GameView.pillar_extension
        br_x = tl_x + self.tower_width

        return (tl_y, tl_x, br_y, br_x)


    def show_tower(self, rings, tower_index):

        tl_y, tl_x, br_y, br_x = self.get_tower_bounding_box(tower_index)

        x_mid = tl_x + int(self.tower_width / 2)
        pillar_height = br_y - tl_y


        #clear the area
        for i in range(br_y - tl_y):
            self.screen.hline(tl_y + i, tl_x, " ", br_x - tl_x)

        #plot the base
        self.screen.hline(br_y, tl_x, curses.ACS_HLINE, self.tower_width)

        #plot the rings
        rev_rings = rings[::-1]

        for i in range(len(rings)):
            ring = rev_rings[i]
            ring_width = self.ring_width(ring)
            curses.textpad.rectangle(self.screen, 
                br_y - ((i + 1) * GameView.ring_height), x_mid - int(ring_width / 2),
                br_y - i * GameView.ring_height, x_mid + int(ring_width / 2))

        #plot the central pillar
        for i in range(pillar_height - (len(rings) * GameView.ring_height)):
            self.screen.addch(tl_y + i, x_mid, curses.ACS_VLINE)

        self.screen.addch(tl_y + i + 1, x_mid, curses.ACS_BTEE)


    def ring_width(self, ring_value):
        """Calculates the width of a given ring"""
        return ring_value * GameView.ring_scaling + 1 + (GameView.min_ring_width - 3)


    def show_board(self, game):

        self.screen.clear()
        self.show_banner()

        for i in range(len(game.board)):
            self.show_tower(game.board[i], i)

        self.screen.refresh()



    def highlight_tower(self, game, tower_index, show=True):

        if show:
            self.screen.attrset(curses.color_pair(RED_ON_BLACK))
        else:
            self.screen.attrset(curses.color_pair(BLACK_ON_BLACK))
        
        tl_y, tl_x, br_y, br_x = self.get_tower_bounding_box(tower_index)

        margin = self.selection_margin

        curses.textpad.rectangle(self.screen,
            tl_y - margin, tl_x - margin - 1, br_y + margin, br_x + margin)

        self.screen.attrset(curses.color_pair(WHITE_ON_BLACK))
        self.screen.refresh()


    def show_selected_ring(self, ring):

        if ring == None:
            #clear the area
            for y in range(self.ring_box[T][Y], self.ring_box[B][Y]):
                self.screen.move(y, 0)
                self.screen.clrtoeol()

        else:

            ring_width = self.ring_width(ring)

            margin = int((self.board_width - ring_width) / 2 )

            y = int( (self.ring_box[T][Y] + self.ring_box[B][Y] - self.ring_height) / 2 )
            x = self.ring_box[T][X] + margin

            curses.textpad.rectangle(self.screen, 
                                     y, x, 
                                     y + self.ring_height, x + ring_width - 1)

        self.screen.refresh()


    def hide_top_ring(self, game, tower):

        self.show_tower(game.board[tower][1:], tower)
        self.screen.refresh()


    def input_move(self, game):

        self.highlight_tower(game, self.current_tower)

        source_tower = None
        while source_tower == None:

            command_chr = self.screen.getch()
            if command_chr == UP_KEY or command_chr == ord("k"):
                
                if len(game.board[self.current_tower]) > 0:
                    source_tower = self.current_tower
                    self.show_selected_ring(game.get_top_ring(source_tower))
                    self.hide_top_ring(game, source_tower)
                
            elif command_chr == LEFT_KEY or command_chr == ord("h"):

                if self.current_tower > 0 :
                    self.highlight_tower(game, self.current_tower, show=False)
                    self.current_tower -= 1
                    self.highlight_tower(game, self.current_tower)

            elif command_chr == RIGHT_KEY or command_chr == ord("l"):
                
                if self.current_tower < game.towers - 1:
                    self.highlight_tower(game, self.current_tower, show=False)
                    self.current_tower += 1
                    self.highlight_tower(game, self.current_tower)


        destination_tower = None
        while destination_tower == None:

            command_chr = self.screen.getch()
            if command_chr == DOWN_KEY or command_chr == ord("j"):
                destination_tower = self.current_tower
                self.show_selected_ring(None)

            elif command_chr == LEFT_KEY or command_chr == ord("h"):

                if self.current_tower > 0 :
                    self.highlight_tower(game, self.current_tower, show=False)
                    self.current_tower -= 1
                    self.highlight_tower(game, self.current_tower)

            elif command_chr == RIGHT_KEY or command_chr == ord("l"):

                if self.current_tower < game.towers - 1:
                    self.highlight_tower(game, self.current_tower, show=False)
                    self.current_tower += 1
                    self.highlight_tower(game, self.current_tower)

        return (source_tower, destination_tower)





#The Controller in an MVC pattern. 
def main(stdscr):

    curses.curs_set(0)

    game = Game()
    ui = GameView(stdscr, game)

    ui.show_splash_screen()
    #ui.show_test_screen()

    while not game.won:
        ui.show_board(game)

        source_tower, destination_tower = ui.input_move(game)

        try:
            game.move(source_tower, destination_tower)
        except ValueError as e:
            ui.show_message_box(str(e))
            ui.pause()

    ui.show_board(game)


    ui.show_message_box("You Won")
    ui.pause()


if __name__ == '__main__':
    curses.wrapper(main)
