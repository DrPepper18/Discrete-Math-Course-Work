#!/usr/bin/env python3
"""Тест оптимального решателя на одном ходе R"""
from backend.rubik.state import apply_move, solved
from backend.rubik.solver_optimal import solve_optimal, solve_bfs_limited

print("=" * 60)
print("Тест оптимального решателя")
print("=" * 60)

# Один ход R
state = apply_move(solved(), "R")

print("\nТест 1: Один ход R")
print("-" * 60)

# Сначала пробуем BFS
print("Попытка двустороннего BFS (max 8 ходов, timeout 5s):")
solution, depth = solve_bfs_limited(state, max_depth=8, timeout=5.0, verbose=True)

if solution:
    print(f"\n[V] BFS найдено оптимальное решение: {len(solution)} ходов")
    print(f"  Решение: {' '.join(solution)}")
else:
    print(f"\n[X] BFS не нашло за отведённое время")
    
print()

# Теперь пробуем оптимальный решатель
print("Полный оптимальный решатель:")
solution = solve_optimal(state, verbose=True)
print(f"\n[V] Найдено решение: {len(solution)} ходов")
print(f"  Первые 10 ходов: {' '.join(solution[:10])}")
if len(solution) > 10:
    print(f"  ... ({len(solution) - 10} ещё)")

print("\n" + "=" * 60)
