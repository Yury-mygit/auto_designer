"""Booking-specific компоненты как функции, возвращающие list[Element].

Каждая функция принимает (x, y, w, [h], **opts) и возвращает плоский
список элементов. external_ref/id у внутренних элементов не задаются
— они идут как child frame'а и идентифицируются позицией.

Pilot-набор (карта Этап 4 #29):
  - topbar(x, y, w, title)
  - msg_bubble_them(x, y, w_max, text)
  - msg_bubble_me(x, y, w_max, text)
  - subject_card(x, y, w, name, extra)
  - banner_warn(x, y, w, text)
  - composer(x, y, w, placeholder)
"""
from __future__ import annotations

from uuid import uuid4

from auto_designer.booking.constants import COLORS, DIM, FONT
from auto_designer.core.primitives import Element, Rect, Text


def topbar(x: float, y: float, w: float, title: str) -> list[Element]:
    h = DIM["topbar_h"]
    return [
        Rect(
            id=uuid4(), x=x, y=y, w=w, h=h,
            attrs={"fill": COLORS["surface"], "stroke": COLORS["border"], "strokeWidth": 1},
        ),
        # Back arrow
        Text(
            id=uuid4(), x=x + 16, y=y + 18, w=24, h=24,
            attrs={"text": "←", "fontSize": 22, "color": COLORS["text"], "fontFamily": FONT["family"]},
        ),
        Text(
            id=uuid4(), x=x + 50, y=y + 18, w=w - 100, h=24,
            attrs={
                "text": title, "fontSize": FONT["size_lg"],
                "color": COLORS["text"], "fontFamily": FONT["family"],
                "fontWeight": "600",
            },
        ),
    ]


def banner_warn(x: float, y: float, w: float, text: str) -> tuple[list[Element], float]:
    """Жёлтый warn-баннер (для bot_blocked). Возвращает (elements, height)."""
    h = 44
    pad = 8
    return [
        Rect(
            id=uuid4(), x=x + pad, y=y + pad, w=w - 2 * pad, h=h - pad,
            attrs={
                "fill": COLORS["warn_bg"], "stroke": COLORS["warn_border"],
                "strokeWidth": 1, "radius": 6,
            },
        ),
        Text(
            id=uuid4(), x=x + pad + 12, y=y + pad + 10, w=w - 2 * pad - 24, h=h - pad - 20,
            attrs={
                "text": text, "fontSize": FONT["size_sm"],
                "color": COLORS["warn_text"], "fontFamily": FONT["family"],
            },
        ),
    ], h


def subject_card(
    x: float, y: float, w: float, name: str, extra: str | None = None,
) -> tuple[list[Element], float]:
    """Sticky SubjectCard сверху thread view. Возвращает (elements, height)."""
    h = 60
    pad = 8
    photo = 44
    return [
        Rect(
            id=uuid4(), x=x + pad, y=y + pad, w=w - 2 * pad, h=h - pad,
            attrs={
                "fill": COLORS["surface_soft"], "stroke": COLORS["border"],
                "strokeWidth": 1, "radius": 8,
            },
        ),
        # photo placeholder
        Rect(
            id=uuid4(), x=x + pad + 10, y=y + pad + 4, w=photo, h=photo,
            attrs={"fill": COLORS["surface"], "stroke": COLORS["border_soft"], "strokeWidth": 1, "radius": 6},
        ),
        Text(
            id=uuid4(), x=x + pad + 10 + photo + 10, y=y + pad + 6, w=w - 2 * pad - photo - 30, h=20,
            attrs={
                "text": name, "fontSize": FONT["size_md"],
                "color": COLORS["text"], "fontFamily": FONT["family"],
                "fontWeight": "600",
            },
        ),
    ] + ([
        Text(
            id=uuid4(), x=x + pad + 10 + photo + 10, y=y + pad + 28, w=w - 2 * pad - photo - 30, h=18,
            attrs={
                "text": extra, "fontSize": FONT["size_sm"],
                "color": COLORS["muted"], "fontFamily": FONT["family"],
            },
        ),
    ] if extra else []), h


