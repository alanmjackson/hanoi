'''
Alan M Jackson

A version of the Towers of Hanoi puzzle
'''


_DEFAULT_TOWERS = 3
_DEFAULT_RINGS = 5


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

            if len(self.board[destination_tower]) == self.rings:
                self.won = True



def show_board(game):

    board_display = [["." for y in range(game.towers)] for x in range(game.rings)]

    for tower_index in range(len(game.board)):
        height = len(game.board[tower_index])

        for ring_index in range(height):
            offset = game.rings - height
            board_display[offset + ring_index][tower_index] = game.board[tower_index][ring_index]


    print("")
    for row in board_display:
        row_str = " "
        for item in row:
            row_str += " " + str(item) + "  "

        print(row_str)

    tower_bases = " "
    for i in range(game.towers):
        tower_bases += "-+- "

    print(tower_bases)
    print("")



def input_tower(prompt, max):

    tower_number = None

    while tower_number == None:

        user_input = raw_input(prompt)

        if user_input.isdigit():
            value = int(user_input)
            if value > 0 and value <= max:
                return value

        print("Enter a number from 1 to " + str(max))



def main():
    print "Hanoi!"

    game = Game()

    while not game.won:
        show_board(game)

        source_tower = input_tower("move from: ", game.towers)
        destination_tower = input_tower("move to: ", game.towers)

        try:
            game.move(source_tower - 1, destination_tower - 1)
        except ValueError as e:
            print e

    show_board(game)
    print("\n\n")
    print("=" * 20)
    print("You Won!!! \n\n\n")



if __name__ == '__main__':
    main()
