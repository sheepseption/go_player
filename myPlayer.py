# -*- coding: utf-8 -*-
''' This is the file you have to modify for the tournament. Your default AI player must be called by this module, in the
myPlayer class.

Right now, this class contains the copy of the randomPlayer. But you have to change this!
'''

import time
import Goban 
from Go_heuristic import iterative_deepening, first_move 
from random import choice
from playerInterface import *

class myPlayer(PlayerInterface):
    ''' Example of a random player for the go. The only tricky part is to be able to handle
    the internal representation of moves given by legal_moves() and used by push() and 
    to translate them to the GO-move strings "A1", ..., "J8", "PASS". Easy!

    '''

    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None

    def getPlayerName(self):
        return "efficient_player"

    def getPlayerMove(self):
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS" 
        
        # If this is the first move of the game, play near center
        #if (self._board._nbBLACK == 0) and (self._board._nbWHITE == 0):
            # Play near center for first move
        #    center = Goban.Board._BOARDSIZE // 2
            # Slightly offset from true center
        #    move = Goban.Board.flatten((center, center-1))
        # choisir le move d'ouverture suivant play-8x8.json
        if (self._board._nbBLACK == 0) and (self._board._nbWHITE == 0):
            move = first_move(self._board)
        else:
            # Use iterative deepening with a reasonable time limit
            move = iterative_deepening(self._board, max_time=1.0)
            
        # Make sure move is valid
        if move is None or not move in self._board.weak_legal_moves():
            # Fallback to a random legal move
            moves = self._board.legal_moves()
            move = choice(moves)
            
        self._board.push(move)

        # Convert to string representation for interface
        move_str = Goban.Board.flat_to_name(move)
        return move_str

    def playOpponentMove(self, move):
        # Convert from string to internal representation
        flat_move = Goban.Board.name_to_flat(move)
        self._board.push(flat_move)

    def newGame(self, color):
        # Reset board state completely for new game
        self._board = Goban.Board()
        self._mycolor = color
        self._opponent = Goban.Board.flip(color)

    def endGame(self, winner):
        pass  # Nothing to clean up at game end