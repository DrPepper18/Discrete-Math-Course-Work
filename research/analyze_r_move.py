#!/usr/bin/env python3
"""Анализ структуры нарушений от одного хода R"""
from backend.rubik.state import solved, apply_move
from backend.rubik.pieces import read_corners, read_edges
from backend.rubik.cycles import cycles_of

state = apply_move(solved(), "R")
cp, co = read_corners(state)
ep, eo = read_edges(state)

print("=== СТРУКТУРА НАРУШЕНИЙ ОТ ХОДА R ===\n")

# Перестановка углов
print("УГЛЫ:")
print(f"Перестановка: {cp}")
corners_perm = [0] + [c + 1 for c in cp]
cycles_c = cycles_of(corners_perm)
print(f"Циклы углов: {cycles_c}")
print(f"Количество циклов: {len(cycles_c)}")
print()

# Перестановка рёбер  
print("РЁБРА:")
print(f"Перестановка: {ep}")
edges_perm = [0] + [e + 1 for e in ep]
cycles_e = cycles_of(edges_perm)
print(f"Циклы рёбер: {cycles_e}")
print(f"Количество циклов: {len(cycles_e)}")
print()

# Ориентация
print("ОРИЕНТАЦИЯ:")
print(f"Углы ориентация: {co}")
print(f"Неправильных углов: {sum(1 for o in co if o != 0)}")
print(f"Сумма ориентаций углов: {sum(co)} (mod 3 = {sum(co) % 3})")
print()

print(f"Рёбра ориентация: {eo}")
print(f"Неправильных рёбер: {sum(1 for o in eo if o != 0)}")
print(f"Сумма ориентаций рёбер: {sum(eo)} (mod 2 = {sum(eo) % 2})")
print()

# Подсчёт нарушений
print("ИТОГО НАРУШЕНИЙ:")
print(f"Углов не на месте: {sum(1 for s in range(8) if cp[s] != s)}")
print(f"Рёбер не на месте: {sum(1 for s in range(12) if ep[s] != s)}")
print(f"Углов разориентировано: {sum(1 for o in co if o != 0)}")
print(f"Рёбер разориентировано: {sum(1 for o in eo if o != 0)}")
