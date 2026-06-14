#!/usr/bin/env python3
"""Проверяем что происходит после U"""
from backend.rubik.state import solved, apply_move, apply_sequence
from backend.rubik.pieces import read_corners, read_edges
from backend.rubik.cycles import parity, cycles_of

print("=== ШАГИ АЛГОРИТМА ===\n")

# Шаг 1: R
state = apply_move(solved(), "R")
cp, _ = read_corners(state)
cp_perm = [0] + [c + 1 for c in cp]
par = parity(cp_perm)
print(f"После R:")
print(f"  Паритет углов: {par} ({'нечетная' if par else 'четная'})")
if par == 1:
    print(f"  → Алгоритм добавляет U\n")
    
    # Шаг 2: R + U
    state = apply_sequence(state, ["U"])
    cp, _ = read_corners(state)
    cp_perm = [0] + [c + 1 for c in cp]
    par = parity(cp_perm)
    print(f"После R + U:")
    print(f"  Паритет углов: {par} ({'нечетная' if par else 'четная'})")
    
    cycles = cycles_of(cp_perm)
    print(f"  Циклы: {cycles}")
    print(f"  Углов не на месте: {sum(1 for s in range(8) if cp[s] != s)}")

print()

# Проверим что происходит если вместо U применить R'
print("=== СРАВНЕНИЕ ===\n")

state_r = apply_move(solved(), "R")
state_r_inv = apply_sequence(state_r, ["R'"])
print(f"После R + R': собран = {all(state_r_inv[i] == i for i in range(1, 55))}")

state_r_u = apply_sequence(apply_move(solved(), "R"), ["U"])
print(f"После R + U: углы на месте = {all(cp[s] == s for s, cp in enumerate(read_corners(state_r_u)[0]))}")
