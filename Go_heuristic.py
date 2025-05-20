""" Binôme :
    SALHI Mohammed-Amine
    TABET AOUL Hanaa
"""


from Goban import Board 
import numpy as np
import time
import json
from collections import Counter

# implémentation avec à faire

cache = {}

# calcul de la différence des libertés pour le calcul de l'heuristique

def sum_liberties(board):  

    cur = board.next_player()
    # vectorisation des libertés par chaîne pour accélérer
    roots = np.where(board._stringLiberties != -1)[0]
    libs = board._stringLiberties[roots]
    stones = board.get_board()[roots]
    own_libs = libs[stones == cur].sum()
    opp_libs = libs[(stones != cur) & (stones != Board._EMPTY)].sum()
    return int(own_libs - opp_libs)


def territories(board):
    return board._count_areas()


# Fonction de l'heuristique:

def heuristic(board):
    z = board._currentHash  # utilise le hash courant
    if z not in cache:
        ter = territories(board)
        black_ter = int(ter[0])
        white_ter = int(ter[1])
        liberties = sum_liberties(board)
        black_stones = int(board._nbBLACK)
        white_stones = int(board._nbWHITE)

        if board.next_player() == board._BLACK:
            sum_territories = black_ter - white_ter
            stone_diff = black_stones - white_stones
        else:
            sum_territories = white_ter - black_ter
            stone_diff = white_stones - black_stones

        cache[z] = int(sum_territories) + int(liberties) + int(stone_diff)
    return cache[z]


# L'une des idées retrouvées c'est le fait que plus on joue près du centre plus le coût est bon
# On ordonne alors suivant la distance

def order_moves(board, moves):
    center = Board._BOARDSIZE // 2
    def score_move(move):
        if move == -1:  
            return -1000  
        # coordonnées via opérations entières plutôt qu'unflatten
        x = move % Board._BOARDSIZE
        y = move // Board._BOARDSIZE
        center_dist = -((x - center)**2 + (y - center)**2)

        ok = board.push(move)
        captures = int(board._capturedBLACK) + int(board._capturedWHITE)
        board.pop()
        return int(center_dist) + captures * 10
    return sorted(moves, key=score_move, reverse=True)


# Fonction alpha beta

def alphabeta(board, depth, alpha, beta, maximizing, max_time, end_time):
    if time.perf_counter() > end_time:
        raise TimeoutError("Search timeout")
    
    if depth == 0 or board.is_game_over():
        return heuristic(board)

    if maximizing:
        value = float('-inf')
        # utilise weak_legal_moves pour vitesse
        moves = order_moves(board, board.weak_legal_moves())
        for move in moves:
            ok = board.push(move)
            if not ok:
                board.pop()
                continue
            try:
                child_val = alphabeta(board, depth - 1, alpha, beta, False, max_time, end_time)
                value = max(value, child_val)
                alpha = max(alpha, value)
            except TimeoutError:
                board.pop()
                raise
            board.pop()
            if alpha >= beta:
                break
        return value
    else:
        value = float('inf')
        moves = order_moves(board, board.weak_legal_moves())
        for move in moves:
            ok = board.push(move)
            if not ok:
                board.pop()
                continue
            try:
                child_val = alphabeta(board, depth - 1, alpha, beta, True, max_time, end_time)
                value = min(value, child_val)
                beta = min(beta, value)
            except TimeoutError:
                board.pop()
                raise
            board.pop()
            if beta <= alpha:
                break
        return value


# Utilisation de alpha beta pour chercher un bon mouvement dans des meilleurs délais

def best_move_alphabeta(board, depth, max_time, end_time):
    best_val = float('-inf')
    best_move = None
    moves = order_moves(board, board.legal_moves())
    
    for move in moves:
        if time.perf_counter() > end_time:
            break
        ok = board.push(move)
        if not ok:
            board.pop()
            continue
        try:
            val = alphabeta(board, depth - 1, float('-inf'), float('inf'), False, max_time, end_time)
            if val > best_val:
                best_val = val
                best_move = move
        except TimeoutError:
            pass
        finally:
            board.pop()

    if best_move is None and len(moves) > 0:
        best_move = moves[0]
    return best_move


# Fonction de l'iterative deepening

def iterative_deepening(board, max_time=1.0):
    start_time = time.perf_counter()
    end_time = start_time + max_time
    
    best_move = None
    max_depth = 8  
    
    for depth in range(1, max_depth + 1):
        try:
            current_best = best_move_alphabeta(board, depth, max_time, end_time)
            if current_best is not None:
                best_move = current_best
        except TimeoutError:
            break
        if time.perf_counter() > (end_time - 0.1):
            break

    if best_move is None:
        moves = board.weak_legal_moves()
        if moves:
            import random
            best_move = random.choice(moves)
    return best_move


# Choix raisonnable du coût d'ouverture en se basant sur le .json

def first_move(board):
    json_file = 'plays-8x8.json'
    current_player = board.next_player()
    try:
        with open(json_file, 'r') as f:
            games = json.load(f)
    except FileNotFoundError:
        print(f"Error: File {json_file} not found.")
        return "D4"  
    except json.JSONDecodeError:
        print(f"Error: File {json_file} contains invalid JSON.")
        return "D4"  
    
    winner = "BLACK" if current_player == Board._BLACK else "WHITE"
    
    # On regroupe les premiers coups gagnants pour le joueur courant
    winning_openings = []
    for game in games:
        if game["winner"] == winner and len(game["moves"]) > 0:
            winning_openings.append(game["moves"][0])
    
    if winning_openings:
        move_counts = Counter(winning_openings)
        best_move = move_counts.most_common(1)[0][0]
        print(f"Choosing move {best_move} which has led to {move_counts[best_move]} wins for {winner}")
        return best_move
    else:
        print(f"No winning moves found for {winner}, using default opening move")
        return "D4"  # Coup par défaut
