"""Booking-specific компоненты как функции, возвращающие list[Element].

Каждая функция принимает (x, y, w, [h], **opts) и возвращает плоский
список элементов с **абсолютными** координатами относительно board
(не frame). Frame.x/y учитывается на уровне screens.py.

Конвенции под board renderer (см. `board/backend/app/api/frames.py`):
  - rect: attrs.{fill, stroke, strokeWidth, rx} (NB: `rx`, не `radius`).
  - text: attrs.{text, fontSize, color, bold, italic, underline}.
    Без word-wrap. Для длинного текста — `note` тип (multi-line, `\n`).
  - note: attrs.{text, fontSize, color, fill, stroke, strokeWidth, rx}.
    Multi-line с word-break по `\n` (board сам не word-wrap'ит, рисует
    по строкам).

Компоненты:
  - topbar(x, y, w, title)                     — client/partner
  - subtitle_bar(x, y, w, text)                — «Клиенты», «Карточка клиента»
  - bottom_nav(x, y, w, items, active)         — нижняя навигация
  - tabs(x, y, w, items, active_idx)           — pill-tabs (отели в чате)
  - client_card(x, y, w, name, info, unread)   — карточка клиента в списке
  - msg_bubble_them/_me(x, y, w_max, text)
  - subject_card(x, y, w, name, extra)
  - banner_warn / banner_readonly(x, y, w, t)
  - composer(x, y, w, placeholder)
"""
from __future__ import annotations

from uuid import uuid4

from auto_designer.booking.constants import COLORS, DIM, FONT
from auto_designer.core.primitives import Element, Rect, Text


def _note(x, y, w, h, text, fill, color, font_size, rx=6, stroke=None):
    """Helper: создаёт элемент note (multi-line text)."""
    attrs = {
        "text": text, "fontSize": font_size, "color": color,
        "fill": fill, "rx": rx,
    }
    if stroke is not None:
        attrs["stroke"] = stroke
        attrs["strokeWidth"] = 1
    return Element(id=uuid4(), type="note", x=x, y=y, w=w, h=h, attrs=attrs)


def topbar(x: float, y: float, w: float, title: str) -> list[Element]:
    h = DIM["topbar_h"]
    return [
        Rect(
            id=uuid4(), x=x, y=y, w=w, h=h,
            attrs={"fill": COLORS["surface"], "stroke": COLORS["border"], "strokeWidth": 1, "rx": 0},
        ),
        Text(
            id=uuid4(), x=x + 16, y=y + 18, w=24, h=24,
            attrs={"text": "←", "fontSize": 22, "color": COLORS["text"]},
        ),
        Text(
            id=uuid4(), x=x + 50, y=y + 18, w=w - 100, h=24,
            attrs={"text": title, "fontSize": FONT["size_lg"], "color": COLORS["text"], "bold": True},
        ),
    ]


def subtitle_bar(x: float, y: float, w: float, text: str) -> tuple[list[Element], float]:
    h = 36
    return [
        Rect(
            id=uuid4(), x=x, y=y, w=w, h=h,
            attrs={"fill": COLORS["surface_soft"], "stroke": COLORS["border_soft"], "strokeWidth": 1, "rx": 0},
        ),
        Text(
            id=uuid4(), x=x + 14, y=y + 10, w=w - 60, h=18,
            attrs={"text": text, "fontSize": FONT["size_md"], "color": COLORS["text"], "bold": True},
        ),
        Text(
            id=uuid4(), x=x + w - 32, y=y + 10, w=20, h=18,
            attrs={"text": "⚙", "fontSize": FONT["size_md"], "color": COLORS["text"]},
        ),
    ], h


def bottom_nav(
    x: float, y: float, w: float, items: list[str], active_idx: int,
) -> tuple[list[Element], float]:
    h = 56
    n = len(items)
    cell_w = w / n
    elements: list[Element] = [
        Rect(
            id=uuid4(), x=x, y=y, w=w, h=h,
            attrs={"fill": COLORS["surface"], "stroke": COLORS["border"], "strokeWidth": 1, "rx": 0},
        ),
    ]
    for i, label in enumerate(items):
        cx = x + i * cell_w
        is_active = i == active_idx
        color = COLORS["accent"] if is_active else COLORS["text_faint"]
        # icon placeholder (square outline)
        elements.append(Rect(
            id=uuid4(), x=cx + cell_w / 2 - 9, y=y + 8, w=18, h=18,
            attrs={"fill": None, "stroke": color, "strokeWidth": 2, "rx": 3},
        ))
        # label
        elements.append(Text(
            id=uuid4(), x=cx + cell_w / 2 - len(label) * 3, y=y + 32, w=cell_w, h=16,
            attrs={"text": label, "fontSize": FONT["size_xs"], "color": color},
        ))
    return elements, h


