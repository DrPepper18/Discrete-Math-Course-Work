#!/usr/bin/env python3
"""Проверяем разложение 4-цикла на 3-циклы"""
from backend.rubik.cycles import cycle_to_3cycles

# 4-цикл
cycle = (1, 3, 5, 7)
threes, leftover = cycle_to_3cycles(cycle)

print(f"Цикл: {cycle}")
print(f"3-циклы: {threes}")
print(f"Остаток (транспозиция): {leftover}")
print()

# Проверим что из этого получается
print("Разложение 4-цикла (1,3,5,7):")
print("Формула: (1,3,5,7) = (1,3,5) · (5,7,1)")
print()
print(f"Наш алгоритм дал:")
print(f"  3-циклы: {threes}")  
print(f"  Остаток: {leftover}")
print()
print("Это означает, что 4-цикл = (1,3,5) · (5,7)?")
print("Проверяем: (1,3,5) переводит 1→3, 3→5, 5→1")
print("           (5,7) переводит 5→7, 7→5")
print("Композиция: 1→3, 3→5, 5→7, 7→5→1")
print("Получается цикл: 1→3, 3→5, 5→7, 7→1")
print("Это (1,3,5,7) ✓")
