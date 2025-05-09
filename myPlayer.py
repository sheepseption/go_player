# -*- coding: utf-8 -*-
''' This is the file you have to modify for the tournament. Your default AI player must be called by this module, in the
myPlayer class.

Right now, this class contains the copy of the randomPlayer. But you have to change this!
'''

import time
import Goban 
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
        return "best player"

    def getPlayerMove(self):
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS" 
        moves = self._board.legal_moves() # Dont use weak_legal_moves() here!
        move = choice(moves) 
        self._board.push(move)

        # New here: allows to consider internal representations of moves
        print("I am playing ", self._board.move_to_str(move))
        print("My current board :")
        self._board.prettyPrint()
        # move is an internal representation. To communicate with the interface I need to change if to a string
        return Goban.Board.flat_to_name(move) 

    def playOpponentMove(self, move):
        print("Opponent played ", move) # New here
        # the board needs an internal represetation to push the move.  Not a string
        self._board.push(Goban.Board.name_to_flat(move)) 

    def newGame(self, color):
        self._mycolor = color
        self._opponent = Goban.Board.flip(color)

    def endGame(self, winner):
        if self._mycolor == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")




def sum_liberties(board):    
    return np.sum(Board._stringLiberties)

def territories(board):
    return Board._count_areas()

def heuristic(board):
    if Board._next_player == Board._BLACK:
        sum_territories = np.sum(territories(board)[0]) - np.sum(territories(board[1]))
        liberties = sum_liberties(board)
    else:
        sum_territories = np.sum(territories(board)[1]) - np.sum(territories(board[0]))
        liberties = sum_liberties(board)
    return sum_territories + liberties

def minimax(board, depth, maximizing):
    if depth == 0 or board.is_game_over():
        return heuristic(board)

    if maximizing:
        max_eval = float('-inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, False)
            board.pop()
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, True)
            board.pop()
            min_eval = min(min_eval, eval)
        return min_eval


def best_move_minimax(board, depth):
    best_val = float('-inf')
    best_move = None
    for move in board.legal_moves:
        board.push(move)
        val = minimax(board, depth - 1, False)
        board.pop()
        if val > best_val:
            best_val = val
            best_move = move
    return best_move

def alphabeta(board, depth, alpha, beta, maximizing):
    if depth == 0 or board.is_game_over():
        return heuristic(board)

    if maximizing:
        value = float('-inf')
        for move in board.legal_moves:
            board.push(move)
            value = max(value, alphabeta(board, depth - 1, alpha, beta, False))
            board.pop()
            alpha = max(alpha, value)
            if alpha >= beta:
                break  # coupure
        return value
    else:
        value = float('inf')
        for move in board.legal_moves:
            board.push(move)
            value = min(value, alphabeta(board, depth - 1, alpha, beta, True))
            board.pop()
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value

def best_move_alphabeta(board, depth):
    best_val = float('-inf')
    best_move = None
    for move in board.legal_moves:
        board.push(move)
        val = alphabeta(board, depth - 1, float('-inf'), float('inf'), False)
        board.pop()
        if val > best_val:
            best_val = val
            best_move = move
    return best_move

#à revoir
def iterative_deepening(board, max_time=5.0):
    start_time = time.perf_counter()
    best = None
    depth = 1
    while time.perf_counter() - start_time < max_time:
        try:
            best = best_move_alphabeta(board, depth)
            depth += 1
        except Exception:
            break
    return best