def tabs(
    x: float, y: float, w: float, items: list[str], active_idx: int,
) -> tuple[list[Element], float]:
    h = 38
    pad = 8
    gap = 8
    n = len(items)
    if n == 0:
        return [], 0
    cell_w = (w - 2 * pad - (n - 1) * gap) / n
    elements: list[Element] = []
    for i, label in enumerate(items):
        cx = x + pad + i * (cell_w + gap)
        is_active = i == active_idx
        elements.append(Rect(
            id=uuid4(), x=cx, y=y, w=cell_w, h=h - 4,
            attrs={
                "fill": COLORS["accent"] if is_active else COLORS["surface"],
                "stroke": COLORS["accent"] if is_active else COLORS["border"],
                "strokeWidth": 1, "rx": 18,
            },
        ))
        # центрируем по горизонтали приблизительно (board не делает textAlign)
        text_x = cx + cell_w / 2 - len(label) * 3.5
        elements.append(Text(
            id=uuid4(), x=text_x, y=y + 9, w=cell_w, h=18,
            attrs={
                "text": label, "fontSize": FONT["size_sm"],
                "color": COLORS["accent_text"] if is_active else COLORS["text"],
            },
        ))
    return elements, h


def client_card(
    x: float, y: float, w: float, name: str, info: str, unread: bool = False,
) -> tuple[list[Element], float]:
    h = 76
    pad = 12
    photo = 52
    elements: list[Element] = [
        Rect(
            id=uuid4(), x=x + pad, y=y + 6, w=w - 2 * pad, h=h - 12,
            attrs={"fill": COLORS["surface"], "stroke": COLORS["border"], "strokeWidth": 1, "rx": 8},
        ),
        Rect(
            id=uuid4(), x=x + pad + 10, y=y + 18, w=photo, h=photo,
            attrs={"fill": COLORS["surface_soft"], "stroke": COLORS["border_soft"], "strokeWidth": 1, "rx": 6},
        ),
        Text(
            id=uuid4(), x=x + pad + 10 + photo + 12, y=y + 20, w=w - 2 * pad - photo - 60, h=20,
            attrs={"text": name, "fontSize": FONT["size_md"], "color": COLORS["text"], "bold": True},
        ),
        Text(
            id=uuid4(), x=x + pad + 10 + photo + 12, y=y + 44, w=w - 2 * pad - photo - 60, h=18,
            attrs={"text": info, "fontSize": FONT["size_sm"], "color": COLORS["muted"]},
        ),
    ]
    if unread:
        elements.append(Rect(
            id=uuid4(), x=x + w - pad - 24, y=y + 28, w=12, h=12,
            attrs={"fill": COLORS["danger"], "rx": 6},
        ))
    return elements, h


def banner_readonly(x: float, y: float, w: float, text: str) -> tuple[list[Element], float]:
    h = 56
    pad = 8
    return [
        _note(
            x=x + pad, y=y + pad, w=w - 2 * pad, h=h - pad - 4,
            text=text, fill=COLORS["surface_soft"],
            color=COLORS["muted"], font_size=FONT["size_sm"],
            rx=6, stroke=COLORS["border"],
        ),
    ], h


def banner_warn(x: float, y: float, w: float, text: str) -> tuple[list[Element], float]:
    h = 56
    pad = 8
    return [
        _note(
            x=x + pad, y=y + pad, w=w - 2 * pad, h=h - pad - 4,
            text=text, fill=COLORS["warn_bg"],
            color=COLORS["warn_text"], font_size=FONT["size_sm"],
            rx=6, stroke=COLORS["warn_border"],
        ),
    ], h


def subject_card(
    x: float, y: float, w: float, name: str, extra: str | None = None,
) -> tuple[list[Element], float]:
    h = 60
    pad = 8
    photo = 44
    elements = [
        Rect(
            id=uuid4(), x=x + pad, y=y + pad, w=w - 2 * pad, h=h - pad,
            attrs={"fill": COLORS["surface_soft"], "stroke": COLORS["border"], "strokeWidth": 1, "rx": 8},
        ),
        Rect(
            id=uuid4(), x=x + pad + 10, y=y + pad + 4, w=photo, h=photo,
            attrs={"fill": COLORS["surface"], "stroke": COLORS["border_soft"], "strokeWidth": 1, "rx": 6},
        ),
        Text(
            id=uuid4(), x=x + pad + 10 + photo + 10, y=y + pad + 6, w=w - 2 * pad - photo - 30, h=20,
            attrs={"text": name, "fontSize": FONT["size_md"], "color": COLORS["text"], "bold": True},
        ),
    ]
    if extra:
        elements.append(Text(
            id=uuid4(), x=x + pad + 10 + photo + 10, y=y + pad + 28, w=w - 2 * pad - photo - 30, h=18,
            attrs={"text": extra, "fontSize": FONT["size_sm"], "color": COLORS["muted"]},
        ))
    return elements, h


