"""Уровень деталей (cubies): из перестановки 54 сегментов извлекаем
перестановку и ориентацию 8 углов и 12 рёбер.

Это нужно солверу для принятия решений (какие детали куда переставить),
тогда как сами ходы применяются на уровне сегментов (state.apply_move).

Ориентация определяется единообразно: как циклический сдвиг, совмещающий
фактический набор цветов в слоте с «домашним» при фиксированном каноническом
порядке позиций слота. Конвенция самосогласована, т.к. состояние деталей
всегда вычисляется из состояния сегментов.
"""
from __future__ import annotations
from .geometry import NUM2STICKER, N_SEG


def _color(num):           # цвет сегмента = его грань (0..5)
    return (num - 1) // 9


# Приоритет оси нормали для канонического порядка позиций слота: Y, X, Z.
_AXIS_RANK = {1: 0, 0: 1, 2: 2}   # индекс ненулевой координаты нормали -> ранг


def _normal_axis(nrm):
    for i in (1, 0, 2):
        if nrm[i] != 0:
            return i
    raise ValueError


def _cross(a, b):
    return (a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2], a[0]*b[1] - a[1]*b[0])


def _order_corner(nums):
    """Правосторонний циклический порядок 3 стикеров угла:
    первый — стикер на Y-грани, далее два так, что n1×n2 = n3.
    Гарантирует, что физический поворот угла = циклический сдвиг цветов."""
    norm = {n: NUM2STICKER[n][1] for n in nums}
    first = next(n for n in nums if norm[n][1] != 0)       # Y-нормаль
    rest = [n for n in nums if n != first]
    a, b = rest
    if _cross(norm[first], norm[a]) == norm[b]:
        return (first, a, b)
    return (first, b, a)


def _build_slots():
    """Слоты углов и рёбер: список позиций сегментов в каноническом порядке."""
    by_cubie = {}
    for num, (p, nrm) in NUM2STICKER.items():
        by_cubie.setdefault(p, []).append(num)
    corners, edges = [], []
    for p, nums in by_cubie.items():
        if len(nums) == 1:
            continue
        if len(nums) == 3:
            corners.append(_order_corner(nums))
        else:
            edges.append(tuple(sorted(nums, key=lambda n: _AXIS_RANK[_normal_axis(NUM2STICKER[n][1])])))
    corners.sort()
    edges.sort()
    return corners, edges


CORNER_SLOTS, EDGE_SLOTS = _build_slots()   # 8 и 12 кортежей позиций
N_CORNERS, N_EDGES = len(CORNER_SLOTS), len(EDGE_SLOTS)

# домашние наборы цветов -> id детали
_CORNER_ID = {frozenset(_color(n) for n in slot): i for i, slot in enumerate(CORNER_SLOTS)}
_EDGE_ID = {frozenset(_color(n) for n in slot): i for i, slot in enumerate(EDGE_SLOTS)}
# домашние цвета в каноническом порядке (для ориентации)
_CORNER_HOME = [[_color(n) for n in slot] for slot in CORNER_SLOTS]
_EDGE_HOME = [[_color(n) for n in slot] for slot in EDGE_SLOTS]


def _read(state, slots, id_map, home, mod):
    perm = [0] * len(slots)
    ori = [0] * len(slots)
    for s, positions in enumerate(slots):
        actual = [_color(state[pos]) for pos in positions]
        piece = id_map[frozenset(actual)]
        perm[s] = piece
        h = home[piece]
        # найти сдвиг o: rotate(h, o) == actual
        for o in range(mod):
            if all(h[(k + o) % mod] == actual[k] for k in range(mod)):
                ori[s] = o
                break
        else:
            raise ValueError(f"не найдена ориентация: slot={s} actual={actual} home={h}")
    return perm, ori


def read_corners(state):
    """-> (perm[8], ori[8] в Z3). perm[s] = id угла в слоте s."""
    return _read(state, CORNER_SLOTS, _CORNER_ID, _CORNER_HOME, 3)


def read_edges(state):
    """-> (perm[12], ori[12] в Z2)."""
    return _read(state, EDGE_SLOTS, _EDGE_ID, _EDGE_HOME, 2)


def pieces_solved(state):
    cp, co = read_corners(state)
    ep, eo = read_edges(state)
    return (cp == list(range(N_CORNERS)) and all(o == 0 for o in co)
            and ep == list(range(N_EDGES)) and all(o == 0 for o in eo))
