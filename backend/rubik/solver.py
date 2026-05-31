"""Сборка кубика методом 3-циклов и коммутаторов (метод методички).

Состояние раскладывается по деталям (углы/рёбра: перестановка + ориентация).
Каждый этап использует один «чистый» примитив-коммутатор, сопряжённый
setup-последовательностью S·P·S⁻¹ для нацеливания на нужные детали:

  c3  — 3-цикл углов        → решает перестановку углов
  e3  — 3-цикл рёбер        → решает перестановку рёбер
  ct  — твист пары углов    → ориентация углов
  ef  — переворот пары рёбер→ ориентация рёбер

Setup-последовательности находятся BFS по образам помеченных слотов:
переход = слот-перестановка хода (не зависит от содержимого слотов).
3-циклы чётны, поэтому при нечётной перестановке углов сначала делается
один четвертной поворот (выравнивание чётности).
"""
from __future__ import annotations
from collections import deque

from .geometry import inverse_label
from .state import solved, apply_move, apply_sequence
from .pieces import (
    read_corners, read_edges, pieces_solved,
    N_CORNERS, N_EDGES, CORNER_SLOTS, EDGE_SLOTS,
)
from . import cycles as C

# ── Базовые чистые примитивы (найдены коммутаторным перебором, см. find_primitives.py) ──
PRIM = {
    'c3': "R F R' B2 R F' R' B2".split(),
    'e3': "R2 U2 R2 F2 R2 U2 R2 F2".split(),
    'ct': "R F R' B2 R F' R' B2 L U B2 R F R' B2 R F' R' U' L'".split(),
    'ef': "R2 U2 R2 F2 R2 U2 R2 F2 U R U' B F2 R2 U2 R2 F2 R2 U2 R2 B' U R' U'".split(),
}
FACES = ['R', 'L', 'U', 'D', 'F', 'B']
QT = [f + s for f in FACES for s in ['', "'", '2']]


def _inv_seq(seq):
    return [inverse_label(m) for m in reversed(seq)]


def _slot_perm(move, read, slots):
    """σ_move[s] = деталь, оказавшаяся в слоте s после хода move (read-конвенция).
    При наращивании setup СПЕРЕДИ образ помеченных слотов под сопряжением
    обновляется поэлементно: nxt[x] = σ_move[cur[x]]."""
    return read(apply_move(solved(), move))[0]


def _bfs_setups(marks, read, slots):
    """Кратчайшие setup-последовательности по образам помеченных слотов marks.
    Setup строится наращиванием спереди, поэтому макрос S·P·S⁻¹ даёт 3-цикл
    в точности на слотах = образ marks. Возвращает dict: образ-кортеж -> ходы."""
    P = {m: _slot_perm(m, read, slots) for m in QT}
    start = tuple(marks)
    dist = {start: []}
    dq = deque([start])
    while dq:
        cur = dq.popleft()
        seq = dist[cur]
        for m in QT:
            if seq and seq[0][0] == m[0]:       # не два хода одной грани подряд (спереди)
                continue
            nxt = tuple(P[m][x] for x in cur)
            if nxt not in dist:
                dist[nxt] = [m] + seq
                dq.append(nxt)
    return dist


def _macro_effect(moves, read):
    """Перестановка-эффект макро на деталях: M[s] = деталь в слоте s после макро
    (правило композиции new[s] = old[M[s]]). Плюс ориентационная дельта."""
    st = apply_sequence(solved(), moves)
    return read(st)            # (perm, ori)


