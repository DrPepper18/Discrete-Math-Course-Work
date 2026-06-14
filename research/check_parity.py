#!/usr/bin/env python3
"""Проверяем паритет перестановок от хода R"""
from backend.rubik.state import solved, apply_move
from backend.rubik.pieces import read_corners, read_edges
from backend.rubik.cycles import parity

state = apply_move(solved(), "R")
cp, co = read_corners(state)
ep, eo = read_edges(state)

# Получаем перестановки как в cycles.py (1-индексированные)
cp_perm = [0] + [c + 1 for c in cp]
ep_perm = [0] + [e + 1 for e in ep]

par_c = parity(cp_perm)
par_e = parity(ep_perm)

print(f"Паритет углов: {par_c} ({'четная' if par_c == 0 else 'нечетная'})")
print(f"Паритет рёбер: {par_e} ({'четная' if par_e == 0 else 'нечетная'})")
print(f"Паритеты совпадают: {par_c == par_e}")
print()

# Проверим отдельно
print("Углы перестановка:", cp_perm[1:])
print("Рёбра перестановка:", ep_perm[1:])
