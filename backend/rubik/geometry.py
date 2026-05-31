"""Геометрия и нумерация кубика Рубика по методичке (Рис.1, Рис.2).

Состояние и повороты — перестановки множества из 54 сегментов (наклеек).
Здесь строится:
  * соответствие  номер сегмента (1..54) <-> (кубик в 3D, внешняя нормаль);
  * 27 образующих Phi_i^k(j) как перестановки.

Геометрия выверена по примеру phi_1 = Phi_1^{-90}(Z) из методички
(см. tests/test_geometry.py).

Соглашение о перестановке состояния (как в методичке):
  alpha[i] = номер сегмента, который СЕЙЧАС находится в слоте i
             (т.е. слот i показывает цвет, изначально стоявший в alpha[i]).
  Собранный куб — тождественная перестановка e[i] = i.
"""
from __future__ import annotations
import numpy as np

# ── Развёртка (Рис.2): grid[face] = 3x3 номеров (строки ↓, столбцы →) ──
GRIDS = {
    1: [[7, 4, 1], [8, 5, 2], [9, 6, 3]],            # I    (+X)
    2: [[16, 13, 10], [17, 14, 11], [18, 15, 12]],   # II   (+Z)
    3: [[25, 22, 19], [26, 23, 20], [27, 24, 21]],   # III  (-X)
    4: [[34, 31, 28], [35, 32, 29], [36, 33, 30]],   # IV   (-Z)
    5: [[37, 38, 39], [40, 41, 42], [43, 44, 45]],   # V    (-Y)
    6: [[46, 47, 48], [49, 50, 51], [52, 53, 54]],   # VI   (+Y)
}

X = np.array([1, 0, 0]); Y = np.array([0, 1, 0]); Z = np.array([0, 0, 1])

# Ориентация каждой грани: n — внешняя нормаль, u — направление +столбца
# (вправо в развёртке), v — направление +строки (вниз в развёртке).
# Значения для граней 5,6 и нормали выверены перебором по phi_1.
FACES = {
    1: dict(n= X, u= Z, v=-Y),
    2: dict(n= Z, u=-X, v=-Y),
    3: dict(n=-X, u=-Z, v=-Y),
    4: dict(n=-Z, u= X, v=-Y),
    5: dict(n=-Y, u=-X, v=-Z),
    6: dict(n= Y, u=-X, v= Z),
}

N_SEG = 54


def _build_stickers():
    """num -> (cubie_pos: tuple[int,int,int], normal: tuple[int,int,int])"""
    num2s, s2num = {}, {}
    for f, grid in GRIDS.items():
        n, u, v = FACES[f]['n'], FACES[f]['u'], FACES[f]['v']
        for r in range(3):
            for c in range(3):
                num = grid[r][c]
                p = tuple(int(x) for x in (n + (c - 1) * u + (r - 1) * v))
                nn = tuple(int(x) for x in n)
                num2s[num] = (p, nn)
                s2num[(p, nn)] = num
    return num2s, s2num


NUM2STICKER, STICKER2NUM = _build_stickers()


def _rot_matrix(axis, turns):
    """Целочисленная матрица поворота на turns*90° вокруг оси axis (правило правой руки)."""
    theta = np.pi / 2 * turns
    c = int(round(np.cos(theta))); s = int(round(np.sin(theta)))
    a = axis / np.linalg.norm(axis)
    ax, ay, az = a
    R = np.array([
        [c + ax*ax*(1-c),    ax*ay*(1-c) - az*s, ax*az*(1-c) + ay*s],
        [ay*ax*(1-c) + az*s, c + ay*ay*(1-c),    ay*az*(1-c) - ax*s],
        [az*ax*(1-c) - ay*s, az*ay*(1-c) + ax*s, c + az*az*(1-c)],
    ])
    return np.rint(R).astype(int)


def make_perm(axis, layer_sign, turns):
    """Перестановка alpha (1-индекс., list длины 55, [0] не используется) для
    поворота слоя {p[axis]==layer_sign} на turns*90°.

    alpha[i] = откуда приехал стикер, стоящий теперь в слоте i  (= g^{-1}).
    """
    axis_idx = int(np.argmax(np.abs(axis)))
    R = _rot_matrix(axis, turns)
    g = list(range(N_SEG + 1))            # g[s] = куда уезжает стикер из слота s
    for num, (p, nrm) in NUM2STICKER.items():
        pa = np.array(p)
        if pa[axis_idx] == layer_sign:
            p2 = tuple(int(x) for x in (R @ pa))
            n2 = tuple(int(x) for x in (R @ np.array(nrm)))
            g[num] = STICKER2NUM[(p2, n2)]
    alpha = list(range(N_SEG + 1))
    for s in range(1, N_SEG + 1):
        alpha[g[s]] = s                   # инверсия: alpha = g^{-1}
    return alpha


# ── Стандартная нотация ходов → (ось, слой, число четвертей по часовой) ──
# "По часовой" (как в нотации спидкубинга) при взгляде снаружи грани.
_AXIS = {'x': X, 'y': Y, 'z': Z}
_BASE = {   # буква: (ось, слой, turns для одного хода "по часовой")
    'R': ('x',  1, -1), 'L': ('x', -1,  1),
    'U': ('y',  1, -1), 'D': ('y', -1,  1),
    'F': ('z',  1, -1), 'B': ('z', -1,  1),
}


def _compose(a, b):
    """(a∘b)[i] = a[b[i]] — сначала применить b (как состояние), потом a."""
    return [0] + [a[b[i]] for i in range(1, N_SEG + 1)]


def _build_moves():
    moves = {}
    for letter, (ax, layer, t) in _BASE.items():
        q = make_perm(_AXIS[ax], layer, t)        # одиночный (по часовой)
        moves[letter] = q
        moves[letter + "'"] = make_perm(_AXIS[ax], layer, -t)
        moves[letter + "2"] = _compose(q, q)
    return moves


MOVES = _build_moves()                  # label -> alpha-перестановка
MOVE_LABELS = list(MOVES.keys())

# Соответствие нотации → вызов rotateFace(axis, layer, dir) во фронтенде (app.js).
# dir подобран так, чтобы поворот app.js совпал с перестановкой MOVES[label]
# (см. verify_frontend_map.py). У оси Y знак обратный из-за angleSign в app.js.
_APPJS_BASE = {
    'R': ('x',  1,  1), 'L': ('x', -1, -1),
    'U': ('y',  1, -1), 'D': ('y', -1,  1),
    'F': ('z',  1,  1), 'B': ('z', -1, -1),
}
APPJS = {}
for _letter, (_ax, _layer, _dir) in _APPJS_BASE.items():
    APPJS[_letter] = (_ax, _layer, _dir)
    APPJS[_letter + "'"] = (_ax, _layer, -_dir)
    APPJS[_letter + "2"] = (_ax, _layer, 2 * _dir)


def inverse_label(label: str) -> str:
    if label.endswith("2"):
        return label
    if label.endswith("'"):
        return label[:-1]
    return label + "'"
