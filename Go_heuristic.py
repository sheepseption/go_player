from Goban import Board 
import numpy as np
import time

cache = {}

def sum_liberties(board):  
    """Calculate the difference in liberties between current player and opponent"""
    liberties = 0
    current_player = board.next_player()
    board_list = board.get_board()
    for i in range(len(board_list)):
        if board_list[i] == 0:
            continue
        if board_list[i] == current_player:
            id_stone = board._getStringOfStone(i)
            liberties += int(board._stringLiberties[id_stone])
        else:
            id_stone = board._getStringOfStone(i)
            liberties -= int(board._stringLiberties[id_stone])
            
    return liberties

def territories(board):
    """Get territory information from the board"""
    return board._count_areas()

def _raw_heuristic(board):
    """Ancien contenu de heuristic(...) sans cache."""
    ter = board._count_areas()
    black_ter, white_ter = int(ter[0]), int(ter[1])
    liberties = sum_liberties(board)
    black_stones = int(board._nbBLACK)
    white_stones = int(board._nbWHITE)
    if board.next_player() == board._BLACK:
        sum_territories = black_ter - white_ter
        stone_diff     = black_stones - white_stones
    else:
        sum_territories = white_ter - black_ter
        stone_diff     = white_stones - black_stones
    return sum_territories + liberties + stone_diff

# 4) Nouvelle version de heuristic avec cache
def heuristic(board):
    z = compute_zobrist_hash(board)
    if z not in cache:
        cache[z] = _raw_heuristic(board)
    return cache[z]

def order_moves(board, moves):
    """Simple move ordering to improve alphabeta efficiency"""
    # Center moves are often better in Go
    center = Board._BOARDSIZE // 2
    
    # Score moves based on distance to center and other metrics
    def score_move(move):
        if move == -1:  # PASS move
            return -1000  # Low priority for passing
        
        x, y = Board.unflatten(move)
        # Distance to center (negative so closer is better)
        center_dist = -((x - center)**2 + (y - center)**2)
        
        # Check if move captures opponent stones
        board.push(move)
        captures = int(board._capturedBLACK + board._capturedWHITE)
        board.pop()
        
        return int(center_dist) + captures * 10
        
    # Return moves sorted by score (best first)
    return sorted(moves, key=score_move, reverse=True)

def compute_zobrist_hash(board):
    flat = board.get_board()
    h = 0
    for i, stone in enumerate(flat):
        if stone == board._BLACK:
            h ^= int(board._positionHashes[i, 0])
        elif stone == board._WHITE:
            h ^= int(board._positionHashes[i, 1])
    return h


def alphabeta(board, depth, alpha, beta, maximizing, max_time, end_time):
    """Alpha-beta pruning algorithm with time limit"""
    # Check if time is up
    if time.perf_counter() > end_time:
        raise TimeoutError("Search timeout")
        
    if depth == 0 or board.is_game_over():
        return heuristic(board)

    if maximizing:
        value = float('-inf')
        
        moves = order_moves(board, board.legal_moves())
        for move in moves:
            if not board.push(move):  # Superko rule violation
                board.pop()
                continue
                
            try:
                value = max(value, alphabeta(board, depth - 1, alpha, beta, False, max_time, end_time))
            except TimeoutError:
                board.pop()
                raise
                
            board.pop()
            alpha = max(alpha, value)
            if alpha >= beta:
                break  # Beta cutoff
        return value
    else:
        value = float('inf')
        moves = order_moves(board, board.legal_moves())
        for move in moves:
            if not board.push(move):  # Superko rule violation
                board.pop()
                continue
                
            try:
                value = min(value, alphabeta(board, depth - 1, alpha, beta, True, max_time, end_time))
            except TimeoutError:
                board.pop()
                raise
                
            board.pop()
            beta = min(beta, value)
            if beta <= alpha:
                break  # Alpha cutoff
        return value

def best_move_alphabeta(board, depth, max_time, end_time):
    """Find best move using alpha-beta with time limit"""
    best_val = float('-inf')
    best_move = None
    moves = order_moves(board, board.legal_moves())
    
    for move in moves:
        if time.perf_counter() > end_time:
            break
            
        if not board.push(move):  # Handle superko rule
            board.pop()
            continue
            
        try:
            val = alphabeta(board, depth - 1, float('-inf'), float('inf'), False, max_time, end_time)
            if val > best_val:
                best_val = val
                best_move = move
        except TimeoutError:
            pass  # Just use best move found so far
        finally:
            board.pop()
    
    # If no move was evaluated (due to immediate timeout), pick the first legal one
    if best_move is None and len(moves) > 0:
        best_move = moves[0]
        
    return best_move

def iterative_deepening(board, max_time=1.0):
    """Iterative deepening with time limit"""
    start_time = time.perf_counter()
    end_time = start_time + max_time
    
    best_move = None
    max_depth = 8  # Reasonable maximum depth
    
    for depth in range(1, max_depth + 1):
        try:
            current_best = best_move_alphabeta(board, depth, max_time, end_time)
            if current_best is not None:
                best_move = current_best
        except TimeoutError:
            break
            
        # Check if we're running out of time
        if time.perf_counter() > (end_time - 0.1):  # Save 100ms for cleanup
            break
            
    # Return the best move found, or a random legal move if none was found
    if best_move is None:
        moves = board.weak_legal_moves()
        if moves:
            import random
            best_move = random.choice(moves)
            
    return best_move