def msg_bubble_them(x: float, y: float, w_max: float, text: str) -> tuple[list[Element], float]:
    """Входящее сообщение (от отеля). Слева. Возвращает (elements, height)."""
    bubble_w = min(w_max * 0.75, 280)
    h = 50
    pad = 10
    return [
        Rect(
            id=uuid4(), x=x + 8, y=y, w=bubble_w, h=h,
            attrs={
                "fill": COLORS["surface"], "stroke": COLORS["border"],
                "strokeWidth": 1, "radius": DIM["msg_radius"],
            },
        ),
        # meta
        Text(
            id=uuid4(), x=x + 8 + pad, y=y + 6, w=bubble_w - 2 * pad, h=12,
            attrs={
                "text": "Отель · 14:23", "fontSize": FONT["size_xs"],
                "color": COLORS["text_faint"], "fontFamily": FONT["family"],
            },
        ),
        Text(
            id=uuid4(), x=x + 8 + pad, y=y + 22, w=bubble_w - 2 * pad, h=20,
            attrs={
                "text": text, "fontSize": FONT["size_md"],
                "color": COLORS["text"], "fontFamily": FONT["family"],
            },
        ),
    ], h


def msg_bubble_me(x: float, y: float, w_max: float, text: str) -> tuple[list[Element], float]:
    """Исходящее сообщение (от клиента). Справа. Возвращает (elements, height)."""
    bubble_w = min(w_max * 0.75, 280)
    h = 50
    pad = 10
    bx = x + w_max - bubble_w - 8
    return [
        Rect(
            id=uuid4(), x=bx, y=y, w=bubble_w, h=h,
            attrs={
                "fill": COLORS["accent"], "stroke": COLORS["accent"],
                "strokeWidth": 1, "radius": DIM["msg_radius"],
            },
        ),
        Text(
            id=uuid4(), x=bx + pad, y=y + 6, w=bubble_w - 2 * pad, h=12,
            attrs={
                "text": "Вы · 14:24", "fontSize": FONT["size_xs"],
                "color": COLORS["accent_text"], "fontFamily": FONT["family"], "opacity": 0.85,
            },
        ),
        Text(
            id=uuid4(), x=bx + pad, y=y + 22, w=bubble_w - 2 * pad, h=20,
            attrs={
                "text": text, "fontSize": FONT["size_md"],
                "color": COLORS["accent_text"], "fontFamily": FONT["family"],
            },
        ),
    ], h


def composer(x: float, y: float, w: float, placeholder: str = "Сообщение…") -> tuple[list[Element], float]:
    """Composer внизу: textarea + кнопка Отправить. Возвращает (elements, height)."""
    h = 56
    pad = 8
    btn_w = 100
    ta_w = w - 2 * pad - btn_w - 8
    # граница сверху
    return [
        Rect(
            id=uuid4(), x=x, y=y, w=w, h=1,
            attrs={"fill": COLORS["border_soft"]},
        ),
        # textarea
        Rect(
            id=uuid4(), x=x + pad, y=y + pad, w=ta_w, h=h - 2 * pad,
            attrs={
                "fill": COLORS["surface"], "stroke": COLORS["border_soft"],
                "strokeWidth": 1, "radius": DIM["input_radius"],
            },
        ),
        Text(
            id=uuid4(), x=x + pad + 10, y=y + pad + 12, w=ta_w - 20, h=16,
            attrs={
                "text": placeholder, "fontSize": FONT["size_md"],
                "color": COLORS["text_faint"], "fontFamily": FONT["family"],
            },
        ),
        # send button
        Rect(
            id=uuid4(), x=x + pad + ta_w + 8, y=y + pad, w=btn_w, h=h - 2 * pad,
            attrs={
                "fill": COLORS["accent"], "stroke": COLORS["accent"],
                "strokeWidth": 1, "radius": DIM["btn_radius"],
            },
        ),
        Text(
            id=uuid4(), x=x + pad + ta_w + 8, y=y + pad + 12, w=btn_w, h=16,
            attrs={
                "text": "Отправить", "fontSize": FONT["size_md"],
                "color": COLORS["accent_text"], "fontFamily": FONT["family"],
                "textAlign": "center", "fontWeight": "600",
            },
        ),
    ], h
