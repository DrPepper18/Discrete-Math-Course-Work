"""Поиск базовых чистых алгоритмов коммутаторным перебором [A,B]=A B A' B'."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from itertools import product
from rubik import solved, apply_sequence
from rubik.pieces import read_corners, read_edges

FACE = ['R', 'L', 'U', 'D', 'F', 'B']
SUF = ['', "'", '2']
QT = [f + s for f in FACE for s in SUF]
FACEOF = {m: m[0] for m in QT}


def inv(m):
    if m.endswith('2'):
        return m
    if m.endswith("'"):
        return m[:-1]
    return m + "'"


def gen(maxlen):
    """последовательности без двух подряд ходов одной грани"""
    out = []
    for L in range(1, maxlen + 1):
        for combo in product(QT, repeat=L):
            if any(FACEOF[combo[i]] == FACEOF[combo[i + 1]] for i in range(L - 1)):
                continue
            out.append(list(combo))
    return out


def effect(seq):
    st = apply_sequence(solved(), seq)
    cp, co = read_corners(st)
    ep, eo = read_edges(st)
    cmis = [i for i in range(8) if cp[i] != i]
    emis = [i for i in range(12) if ep[i] != i]
    ctw = [(i, co[i]) for i in range(8) if co[i] != 0]
    efl = [i for i in range(12) if eo[i] != 0]
    return cp, co, ep, eo, cmis, emis, ctw, efl


def classify(seq):
    cp, co, ep, eo, cmis, emis, ctw, efl = effect(seq)
    if not emis and not efl and not ctw and len(cmis) == 3 and all(cp[cp[cp[i]]] == i for i in cmis):
        return 'c3'
    if not cmis and not ctw and not efl and len(emis) == 3 and all(ep[ep[ep[i]]] == i for i in emis):
        return 'e3'
    if not cmis and not emis and not efl and len(ctw) == 2 and sum(co) % 3 == 0:
        return 'ct'
    if not cmis and not emis and not ctw and len(efl) == 2:
        return 'ef'
    return None


found = {}
As = gen(3)
Bs = gen(2)
cnt = 0
for A in As:
    for B in Bs:
        if FACEOF[A[-1]] == FACEOF[B[0]]:
            continue
        seq = A + B + [inv(m) for m in reversed(A)] + [inv(m) for m in reversed(B)]
        cnt += 1
        k = classify(seq)
        if k and k not in found:
            found[k] = seq
    if len(found) == 4:
        break

print('searched', cnt)

# Орентационные примитивы: коммутаторы найденных 3-циклов с короткими seq.
C3 = found['c3']
E3 = found['e3']


def commute(X, Y):
    return X + Y + [inv(m) for m in reversed(X)] + [inv(m) for m in reversed(Y)]


for Y in gen(4):
    if 'ct' not in found:
        s = commute(C3, Y)
        if classify(s) == 'ct':
            found['ct'] = s
    if 'ef' not in found:
        for s in (commute(E3, Y), commute(Y, E3)):
            if classify(s) == 'ef':
                found['ef'] = s
                break
    if 'ct' in found and 'ef' in found:
        break

for k in ('c3', 'e3', 'ct', 'ef'):
    v = found.get(k)
    print(k, '=', ' '.join(v) if v else None)
    if v:
        cp, co, ep, eo, cmis, emis, ctw, efl = effect(v)
        print('    corners', cmis, 'twist', ctw, '| edges', emis, 'flip', efl, '| len', len(v))