def _build():
    """Строит библиотеки макросов для всех этапов (выполняется один раз при импорте)."""
    lib = {}

    # — перестановочные макросы: сопряжение c3 / e3 —
    for key, prim, read, slots, marks in (
        ('corner3', PRIM['c3'], read_corners, CORNER_SLOTS, (0, 2, 5)),
        ('edge3',   PRIM['e3'], read_edges,   EDGE_SLOTS,   (4, 8, 11)),
    ):
        setups = _bfs_setups(marks, read, slots)
        macros = {}
        for triple, S in setups.items():
            if len(set(triple)) < 3:
                continue
            moves = S + prim + _inv_seq(S)
            perm, _ori = _macro_effect(moves, read)
            # перестановочному этапу ориентация безразлична (правится в этапах 3,4),
            # важно лишь покрыть все 3-циклы деталей
            key_perm = tuple(perm)
            if key_perm not in macros or len(moves) < len(macros[key_perm][0]):
                macros[key_perm] = (moves, perm)
        lib[key] = list(macros.values())

    # — ориентационные макросы: сопряжение ct / ef (примитив + инверсия) —
    for key, prim, read, slots, marks, mod in (
        ('twist', PRIM['ct'], read_corners, CORNER_SLOTS, (2, 5), 3),
        ('flip',  PRIM['ef'], read_edges,   EDGE_SLOTS,   (4, 8), 2),
    ):
        setups = _bfs_setups(marks, read, slots)
        macros = []
        seen = set()
        for pair, S in setups.items():
            if len(set(pair)) < 2:
                continue
            for base in (prim, _inv_seq(prim)):
                moves = S + base + _inv_seq(S)
                perm, ori = _macro_effect(moves, read)
                if list(perm) != list(range(len(slots))):    # перестановка не должна меняться
                    continue
                delta = tuple(ori)
                if delta in seen:
                    continue
                seen.add(delta)
                macros.append((moves, ori))
        lib[key] = macros

    return lib


_LIB = _build()


def _compress(seq):
    """Лёгкое сокращение: схлопывание подряд идущих ходов одной грани."""
    ang = {'': 1, "'": 3, '2': 2}
    rev = {1: '', 3: "'", 2: '2'}
    out = []
    for m in seq:
        if out and out[-1][0] == m[0]:
            tot = (ang[out[-1][1:]] + ang[m[1:]]) % 4
            out.pop()
            if tot:
                out.append(m[0] + rev[tot])
        else:
            out.append(m)
    return out


class _Run:
    def __init__(self, state):
        self.st = list(state)
        self.sol = []

    def do(self, moves):
        self.sol.extend(moves)
        self.st = apply_sequence(self.st, moves)


def solve(state):
    """Возвращает список ходов, собирающих куб из позиции state."""
    r = _Run(state)

    # 0) выравнивание чётности: 3-циклы чётны, перестановка должна быть чётной
    cp, _ = read_corners(r.st)
    if C.parity([0] + [c + 1 for c in cp]) == 1:
        r.do(['U'])

    _solve_perm(r, read_corners, _LIB['corner3'], N_CORNERS)   # 1) углы: позиции
    _solve_perm(r, read_edges,   _LIB['edge3'],   N_EDGES)     # 2) рёбра: позиции
    _solve_orient(r, read_corners, _LIB['twist'], 3)           # 3) углы: ориентация
    _solve_orient(r, read_edges,   _LIB['flip'],  2)           # 4) рёбра: ориентация

    assert pieces_solved(apply_sequence(list(state), r.sol)), "решение неверно!"
    return _compress(r.sol)


def _solve_perm(r, read, macros, n):
    for _ in range(n * 4):
        perm = read(r.st)[0]
        mis = sum(perm[s] != s for s in range(n))
        if mis == 0:
            return
        best = None
        for moves, M in macros:
            nm = sum(perm[M[s]] != s for s in range(n))
            gain = mis - nm
            if best is None or gain > best[0] or (gain == best[0] and len(moves) < len(best[1])):
                best = (gain, moves)
        assert best and best[0] > 0, "нет улучшающего 3-цикла (чётность?)"
        r.do(best[1])
    raise RuntimeError("перестановка не сошлась")


def _solve_orient(r, read, macros, mod):
    for _ in range(48):
        ori = read(r.st)[1]
        cnt = sum(o != 0 for o in ori)
        if cnt == 0:
            return
        best = None
        for moves, delta in macros:
            new = [(ori[s] + delta[s]) % mod for s in range(len(ori))]
            score = (sum(o != 0 for o in new), sum(new))
            if best is None or score < best[0] or (score == best[0] and len(moves) < len(best[1])):
                best = (score, moves)
        assert best and best[0][0] < cnt, "ориентация не уменьшается"
        r.do(best[1])
    raise RuntimeError("ориентация не сошлась")
