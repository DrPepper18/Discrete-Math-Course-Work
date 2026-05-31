"""Сверка: какой (axis, layer, dir) в модели app.js даёт ТУ ЖЕ перестановку
54 сегментов, что и образующая бэкенда MOVES[label].

Модель app.js: поворот слоя {coord[axis]==layer} на угол
    angle = angleSign * dir * 90°,   angleSign = +1 если axis=='y' иначе -1
вокруг оси axis (правило правой руки, как в three.js).
Стикер (cubie p, нормаль n) переходит в (R·p, R·n).
"""
import numpy as np
from rubik.geometry import NUM2STICKER, STICKER2NUM, MOVES, N_SEG

AXIS_IDX = {'x': 0, 'y': 1, 'z': 2}
AXIS_VEC = {'x': np.array([1, 0, 0]), 'y': np.array([0, 1, 0]), 'z': np.array([0, 0, 1])}


def rot(axis, turns):
    th = np.pi / 2 * turns
    c, s = int(round(np.cos(th))), int(round(np.sin(th)))
    a = AXIS_VEC[axis]
    ax, ay, az = a
    R = np.array([
        [c+ax*ax*(1-c),   ax*ay*(1-c)-az*s, ax*az*(1-c)+ay*s],
        [ay*ax*(1-c)+az*s, c+ay*ay*(1-c),   ay*az*(1-c)-ax*s],
        [az*ax*(1-c)-ay*s, az*ay*(1-c)+ax*s, c+az*az*(1-c)],
    ])
    return np.rint(R).astype(int)


def appjs_perm(axis, layer, dir):
    """Перестановка alpha[i]=g^{-1}(i) для одиночного хода в модели app.js."""
    angle_sign = 1 if axis == 'y' else -1
    R = rot(axis, angle_sign * dir)          # turns = angle/90
    idx = AXIS_IDX[axis]
    g = list(range(N_SEG + 1))
    for num, (p, n) in NUM2STICKER.items():
        if p[idx] == layer:
            p2 = tuple(int(x) for x in (R @ np.array(p)))
            n2 = tuple(int(x) for x in (R @ np.array(n)))
            g[num] = STICKER2NUM[(p2, n2)]
    alpha = list(range(N_SEG + 1))
    for s in range(1, N_SEG + 1):
        alpha[g[s]] = s
    return alpha


if __name__ == "__main__":
    print("label -> (axis, layer, dir)  [где app.js даёт MOVES[label]]")
    label_map = {}
    for face in ['R', 'L', 'U', 'D', 'F', 'B']:
        target = MOVES[face]
        hit = None
        for axis in ('x', 'y', 'z'):
            for layer in (-1, 1):
                for dir in (-1, 1):
                    if appjs_perm(axis, layer, dir) == target:
                        hit = (axis, layer, dir)
        print(f"  {face}: {hit}")
        label_map[face] = hit
    print("\nJS LABEL_MAP:")
    for f, (a, l, d) in label_map.items():
        print(f"  {f}: ['{a}', {l}, {d}],")
