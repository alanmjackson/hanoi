''' 
unit test for hanoi.py
Alan M Jackson 
'''

import unittest

import hanoi

class Test(unittest.TestCase):
    
    def test_new_game(self):

        game = hanoi.Game()

        self.assertTrue(game != None)
        self.assertTrue(game.towers == 3)
        self.assertTrue(game.rings == 5)
        self.assertTrue(len(game.board) == 3)
        self.assertTrue(game.board[0][0] == 1)
        self.assertTrue(len(game.board[0]) == 5)
        self.assertTrue(game.board[0][4] == 5)

    def test_legal_move(self):

        game = hanoi.Game()

        game.move(0,2)

        self.assertTrue(game.board[0][0] == 2)
        self.assertTrue(game.board[2][0] == 1)


    def test_illegal_move(self):

        game = hanoi.Game()

        game.move(0,2)

        err = None
        try:
            game.move(0,2)
        except ValueError as e:
            err = e

        self.assertTrue(err != None)
        print err


    def test_winning(self):

        game = hanoi.Game(2, 1)

        game.move(0, 1)

        self.assertTrue(game.won)




if __name__ == "__main__":
    unittest.main()


