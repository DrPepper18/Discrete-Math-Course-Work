"""Алгебра перестановок: разложение на циклы и формулы (3),(4),(5) методички.

Перестановка хранится как list длины 55 (1-индекс.), p[i] = образ i.
Цикл (a1,a2,...,as) означает a1->a2->...->as->a1.
"""
from __future__ import annotations
from .geometry import N_SEG


def identity():
    return list(range(N_SEG + 1))


def compose(a, b):
    """(a∘b)[i] = a[b[i]] — сначала b, потом a."""
    return [0] + [a[b[i]] for i in range(1, N_SEG + 1)]


def cycle_to_perm(cycle, n=N_SEG):
    """Цикл (a1,...,as) -> перестановка."""
    p = list(range(n + 1))
    s = len(cycle)
    for k in range(s):
        p[cycle[k]] = cycle[(k + 1) % s]
    return p


def cycles_of(perm):
    """Формула (3): разложение на непересекающиеся циклы (длины >= 2)."""
    seen = set()
    cycles = []
    for start in range(1, len(perm)):
        if start in seen or perm[start] == start:
            continue
        cyc, x = [], start
        while x not in seen:
            seen.add(x)
            cyc.append(x)
            x = perm[x]
        if len(cyc) > 1:
            cycles.append(tuple(cyc))
    return cycles


def cycle_to_transpositions(cycle):
    """Формула (5): (a1,...,as) = (a1,a2)∘(a2,a3)∘...∘(a_{s-1},as).
    Список 2-циклов в порядке внешняя→внутренняя композиция (compose-слева)."""
    return [(cycle[k], cycle[k + 1]) for k in range(len(cycle) - 1)]


def cycle_to_3cycles(cycle):
    """Разложение цикла на 3-циклы (ядро направленного перебора при сборке).

    Использует тождество  (a1..as) = (a1,a2,a3)∘(a3,a4,a5)∘(a5,a6,a7)∘...
    (сцепка по последнему элементу). Чётный цикл оставляет одну транспозицию —
    его нельзя выразить только 3-циклами (проявление чётности перестановки).
    Возвращает (список 3-циклов, остаточная транспозиция | None).
    """
    a = list(cycle)
    threes = []
    i = 0
    while len(a) - i >= 3:
        threes.append((a[i], a[i + 1], a[i + 2]))
        i += 2
    leftover = (a[i], a[i + 1]) if len(a) - i == 2 else None
    return threes, leftover


def perm_to_3cycles(perm):
    """Вся перестановка -> (3-циклы, список остаточных транспозиций)."""
    all_threes, transps = [], []
    for cyc in cycles_of(perm):
        threes, left = cycle_to_3cycles(cyc)
        all_threes.extend(threes)
        if left:
            transps.append(left)
    return all_threes, transps


def parity(perm):
    """Чётность перестановки: 0 — чётная, 1 — нечётная."""
    p = 0
    for cyc in cycles_of(perm):
        p ^= (len(cyc) - 1) & 1
    return p
