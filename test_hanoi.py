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
        #game should raise a ValueError for an illegal move.

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

        #Test that you only win if you get all the rings to the farthest tower.
        game = hanoi.Game(3, 2)
        game.move(0, 2)
        game.move(0, 1)
        game.move(2, 1)
        self.assertTrue(game.won == False)  #All rings are on the middle tower

        game = hanoi.Game(3, 2)
        game.move(0, 1)
        game.move(0, 2)
        game.move(1, 2)
        self.assertTrue(game.won)   #All rings on the farthest tower.



    def test_get_top_ring(self):

        game = hanoi.Game()

        ring = game.get_top_ring(0) # What is the top ring on tower 0?
        self.assertTrue(ring == 1)

        ring = game.get_top_ring(1) 
        self.assertTrue(ring == None)        

        game.move(0,2)

        ring = game.get_top_ring(0) # What is the top ring on tower 0 now?
        self.assertTrue(ring == 2)


    def test_create_multiple_sets_game(self):

        game = hanoi.Game(sets = 2)

        self.assertTrue(len(game.board[0]) == game.rings)
        self.assertTrue(len(game.board[game.towers - 1]) == game.rings)





if __name__ == "__main__":
    unittest.main()


