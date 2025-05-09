import Board from Goban 
import numpy as np

def sum_liberties(board):  
    #parcours board
    liberties = 0
    current_player = board._next_player
    board_list = board.get_board()
    for i in range(len(board_list)):
        if board[i] == current_player:
            id_stone = board._getStringOfStone(i)
            liberties += board._stringLiberties[id_stone]
        else:
            id_stone = board._getStringOfStone(i)
            liberties -= board._stringLiberties[id_stone]
            
    return liberties


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
