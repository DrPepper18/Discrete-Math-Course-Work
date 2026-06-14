"""FastAPI-бэкенд: состояние кубика (перестановка 54 сегментов) + сборка.

Состояние хранится на сервере. Фронтенд:
  * отображает ходы и текущую раскраску,
  * по кнопке «Решить» получает алгоритм сборки в нотации,
  * проигрывает анимацию по списку ходов.
"""
from __future__ import annotations
import threading
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from rubik import (
    solved, apply_move, apply_sequence, is_solved, scramble, MOVE_LABELS, APPJS,
)
from rubik.solver_optimal import solve_optimal

# face index (1..6) -> цвет (как в app.js, по осям)
FACE_COLOR = {1: "R", 2: "F", 3: "L", 4: "B", 5: "D", 6: "U"}  # +X,+Z,-X,-Z,-Y,+Y


def facelets(state):
    """Цвет каждого слота 1..54 = грань исходного сегмента, стоящего в нём."""
    return [FACE_COLOR[(state[i] - 1) // 9 + 1] for i in range(1, 55)]


app = FastAPI(title="Rubik Cube Solver")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

_lock = threading.Lock()
_state = solved()


def _snapshot():
    return {
        "state": _state[1:],
        "facelets": facelets(_state),
        "solved": is_solved(_state),
    }


class MoveBody(BaseModel):
    move: str


class MovesBody(BaseModel):
    moves: list[str]


class ScrambleBody(BaseModel):
    n: int = 25
    seed: int | None = None


@app.get("/api/state")
def get_state():
    with _lock:
        return _snapshot()


@app.post("/api/reset")
def reset():
    global _state
    with _lock:
        _state = solved()
        return _snapshot()


@app.post("/api/move")
def move(body: MoveBody):
    global _state
    if body.move not in MOVE_LABELS:
        raise HTTPException(400, f"неизвестный ход: {body.move}")
    with _lock:
        _state = apply_move(_state, body.move)
        return _snapshot()


@app.post("/api/apply")
def apply_many(body: MovesBody):
    global _state
    for m in body.moves:
        if m not in MOVE_LABELS:
            raise HTTPException(400, f"неизвестный ход: {m}")
    with _lock:
        _state = apply_sequence(_state, body.moves)
        return _snapshot()


@app.post("/api/scramble")
def do_scramble(body: ScrambleBody):
    global _state
    with _lock:
        _state, seq = scramble(body.n, seed=body.seed)
        snap = _snapshot()
        snap["scramble"] = seq
        return snap


@app.post("/api/solve")
def do_solve():
    """Возвращает алгоритм сборки для ТЕКУЩЕГО состояния (не мутирует состояние).
    Для каждого хода даётся и нотация, и тройка (axis, layer, dir) для анимации."""
    with _lock:
        sol = solve_optimal(_state)
    return {
        "solution": sol,
        "length": len(sol),
        "anim": [APPJS[m] for m in sol],
    }


# отдаём фронтенд (index.html, app.js) из каталога проекта
_ROOT = Path(__file__).resolve().parent.parent
app.mount("/", StaticFiles(directory=str(_ROOT), html=True), name="static")
