"""
Alan M Jackson

A version of the Towers of Hanoi puzzle
"""


import curses
import curses.textpad
import argparse

_DEFAULT_TOWERS = 3
_DEFAULT_RINGS = 5
_DEFAULT_SETS = 1

DOWN_KEY = 258
UP_KEY = 259
LEFT_KEY = 260
RIGHT_KEY = 261

T = 0   # top coordinate of bounding box
B = 1   # bottom coordinate of bounding box
Y = 0   # Y part of coordinate
X = 1   # X part of coordinate

WHITE_ON_BLACK = 0
GREEN_ON_BLACK = 1
YELLOW_ON_BLACK = 2
BLUE_ON_BLACK = 3
CYAN_ON_BLACK = 4
MAGENTA_ON_BLACK = 5
RED_ON_BLACK = 6
BLACK_ON_BLACK = 7


#The Model in an MVC pattern - can be used without a view, implements the game logic.
class Game:

    def __init__(self, towers=_DEFAULT_TOWERS, rings=_DEFAULT_RINGS, sets=_DEFAULT_SETS):

        if sets > towers:
            raise ValueError("Can't have more sets than towers.")

        if towers < 1 or rings < 1 or sets < 1:
            raise ValueError("Towers, rings and sets must be greater than zero.")

        self.towers = towers
        self.rings = rings
        self.sets = sets
        self.board = [[] for x in range(self.towers)]
        self.winning_state = [[] for x in range(self.towers)]
        self.moves = 0

        #The first tower has a set
        towers_with_sets = [0]

        #The next set goes on the last tower
        if sets > 1:
            towers_with_sets.append(towers - 1)

        #Put the next sets on the towers in order
        if sets > 2:
            for i in range(1, sets - 1):
                towers_with_sets.append(i)

        set = 0
        for tower in towers_with_sets:
            for i in range(1, self.rings + 1):
                self.board[tower].append([i, set])

                #reverse the order of the towers for the winning state. 
                self.winning_state[self.towers - 1 - tower].append([i, set])
            set += 1

        self.won = False


    def valid_move(self, source_tower, destination_tower):

        #You can't move a ring from an empty tower
        if len(self.board[source_tower]) == 0:
            raise ValueError("Cannot move a ring from an empty tower.")

        #It's valid to move a ring to an empty tower
        if len(self.board[destination_tower]) == 0:
            return True

        #You can't put a ring on top of a smaller one
        if self.board[source_tower][0][0] > self.board[destination_tower][0][0]:
            raise ValueError("Cannot put a ring on top of a smaller ring.")


        return True


    def winning_condition(self):

        if self.board == self.winning_state:
            return True


    def move(self, source_tower, destination_tower):

        #If the source is the same as the desitination don't bother doing anything
        if source_tower != destination_tower:

            if self.valid_move(source_tower, destination_tower):

                ring = self.board[source_tower].pop(0)
                self.board[destination_tower].insert(0, ring)
                self.moves += 1

            if self.winning_condition():
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
    left_margin = 2
    min_tower_margin = 2        #The space between towers
    selection_margin = 1
    pillar_extension = 1    #Height that the pillar extends above the top ring.
    base_extension = 1      #The width the base extends wider than the largest ring on each side.
    min_ring_width = 5      #Width of the smallest ring
    ring_scaling = 2
    ring_height = 1
    score_width = 12


    def __init__(self, screen, game, debug=True):
        #Set up curses
        curses.curs_set(0)
        curses.init_pair(GREEN_ON_BLACK,   curses.COLOR_GREEN,   curses.COLOR_BLACK)
        curses.init_pair(YELLOW_ON_BLACK,  curses.COLOR_YELLOW,  curses.COLOR_BLACK)
        curses.init_pair(BLUE_ON_BLACK,    curses.COLOR_BLUE,    curses.COLOR_BLACK)
        curses.init_pair(CYAN_ON_BLACK,    curses.COLOR_CYAN,    curses.COLOR_BLACK)
        curses.init_pair(MAGENTA_ON_BLACK, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        self.ring_colours = 6

        curses.init_pair(RED_ON_BLACK,     curses.COLOR_RED,     curses.COLOR_BLACK)
        curses.init_pair(BLACK_ON_BLACK,   curses.COLOR_BLACK,   curses.COLOR_BLACK)

        self.screen_height, self.screen_width = screen.getmaxyx()
        self.banner_text = "Hanoi"

        self.rings = game.rings
        self.towers = game.towers
        self.tower_width = game.rings * GameView.ring_scaling + 1 + \
            (GameView.min_ring_width - 3) + GameView.base_extension * 2

        tower_widths = game.towers * self.tower_width
        self.tower_margin = max(int(((self.screen_width - tower_widths) / (self.towers - 1)) / 2), 
            self.min_tower_margin)

        self.board_width = tower_widths + (game.towers - 1) * self.tower_margin
        self.screen = screen
        self.current_tower = 0
        self.__DEBUG_SCR = screen.subwin(self.screen_height - 12, 0)

        x = GameView.left_margin
        self.banner_box = ((0, x),(3, x + self.board_width))   #(y,x) coords of top left & bottom right of bounding box
        self.ring_box = ((self.banner_box[B][Y], x), (self.banner_box[B][Y] + 3, x + self.board_width))

        self.tower_height = game.rings * self.ring_height * game.sets  \
                            - (game.sets - 1) \
                            + self.pillar_extension
        
        self.tower_box = ((self.ring_box[B][Y] + GameView.selection_margin, 
                           x + GameView.selection_margin), 
                          (self.ring_box[B][Y] + GameView.selection_margin + self.tower_height + 2, 
                            x + self.board_width))

        self.board_height = self.tower_box[B][Y]
        self.select_box =((self.tower_box[B][Y], x), (self.tower_box[B][Y] + 3, x + self.board_width)) 

        self.__debug = debug
        self.previous_move = None



    def show_message(self, message):
        self.screen.addstr(message)
        self.screen.refresh()


    def show_message_box(self, message):

        y = GameView.top_margin
        x = max(GameView.left_margin, self.score_width)
        height = 3
        width = self.board_width - (2 * x)

        msg_screen = self.screen.derwin(height, width, y, x)

        #clear the area
        msg_screen.clear()

        msg_screen.addstr(1, 0, message.center(width))

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

        msg_box = screen.subwin(22, 55, GameView.top_margin, GameView.left_margin)

        left = 2
        msg_box.addstr(1, left, "Hanoi".center(50))
        msg_box.addstr(10, left, "Move the discs in to the winning position.".center(50))
        msg_box.addstr(11, left, "You can't put a big disc on top of a smaller one.".center(50))
        
        msg_box.addstr(13, left, "Use LEFT and RIGHT arrow keys to select a tower.".center(50))
        msg_box.addstr(14, left, "Use UP and DOWN to pick up and place a disc.".center(50))

        msg_box.addstr(16, left, "Press W to see the winning position.".center(50))
        msg_box.addstr(17, left, "Press A to repeat the last move.".center(50))

        msg_box.addstr(19, left, "Press any key to continue...".center(50))

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


    def show_score(self, game):
        self.screen.addstr(self.banner_box[T][Y] + 1, self.banner_box[B][X] - self.score_width,
                           "moves: " + str(game.moves))
        self.screen.refresh()


    def show_banner(self):

        #clear the area
        for y in range(self.banner_box[T][Y], self.banner_box[B][Y]):
            self.screen.move(y, 0)
            self.screen.clrtoeol()

        self.screen.addstr(self.banner_box[T][Y], self.banner_box[T][X], 
                           self.banner_text.center(self.board_width))
        self.screen.refresh()


    def get_tower_bounding_box(self, tower_index):
        #Coords of top left of bounding box
        tl_y = self.tower_box[T][Y]
        tl_x = self.tower_box[T][X] + tower_index * (self.tower_width + self.tower_margin)

        #Coords of bottom right of bounding box
        br_y = tl_y + self.tower_height
        br_x = tl_x + self.tower_width

        return (tl_y, tl_x, br_y, br_x)


    def show_tower(self, rings, tower_index):

        tl_y, tl_x, br_y, br_x = self.get_tower_bounding_box(tower_index)

        x_mid = tl_x + int(self.tower_width / 2)
        pillar_height = self.tower_height


        #clear the area
        for i in range(br_y - tl_y):
            self.screen.hline(tl_y + i, tl_x, " ", br_x - tl_x)

        #plot the base
        self.screen.hline(br_y, tl_x, curses.ACS_HLINE, self.tower_width)
        self.screen.addch(br_y, x_mid, curses.ACS_BTEE)

        #plot the rings
        rev_rings = rings[::-1]

        for i in range(len(rings)):
            ring_value = rev_rings[i][0]
            ring_set = rev_rings[i][1]
            ring_width = self.ring_width(ring_value)

            self.screen.attrset(curses.color_pair(ring_set % self.ring_colours))
            curses.textpad.rectangle(self.screen, 
                br_y - ((i + 1) * GameView.ring_height), x_mid - int(ring_width / 2),
                br_y - i * GameView.ring_height, x_mid + int(ring_width / 2))

            self.screen.attrset(curses.color_pair(WHITE_ON_BLACK))

        #plot the central pillar
        for i in range(pillar_height - (len(rings) * GameView.ring_height)):
            self.screen.addch(tl_y + i, x_mid, curses.ACS_VLINE)



    def ring_width(self, ring_value):
        """Calculates the width of a given ring"""
        return ring_value * GameView.ring_scaling + 1 + (GameView.min_ring_width - 3)


    def show_towers(self, board):

        #clear the area
        for y in range(self.tower_box[T][Y], self.tower_box[B][Y]):
            self.screen.move(y, 0)
            self.screen.clrtoeol()

        for i in range(len(board)):
            self.show_tower(board[i], i)

        self.screen.refresh()


    def show_board(self, game):
        """Repaint the whole board screen"""

        self.screen.clear()
        self.show_banner()
        self.show_score(game)
        self.show_towers(game.board)
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

            ring_width = self.ring_width(ring[0])

            margin = int((self.board_width - ring_width) / 2 ) + 1

            y = int( (self.ring_box[T][Y] + self.ring_box[B][Y] - self.ring_height) / 2 )
            x = self.ring_box[T][X] + margin

            self.screen.attrset(curses.color_pair(ring[1] % self.ring_colours))
            curses.textpad.rectangle(self.screen, 
                                     y, x, 
                                     y + self.ring_height, x + ring_width - 1)

            self.screen.attrset(curses.color_pair(WHITE_ON_BLACK))


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


            elif command_chr == ord("w"):

                self.show_winning_state(game)
                self.show_board(game)

            elif command_chr == DOWN_KEY or command_chr == ord("j") or command_chr == ord("a"):

                if self.previous_move != None:
                    return self.previous_move


        destination_tower = None
        while destination_tower == None:

            command_chr = self.screen.getch()
            if command_chr == DOWN_KEY or command_chr == ord("j") or command_chr == ord("a"):
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

            elif command_chr == ord("w"):

                self.show_winning_state(game)
                self.show_board(game)
                self.show_selected_ring(game.get_top_ring(source_tower))
                self.hide_top_ring(game, source_tower)

        self.previous_move = (source_tower, destination_tower)
        return (source_tower, destination_tower)


    def show_winning_state(self, game):

        self.show_towers(game.winning_state)
        banner_text = self.banner_text
        self.banner_text = "Winning Position"
        self.show_banner()
        self.pause()
        self.banner_text = banner_text





#The Controller in an MVC pattern. 
def main(stdscr, args):

    game_kwargs = {}
    distribution = 0.75

    if args.towers != None:
        game_kwargs['towers'] = args.towers

    if args.rings != None:
        game_kwargs['rings'] = args.rings

    if args.sets != None:
        game_kwargs['sets'] = args.sets


    game = Game(**game_kwargs)
    ui = GameView(stdscr, game)

    if not args.quiet:
        ui.show_splash_screen()
        ui.show_winning_state(game)

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
    argparser = argparse.ArgumentParser(description='A game of moving rings on towers.')
    argparser.add_argument('-t', '--towers', type=int)
    argparser.add_argument('-r', '--rings', type=int)
    argparser.add_argument('-s', '--sets', type=int)
    argparser.add_argument('-q', '--quiet', action='store_true')

    args = argparser.parse_args()

    curses.wrapper(main, args)
