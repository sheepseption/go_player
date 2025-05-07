import time
import chess
from random import randint, choice

def randomMove(b):
    '''Renvoie un mouvement au hasard sur la liste des mouvements possibles. Pour avoir un choix au hasard, il faut
    construire explicitement tous les mouvements. Or, generate_legal_moves() nous donne un itérateur.'''
    return choice([m for m in b.generate_legal_moves()])

def deroulementRandom(b):
    '''Déroulement d'une partie d'échecs au hasard des coups possibles. Cela va donner presque exclusivement
    des parties très longues et sans gagnant. Cela illustre cependant comment on peut jouer avec la librairie
    très simplement.'''
    print("----------")
    print(b)
    if b.is_game_over():
        print("Resultat : ", b.result())
        return
    b.push(randomMove(b))
    deroulementRandom(b)
    b.pop()


def explore_chess_tree(b, depth):
    if depth == 0 or b.is_game_over():
        return 1  # 1 nœud exploré
    count = 0
    for move in b.legal_moves:
        b.push(move)
        count += explore_chess_tree(b, depth - 1)
        b.pop()
    return count


def shannon_heuristic(board):
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }
    score = 0
    for piece_type in piece_values:
        score += len(board.pieces(piece_type, chess.WHITE)) * piece_values[piece_type]
        score -= len(board.pieces(piece_type, chess.BLACK)) * piece_values[piece_type]
    return score



def minimax(board, depth, maximizing):
    if depth == 0 or board.is_game_over():
        return shannon_heuristic(board)

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



def random_vs_minimax():
    board = chess.Board()
    while not board.is_game_over():
        if board.turn == chess.WHITE:
            move = randomMove(board)  # joueur aléatoire
        else:
            move = best_move_minimax(board, 3)  # minimax niveau 3
        board.push(move)
    print("Résultat :", board.result())


def minimax_vs_minimax():
    board = chess.Board()
    while not board.is_game_over():
        move = best_move_minimax(board, 1) if board.turn == chess.WHITE else best_move_minimax(board, 3)
        board.push(move)
    print("Résultat :", board.result())


board = chess.Board()
deroulementRandom(board)


def alphabeta(board, depth, alpha, beta, maximizing):
    if depth == 0 or board.is_game_over():
        return shannon_heuristic(board)

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


opening_book = {
    (): "e2e4",
    ("e2e4",): "e7e5",
    ("e2e4", "e7e5"): "g1f3",
    ("d2d4",): "d7d5",
}

def opening_move(board):
    moves_played = tuple(str(m) for m in board.move_stack)
    if moves_played in opening_book:
        return chess.Move.from_uci(opening_book[moves_played])
    return None


def smart_move(board, time_limit=3.0):
    move = opening_move(board)
    if move:
        print("→ Ouverture")
        return move
    print("→ IA (Iterative Deepening)")
    return iterative_deepening(board, time_limit)


def play_vs_random_smart():
    board = chess.Board()
    move_count = 0
    while not board.is_game_over() and move_count < 100:
        print(board, '\n')
        if board.turn == chess.WHITE:
            move = randomMove(board)
        else:
            move = smart_move(board, time_limit=2)
        board.push(move)
        move_count += 1
    print("Résultat :", board.result())


def human_move(board):
    while True:
        print("Votre coup (format e2e4) : ", end="")
        user_input = input().strip()
        try:
            move = chess.Move.from_uci(user_input)
            if move in board.legal_moves:
                return move
            else:
                print("Coup illégal.")
        except:
            print("Format invalide. Exemple correct : e2e4")


def play_human_vs_ai():
    board = chess.Board()
    print("Vous êtes les Blancs. Jouez contre l'IA noire (alpha-bêta + ouvertures)")
    print(board)
    while not board.is_game_over():
        if board.turn == chess.WHITE:
            move = human_move(board)
        else:
            move = smart_move(board, time_limit=2)
            print("IA joue :", move)
        board.push(move)
        print(board, '\n')

    print("Résultat :", board.result())


