#!/usr/bin/env python3
"""Быстрая проверка: отменяет ли R' ход R?"""
from backend.rubik.state import solved, apply_move, is_solved
from backend.rubik.solver import solve

# Применяем R
state1 = apply_move(solved(), "R")
print(f"После R: собран={is_solved(state1)}")

# Применяем R'
state2 = apply_move(state1, "R'")
print(f"После R': собран={is_solved(state2)}")

# Пытаемся решить через алгоритм
print("\nТестируем алгоритм на одном ходе R:")
state1 = apply_move(solved(), "R")
solution = solve(state1)
print(f"Найдено решение в {len(solution)} ходов: {' '.join(solution[:30])}{'...' if len(solution) > 30 else ''}")

# Проверим что в решении есть
print(f"\nПервые 20 ходов: {solution[:20]}")
print(f"Последние 20 ходов: {solution[-20:]}")

# Проверим есть ли R' в решении
inverse_r = sum(1 for m in solution if "R'" in m or (m[0] == 'R' and len(m) > 1))
print(f"Ходов с R или R' в решении: {inverse_r}")