def _bubble(x_bubble, y, bubble_w, body, sender_label, time, fg, bg, stroke=None):
    """Внутренний хелпер: bubble = note (для word-wrap) + meta-line text."""
    # Высота: оценочно от длины body. note сам не wrap'ит — лучше использовать
    # одну строку, но для демо — оценим высоту через len(body)/wrap_chars.
    chars_per_line = max(1, int(bubble_w / 8))
    lines = max(1, -(-len(body) // chars_per_line))  # ceil
    body_h = 14 + lines * 18
    h = 18 + body_h + 6
    return [
        # Meta — наверху как text (single line, короткий)
        Rect(
            id=uuid4(), x=x_bubble, y=y, w=bubble_w, h=h,
            attrs={
                "fill": bg,
                "stroke": stroke if stroke else bg,
                "strokeWidth": 1, "rx": 12,
            },
        ),
        Text(
            id=uuid4(), x=x_bubble + 10, y=y + 6, w=bubble_w - 20, h=12,
            attrs={
                "text": f"{sender_label} · {time}",
                "fontSize": FONT["size_xs"], "color": fg,
            },
        ),
        # Body — note (wrap'a нет, но если короткий — OK)
        Text(
            id=uuid4(), x=x_bubble + 10, y=y + 24, w=bubble_w - 20, h=body_h - 14,
            attrs={
                "text": body,
                "fontSize": FONT["size_md"], "color": fg,
            },
        ),
    ], h


def msg_bubble_them(x: float, y: float, w_max: float, text: str) -> tuple[list[Element], float]:
    """Входящее сообщение (от отеля, слева)."""
    bubble_w = min(w_max * 0.75, 280)
    return _bubble(
        x_bubble=x + 8, y=y, bubble_w=bubble_w, body=text,
        sender_label="Отель", time="14:23",
        fg=COLORS["text"], bg=COLORS["surface"], stroke=COLORS["border"],
    )


def msg_bubble_me(x: float, y: float, w_max: float, text: str) -> tuple[list[Element], float]:
    """Исходящее сообщение (от клиента, справа)."""
    bubble_w = min(w_max * 0.75, 280)
    bx = x + w_max - bubble_w - 8
    return _bubble(
        x_bubble=bx, y=y, bubble_w=bubble_w, body=text,
        sender_label="Вы", time="14:24",
        fg=COLORS["accent_text"], bg=COLORS["accent"],
    )


def composer(x: float, y: float, w: float, placeholder: str = "Сообщение…") -> tuple[list[Element], float]:
    h = 56
    pad = 8
    btn_w = 100
    ta_w = w - 2 * pad - btn_w - 8
    return [
        # граница сверху — тонкий rect
        Rect(
            id=uuid4(), x=x, y=y, w=w, h=1,
            attrs={"fill": COLORS["border_soft"], "rx": 0},
        ),
        # textarea
        Rect(
            id=uuid4(), x=x + pad, y=y + pad, w=ta_w, h=h - 2 * pad,
            attrs={
                "fill": COLORS["surface"], "stroke": COLORS["border_soft"],
                "strokeWidth": 1, "rx": 6,
            },
        ),
        Text(
            id=uuid4(), x=x + pad + 10, y=y + pad + 12, w=ta_w - 20, h=16,
            attrs={"text": placeholder, "fontSize": FONT["size_md"], "color": COLORS["text_faint"]},
        ),
        # send button
        Rect(
            id=uuid4(), x=x + pad + ta_w + 8, y=y + pad, w=btn_w, h=h - 2 * pad,
            attrs={"fill": COLORS["accent"], "stroke": COLORS["accent"], "strokeWidth": 1, "rx": 4},
        ),
        Text(
            id=uuid4(), x=x + pad + ta_w + 8 + 20, y=y + pad + 12, w=btn_w, h=16,
            attrs={"text": "Отправить", "fontSize": FONT["size_md"], "color": COLORS["accent_text"], "bold": True},
        ),
    ], h
