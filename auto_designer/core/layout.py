"""Layout helpers — vstack / hstack / etc.

Принимают список (h, builder), где builder получает (x, y, w) и возвращает
list[Element]. Возвращают список Element'ов с уже выставленными
координатами.
"""
from __future__ import annotations

from typing import Callable

from auto_designer.core.primitives import Element


Builder = Callable[[float, float, float], list[Element]]


def vstack(
    items: list[tuple[float, Builder]],
    x: float,
    y: float,
    w: float,
    gap: float = 0.0,
) -> list[Element]:
    """Вертикальная укладка. items = [(height, builder(x, y, w)), ...].
    builder вызывается с уже посчитанным y.
    """
    out: list[Element] = []
    cur_y = y
    for h, builder in items:
        out.extend(builder(x, cur_y, w))
        cur_y += h + gap
    return out


def hstack(
    items: list[tuple[float, Builder]],
    x: float,
    y: float,
    h: float,
    gap: float = 0.0,
) -> list[Element]:
    """Горизонтальная укладка. items = [(width, builder(x, y, h)), ...]."""
    out: list[Element] = []
    cur_x = x
    for w, builder in items:
        out.extend(builder(cur_x, y, w))
        cur_x += w + gap
    return out
