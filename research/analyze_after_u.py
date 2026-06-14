#!/usr/bin/env python3
"""Анализируем что происходит после U на кубе R"""
from backend.rubik.state import apply_sequence, solved
from backend.rubik.pieces import read_corners, read_edges
from backend.rubik.cycles import cycles_of, perm_to_3cycles

# R + U
state = apply_sequence(solved(), ["R", "U"])

cp, co = read_corners(state)
ep, eo = read_edges(state)

cp_perm = [0] + [c + 1 for c in cp]
ep_perm = [0] + [e + 1 for e in ep]

print("После R + U:\n")

print("УГЛЫ:")
cycles_c = cycles_of(cp_perm)
print(f"  Циклы: {cycles_c}")
threes_c, transps_c = perm_to_3cycles(cp_perm)
print(f"  3-циклы: {threes_c}")
print(f"  Транспозиции: {transps_c}")
print()

print("РЁБРА:")
cycles_e = cycles_of(ep_perm)
print(f"  Циклы: {cycles_e}")
threes_e, transps_e = perm_to_3cycles(ep_perm)
print(f"  3-циклы: {threes_e}")
print(f"  Транспозиции: {transps_e}")
print()

# Теперь протестируем алгоритм
from backend.rubik.solver import solve

print("Решаем куб R + U:")
try:
    solution = solve(apply_sequence(solved(), ["R"]))
    print(f"✓ Решено в {len(solution)} ходов")
    print(f"  Первые 30: {' '.join(solution[:30])}")
except Exception as e:
    print(f"✗ Ошибка: {e}")
