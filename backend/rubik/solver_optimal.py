"""Оптимальное решение кубика Рубика методом двустороннего BFS."""
import time
from .state import solved, apply_move, MOVE_LABELS, invert_sequence
from .pieces import pieces_solved
from .geometry import inverse_label


def solve_bfs_limited(state, max_depth=8, timeout=5.0, verbose=False):
    if pieces_solved(state):
        return [], 0
    
    start_time = time.time()
    target = tuple(solved())
    state_tuple = tuple(state)
    
    forward = {state_tuple: ([], 0)}
    curr_level_f = {state_tuple}
    
    backward = {target: ([], 0)}
    curr_level_b = {target}
    
    depth = 0
    
    while depth < max_depth:
        if time.time() - start_time > timeout:
            return None, None
        
        if verbose and depth % 2 == 0:
            print(f"  BFS depth {depth}: |F|={len(forward)}, |B|={len(backward)}")
        
        # Расширяем меньший слой для экономии памяти
        if len(curr_level_f) <= len(curr_level_b) and curr_level_f:
            next_level = set()
            for state_t in curr_level_f:
                moves_f, d_f = forward[state_t]
                state_list = list(state_t)
                
                for move in MOVE_LABELS:
                    next_state = tuple(apply_move(state_list, move))
                    
                    if next_state in backward:
                        moves_b, _ = backward[next_state]
                        # Соединяем: путь вперед + текущий ход + инвертированный путь назад
                        solution = moves_f + [move] + invert_sequence(moves_b)
                        if verbose:
                            print(f"  ✓ Optimal solution found: {len(solution)} moves")
                        return solution, len(solution)
                    
                    if next_state not in forward:
                        forward[next_state] = (moves_f + [move], d_f + 1)
                        next_level.add(next_state)
            
            curr_level_f = next_level
            depth += 1
        
        elif curr_level_b:
            next_level = set()
            for state_t in curr_level_b:
                moves_b, d_b = backward[state_t]
                state_list = list(state_t)
                
                for move in MOVE_LABELS:
                    inv_move = inverse_label(move)
                    next_state = tuple(apply_move(state_list, inv_move))
                    
                    if next_state in forward:
                        moves_f, _ = forward[next_state]
                        # Корректный стык при обратном поиске
                        solution = moves_f + [move] + invert_sequence(moves_b)
                        if verbose:
                            print(f"  ✓ Optimal solution found: {len(solution)} moves")
                        return solution, len(solution)
                    
                    if next_state not in backward:
                        backward[next_state] = (moves_b + [inv_move], d_b + 1)
                        next_level.add(next_state)
            
            curr_level_b = next_level
            depth += 1
        else:
            break
            
    return None, None


def solve_optimal(state, verbose=False):
    """Находит оптимальное решение или хорошее приближение."""
    from .solver import solve as solve_commutator
    
    # Сначала пробуем оптимальный BFS
    solution, _ = solve_bfs_limited(state, max_depth=8, timeout=5.0, verbose=verbose)
    
    if solution is not None:
        if verbose:
            print(f"✓ BFS found optimal solution: {len(solution)} moves")
        return solution
    
    if verbose:
        print("BFS timeout, using commutator method...")
    
    # Fallback
    return solve_commutator(state)

