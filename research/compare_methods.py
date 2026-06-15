#!/usr/bin/env python3
"""Полное сравнение: коммутаторный метод vs оптимальный BFS"""
from backend.rubik.state import apply_move, apply_sequence, solved, scramble
from backend.rubik.solver import solve as solve_commutator
from backend.rubik.solver_optimal import solve_optimal

test_cases = [
    ("R", ["R"]),
    ("U", ["U"]),
    ("F", ["F"]),
    ("R U", ["R", "U"]),
    ("R U R'", ["R", "U", "R'"]),
    ("R U R' U'", ["R", "U", "R'", "U'"]),
    ("R U R' U' (x6)", ["R", "U", "R'", "U'"] * 6),  # 24 хода на самом деле
]

print("=" * 80)
print("СРАВНЕНИЕ: Коммутаторный метод vs Оптимальный BFS")
print("=" * 80)

for name, scramble_moves in test_cases:
    state = apply_sequence(solved(), scramble_moves)
    
    print(f"\nТест: {name}")
    print(f"  Скрэмбл ходов: {len(scramble_moves)}")
    
    # Коммутаторный метод
    try:
        sol_comm = solve_commutator(state)
        len_comm = len(sol_comm)
    except Exception as e:
        len_comm = None
        print(f"    Коммутаторный метод: ОШИБКА - {e}")
    
    # Оптимальный BFS
    try:
        sol_opt = solve_optimal(state, verbose=False)
        len_opt = len(sol_opt)
    except Exception as e:
        len_opt = None
        print(f"    Оптимальный метод: ОШИБКА - {e}")
    
    if len_comm is not None and len_opt is not None:
        ratio = len_comm / len_opt if len_opt > 0 else 0
        print(f"  Коммутаторный: {len_comm:3d} ходов")
        print(f"  Оптимальный:   {len_opt:3d} ходов (улучшение в {ratio:.1f}x)")
    elif len_opt is not None:
        print(f"  Оптимальный:   {len_opt:3d} ходов [V]")
    elif len_comm is not None:
        print(f"  Коммутаторный: {len_comm:3d} ходов (оптимальный не работал)")

print("\n" + "=" * 80)
