"""Состояние кубика как перестановка 54 сегментов + операции над ним."""
from __future__ import annotations
import random
from .geometry import MOVES, MOVE_LABELS, N_SEG, inverse_label


def solved():
    """Тождественная перестановка e[i] = i (собранный куб)."""
    return list(range(N_SEG + 1))


def apply_move(state, label):
    """new[i] = state[ MOVES[label][i] ]  (композиция перестановок)."""
    perm = MOVES[label]
    return [0] + [state[perm[i]] for i in range(1, N_SEG + 1)]


def apply_sequence(state, labels):
    for lab in labels:
        state = apply_move(state, lab)
    return state


def is_solved(state):
    return all(state[i] == i for i in range(1, N_SEG + 1))


def scramble(n=25, seed=None):
    """Случайная скрэмбл-последовательность из n ходов (без тривиальных повторов)."""
    rng = random.Random(seed)
    faces = ['R', 'L', 'U', 'D', 'F', 'B']
    suffix = ['', "'", '2']
    seq, last = [], None
    while len(seq) < n:
        f = rng.choice(faces)
        if f == last:
            continue
        last = f
        seq.append(f + rng.choice(suffix))
    state = apply_sequence(solved(), seq)
    return state, seq


def invert_sequence(labels):
    return [inverse_label(l) for l in reversed(labels)]
