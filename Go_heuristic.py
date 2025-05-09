from Goban import Board 
import numpy as np
import time
def sum_liberties(board):  
    #parcours board
    liberties = 0
    current_player = board.next_player()
    board_list = board.get_board()
    for i in range(len(board_list)):
        if board_list[i] == 0:
            continue
        if board_list[i] == current_player:
            id_stone = board._getStringOfStone(i)
            liberties += board._stringLiberties[id_stone]
        else:
            id_stone = board._getStringOfStone(i)
            liberties -= board._stringLiberties[id_stone]
            
    return liberties


def territories(board):
    return board._count_areas()

def heuristic(board):
    print("counting heuristic")
    ter = territories(board)
    black_ter = np.sum(ter[0])
    white_ter = np.sum(ter[1])
    liberties = sum_liberties(board)
    if board.next_player() == board._BLACK:
        sum_territories = black_ter - white_ter
    else:
        sum_territories = white_ter - black_ter
    return sum_territories + liberties


def alphabeta(board, depth, alpha, beta, maximizing):
    if depth == 0 or board.is_game_over():
        return heuristic(board)
    print("counting alphabeta")

    if maximizing:
        value = float('-inf')
        for move in board.weak_legal_moves():
            board.push(move)
            value = max(value, alphabeta(board, depth - 1, alpha, beta, False))
            board.pop()
            alpha = max(alpha, value)
            if alpha >= beta:
                break  # coupure
        return value
    else:
        value = float('inf')
        for move in board.weak_legal_moves():
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
    for move in board.weak_legal_moves():
        board.push(move)
        val = alphabeta(board, depth - 1, float('-inf'), float('inf'), False)
        board.pop()
        if val > best_val:
            best_val = val
            best_move = move
    print(best_move)
    return best_move


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
