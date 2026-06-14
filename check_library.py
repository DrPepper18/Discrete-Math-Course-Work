#!/usr/bin/env python3
"""Проверяем библиотеку макросов для углов"""
from backend.rubik.solver import _LIB, _macro_effect, PRIM
from backend.rubik.pieces import read_corners
from backend.rubik.state import solved

print(f"Размер библиотеки corner3: {len(_LIB['corner3'])} макросов\n")

# Показываем первые 5 макросов
print("Первые 5 макросов corner3:")
for i, (moves, perm) in enumerate(_LIB['corner3'][:5]):
    print(f"  {i+1}. Перестановка: {perm}, ходов: {len(moves)}")

print()

# Проверим может ли библиотека решить 4-цикл (1,3,5,7)
# Перестановка углов [0, 2, 1, 4, 3, 6, 5, 7]
target_perm = [0, 2, 1, 4, 3, 6, 5, 7]
print(f"Ищем макро для перестановки: {target_perm}")

found = False
for moves, perm in _LIB['corner3']:
    if perm == target_perm:
        print(f"Найден макро: {' '.join(moves)} ({len(moves)} ходов)")
        found = True
        break

if not found:
    print("Макро для этой перестановки не найден в библиотеке")

# Покажем все перестановки в библиотеке
print()
print("Все перестановки в библиотеке corner3:")
perms = set()
for _, perm in _LIB['corner3']:
    perm_tuple = tuple(perm)
    perms.add(perm_tuple)

for perm in sorted(list(perms))[:10]:
    print(f"  {list(perm)}")
    
print(f"... и еще {len(perms) - 10} перестановок" if len(perms) > 10 else "")
