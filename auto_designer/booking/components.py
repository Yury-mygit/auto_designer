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


# Lucide icons via iconify.design (SVG). Цвет берётся из ?color param.
# Active items используют accent (#1a73e8), inactive — #888888.
_LUCIDE_ICON = {
    # partner
    "Отели": "lucide:building-2",
    "Комнаты": "lucide:bed",
    "Брони": "lucide:calendar-days",
    "Клиенты": "lucide:users",
    "Персонал": "lucide:user",
    # client
    "Отель": "lucide:hotel",
    "Услуги": "lucide:sparkles",
}


def _icon_url(name: str, color_hex: str) -> str:
    """color_hex без '#'. iconify SVG raster через ?color=hex."""
    color = color_hex.lstrip("#")
    return f"https://api.iconify.design/{name}.svg?color=%23{color}"


def bottom_nav(
    x: float, y: float, w: float, items: list[tuple[str, str]] | list[str], active_idx: int,
) -> tuple[list[Element], float]:
    """items — список label'ов; иконки берутся из `_LUCIDE_ICON` по label'у."""
    h = 56
    n = len(items)
    cell_w = w / n
    elements: list[Element] = [
        Rect(
            id=uuid4(), x=x, y=y, w=w, h=h,
            attrs={"fill": COLORS["surface"], "stroke": COLORS["border"], "strokeWidth": 1, "rx": 0},
        ),
    ]
    for i, item in enumerate(items):
        label = item if isinstance(item, str) else item[0]
        cx = x + i * cell_w
        is_active = i == active_idx
        color_hex = COLORS["accent"] if is_active else COLORS["text_faint"]
        # icon — image с lucide SVG URL
        icon_name = _LUCIDE_ICON.get(label, "lucide:square")
        elements.append(Element(
            id=uuid4(), type="image",
            x=cx + cell_w / 2 - 11, y=y + 6, w=22, h=22,
            attrs={"src": _icon_url(icon_name, color_hex), "fit": "contain"},
        ))
        # label
        text_w = len(label) * 5.5
        elements.append(Text(
            id=uuid4(), x=cx + (cell_w - text_w) / 2, y=y + 34, w=cell_w, h=16,
            attrs={"text": label, "fontSize": FONT["size_xs"], "color": color_hex},
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


def role_card(
    x: float, y: float, w: float, label: str, description: str, icon_name: str,
) -> tuple[list[Element], float]:
    """Большая карточка выбора роли на entry-экране."""
    h = 96
    pad = 16
    icon_size = 40
    return [
        Rect(
            id=uuid4(), x=x + 12, y=y + 6, w=w - 24, h=h - 12,
            attrs={"fill": COLORS["surface"], "stroke": COLORS["border"], "strokeWidth": 1, "rx": 12},
        ),
        Element(
            id=uuid4(), type="image",
            x=x + 12 + pad, y=y + 6 + (h - 12 - icon_size) / 2, w=icon_size, h=icon_size,
            attrs={"src": _icon_url(icon_name, COLORS["accent"]), "fit": "contain"},
        ),
        Text(
            id=uuid4(), x=x + 12 + pad + icon_size + 12, y=y + 24, w=w - 100, h=22,
            attrs={"text": label, "fontSize": FONT["size_lg"], "color": COLORS["text"], "bold": True},
        ),
        Text(
            id=uuid4(), x=x + 12 + pad + icon_size + 12, y=y + 52, w=w - 100, h=18,
            attrs={"text": description, "fontSize": FONT["size_sm"], "color": COLORS["muted"]},
        ),
    ], h


def hotel_list_card(
    x: float, y: float, w: float, name: str, city: str, meta: str,
) -> tuple[list[Element], float]:
    """Карточка отеля в общем списке (client/hotels или partner/hotels_list)."""
    h = 88
    pad = 12
    photo = 64
    return [
        Rect(
            id=uuid4(), x=x + 8, y=y + 4, w=w - 16, h=h - 8,
            attrs={"fill": COLORS["surface"], "stroke": COLORS["border"], "strokeWidth": 1, "rx": 8},
        ),
        Rect(
            id=uuid4(), x=x + 18, y=y + 16, w=photo, h=photo - 16,
            attrs={"fill": COLORS["surface_soft"], "stroke": COLORS["border_soft"], "strokeWidth": 1, "rx": 6},
        ),
        Text(
            id=uuid4(), x=x + 18 + photo / 2 - 10, y=y + 36, w=20, h=20,
            attrs={"text": "🏨", "fontSize": 18, "color": COLORS["text_faint"]},
        ),
        Text(
            id=uuid4(), x=x + 18 + photo + 14, y=y + 18, w=w - 60 - photo, h=20,
            attrs={"text": name, "fontSize": FONT["size_md"], "color": COLORS["text"], "bold": True},
        ),
        Text(
            id=uuid4(), x=x + 18 + photo + 14, y=y + 40, w=w - 60 - photo, h=18,
            attrs={"text": city, "fontSize": FONT["size_sm"], "color": COLORS["muted"]},
        ),
        Text(
            id=uuid4(), x=x + 18 + photo + 14, y=y + 60, w=w - 60 - photo, h=16,
            attrs={"text": meta, "fontSize": FONT["size_xs"], "color": COLORS["text_faint"]},
        ),
    ], h


def form_field(
    x: float, y: float, w: float, label: str, value: str, multiline: bool = False,
) -> tuple[list[Element], float]:
    """Form field: label сверху, input под ним. value — текущее значение."""
    h = 70 if not multiline else 96
    pad = 12
    elements: list[Element] = [
        Text(
            id=uuid4(), x=x + pad, y=y + 2, w=w - 2 * pad, h=16,
            attrs={"text": label, "fontSize": FONT["size_xs"], "color": COLORS["muted"]},
        ),
        Rect(
            id=uuid4(), x=x + pad, y=y + 22, w=w - 2 * pad, h=h - 30,
            attrs={"fill": COLORS["surface"], "stroke": COLORS["border"], "strokeWidth": 1, "rx": 6},
        ),
        Text(
            id=uuid4(), x=x + pad + 10, y=y + 22 + 12, w=w - 2 * pad - 20, h=18,
            attrs={"text": value, "fontSize": FONT["size_md"], "color": COLORS["text"]},
        ),
    ]
    return elements, h


def primary_button(
    x: float, y: float, w: float, label: str, disabled: bool = False,
) -> tuple[list[Element], float]:
    """Большая кнопка primary внизу экранов."""
    h = 48
    pad = 12
    fill = "#aaaaaa" if disabled else COLORS["accent"]
    btn_x = x + pad
    btn_w = w - 2 * pad
    text_w = len(label) * 8.5
    text_x = btn_x + max(8, (btn_w - text_w) / 2)
    return [
        Rect(
            id=uuid4(), x=btn_x, y=y, w=btn_w, h=h,
            attrs={"fill": fill, "stroke": fill, "strokeWidth": 1, "rx": 6},
        ),
        Text(
            id=uuid4(), x=text_x, y=y + 14, w=text_w + 4, h=18,
            attrs={"text": label, "fontSize": FONT["size_md"], "color": COLORS["accent_text"], "bold": True},
        ),
    ], h


def pay_method(
    x: float, y: float, w: float, name: str, logo_text: str, selected: bool = False,
) -> tuple[list[Element], float]:
    """Метод оплаты: rect + logo placeholder + name + radio."""
    h = 56
    pad = 12
    radio = 18
    return [
        Rect(
            id=uuid4(), x=x + pad, y=y + 6, w=w - 2 * pad, h=h - 12,
            attrs={
                "fill": COLORS["surface"],
                "stroke": COLORS["accent"] if selected else COLORS["border"],
                "strokeWidth": 2 if selected else 1, "rx": 8,
            },
        ),
        # logo placeholder
        Rect(
            id=uuid4(), x=x + pad + 10, y=y + 14, w=44, h=28,
            attrs={"fill": COLORS["surface_soft"], "stroke": COLORS["border_soft"], "strokeWidth": 1, "rx": 4},
        ),
        Text(
            id=uuid4(), x=x + pad + 14, y=y + 20, w=36, h=18,
            attrs={"text": logo_text, "fontSize": FONT["size_xs"], "color": COLORS["text"], "bold": True},
        ),
        Text(
            id=uuid4(), x=x + pad + 66, y=y + 20, w=w - 130, h=18,
            attrs={"text": name, "fontSize": FONT["size_md"], "color": COLORS["text"]},
        ),
        # radio
        Rect(
            id=uuid4(), x=x + w - pad - 30, y=y + 18, w=radio, h=radio,
            attrs={
                "fill": COLORS["accent"] if selected else "transparent",
                "stroke": COLORS["accent"] if selected else COLORS["border"],
                "strokeWidth": 2, "rx": 9,
            },
        ),
    ], h


def partner_booking_card(
    x: float, y: float, w: float, code: str, client: str, room: str,
    dates: str, total: str, status: str, status_color: str,
) -> tuple[list[Element], float]:
    """Карточка брони в партнёрском списке. status_color — accent/success/danger."""
    h = 124
    pad = 14
    return [
        Rect(
            id=uuid4(), x=x + 8, y=y + 4, w=w - 16, h=h - 8,
            attrs={"fill": COLORS["surface"], "stroke": COLORS["border"], "strokeWidth": 1, "rx": 10},
        ),
        # code + status pill (top row)
        Text(
            id=uuid4(), x=x + 20, y=y + 14, w=180, h=18,
            attrs={"text": code, "fontSize": FONT["size_sm"], "color": COLORS["muted"]},
        ),
        Rect(
            id=uuid4(), x=x + w - 110, y=y + 12, w=92, h=22,
            attrs={"fill": status_color, "stroke": status_color, "strokeWidth": 1, "rx": 11},
        ),
        Text(
            id=uuid4(), x=x + w - 104, y=y + 16, w=80, h=16,
            attrs={"text": status, "fontSize": FONT["size_xs"], "color": "#ffffff", "bold": True},
        ),
        # client + room (middle)
        Text(
            id=uuid4(), x=x + 20, y=y + 40, w=w - 40, h=20,
            attrs={"text": client, "fontSize": FONT["size_md"], "color": COLORS["text"], "bold": True},
        ),
        Text(
            id=uuid4(), x=x + 20, y=y + 62, w=w - 40, h=18,
            attrs={"text": room, "fontSize": FONT["size_sm"], "color": COLORS["muted"]},
        ),
        # dates + total (bottom row)
        Text(
            id=uuid4(), x=x + 20, y=y + 86, w=w / 2, h=18,
            attrs={"text": dates, "fontSize": FONT["size_sm"], "color": COLORS["text"]},
        ),
        Text(
            id=uuid4(), x=x + w - 130, y=y + 86, w=120, h=20,
            attrs={"text": total, "fontSize": FONT["size_md"], "color": COLORS["text"], "bold": True},
        ),
    ], h


def room_card_partner(
    x: float, y: float, w: float, name: str, meta: str, price: str, published: bool,
) -> tuple[list[Element], float]:
    """Карточка комнаты в партнёрском списке (без Забронировать)."""
    h = 100
    pad = 12
    photo = 64
    return [
        Rect(
            id=uuid4(), x=x + 8, y=y + 4, w=w - 16, h=h - 8,
            attrs={"fill": COLORS["surface"], "stroke": COLORS["border"], "strokeWidth": 1, "rx": 8},
        ),
        Rect(
            id=uuid4(), x=x + 18, y=y + 18, w=photo, h=photo,
            attrs={"fill": COLORS["surface_soft"], "stroke": COLORS["border_soft"], "strokeWidth": 1, "rx": 6},
        ),
        Text(
            id=uuid4(), x=x + 18 + photo / 2 - 12, y=y + 18 + photo / 2 - 8, w=24, h=20,
            attrs={"text": "🛏", "fontSize": 22, "color": COLORS["text_faint"]},
        ),
        Text(
            id=uuid4(), x=x + 18 + photo + 14, y=y + 16, w=w - 100 - photo, h=20,
            attrs={"text": name, "fontSize": FONT["size_md"], "color": COLORS["text"], "bold": True},
        ),
        Text(
            id=uuid4(), x=x + 18 + photo + 14, y=y + 40, w=w - 100 - photo, h=18,
            attrs={"text": meta, "fontSize": FONT["size_sm"], "color": COLORS["muted"]},
        ),
        Text(
            id=uuid4(), x=x + 18 + photo + 14, y=y + 60, w=w - 100 - photo, h=18,
            attrs={"text": price, "fontSize": FONT["size_md"], "color": COLORS["text"], "bold": True},
        ),
        # status pill top-right
        Rect(
            id=uuid4(), x=x + w - 110, y=y + 12, w=92, h=22,
            attrs={
                "fill": COLORS["success"] if published else COLORS["text_faint"],
                "stroke": COLORS["success"] if published else COLORS["text_faint"],
                "strokeWidth": 1, "rx": 11,
            },
        ),
        Text(
            id=uuid4(), x=x + w - 100, y=y + 16, w=80, h=16,
            attrs={
                "text": "опубликовано" if published else "черновик",
                "fontSize": FONT["size_xs"], "color": "#ffffff", "bold": True,
            },
        ),
    ], h


def staff_card(
    x: float, y: float, w: float, name: str, perm_summary: str, chat: bool,
) -> tuple[list[Element], float]:
    """Карточка staff с perm-summary + чат-флаг + edit-icon."""
    h = 76
    pad = 12
    return [
        Rect(
            id=uuid4(), x=x + 8, y=y + 4, w=w - 16, h=h - 8,
            attrs={"fill": COLORS["surface"], "stroke": COLORS["border"], "strokeWidth": 1, "rx": 8},
        ),
        # avatar placeholder
        Rect(
            id=uuid4(), x=x + 18, y=y + 16, w=44, h=44,
            attrs={"fill": COLORS["surface_soft"], "stroke": COLORS["border_soft"], "strokeWidth": 1, "rx": 22},
        ),
        Element(
            id=uuid4(), type="image",
            x=x + 18 + 12, y=y + 16 + 12, w=20, h=20,
            attrs={"src": _icon_url("lucide:user", COLORS["text_faint"]), "fit": "contain"},
        ),
        Text(
            id=uuid4(), x=x + 18 + 56, y=y + 18, w=w - 130 - 56, h=20,
            attrs={"text": name, "fontSize": FONT["size_md"], "color": COLORS["text"], "bold": True},
        ),
        Text(
            id=uuid4(), x=x + 18 + 56, y=y + 42, w=w - 130 - 56, h=18,
            attrs={"text": perm_summary, "fontSize": FONT["size_xs"], "color": COLORS["muted"]},
        ),
        # chat-icon если chat=True
        Element(
            id=uuid4(), type="image",
            x=x + w - 60, y=y + 22, w=22, h=22,
            attrs={
                "src": _icon_url("lucide:message-circle", COLORS["accent"] if chat else COLORS["text_faint"]),
                "fit": "contain",
            },
        ),
        # edit icon
        Element(
            id=uuid4(), type="image",
            x=x + w - 30, y=y + 22, w=22, h=22,
            attrs={"src": _icon_url("lucide:settings-2", COLORS["text_faint"]), "fit": "contain"},
        ),
    ], h


def calendar_grid(
    x: float, y: float, w: float, rows: list[tuple[str, list[str]]],
    days: list[str],
) -> tuple[list[Element], float]:
    """Календарь занятости: header (days) + rows of (room_name, [status, ...]).
    status ∈ {"free", "booked", "blocked"}.
    """
    header_h = 28
    row_h = 36
    name_w = 110
    cells = len(days)
    cell_w = (w - name_w - 8) / cells
    elements: list[Element] = []
    # header
    elements.append(Rect(
        id=uuid4(), x=x + 8, y=y, w=w - 16, h=header_h,
        attrs={"fill": COLORS["surface_soft"], "stroke": COLORS["border"], "strokeWidth": 1, "rx": 6},
    ))
    elements.append(Text(
        id=uuid4(), x=x + 16, y=y + 7, w=name_w - 8, h=16,
        attrs={"text": "Комната / День", "fontSize": FONT["size_xs"], "color": COLORS["muted"], "bold": True},
    ))
    for i, d in enumerate(days):
        cx = x + 8 + name_w + i * cell_w
        elements.append(Text(
            id=uuid4(), x=cx + cell_w / 2 - 12, y=y + 7, w=cell_w, h=16,
            attrs={"text": d, "fontSize": FONT["size_xs"], "color": COLORS["muted"]},
        ))
    cur_y = y + header_h + 4
    # rows
    color_map = {
        "free": COLORS["surface"],
        "booked": COLORS["accent"],
        "blocked": "#aaaaaa",
    }
    for room_name, row in rows:
        elements.append(Text(
            id=uuid4(), x=x + 16, y=cur_y + 10, w=name_w - 8, h=18,
            attrs={"text": room_name, "fontSize": FONT["size_sm"], "color": COLORS["text"], "bold": True},
        ))
        for i, status in enumerate(row):
            cx = x + 8 + name_w + i * cell_w
            fill = color_map.get(status, COLORS["surface"])
            elements.append(Rect(
                id=uuid4(), x=cx + 2, y=cur_y, w=cell_w - 4, h=row_h - 4,
                attrs={"fill": fill, "stroke": COLORS["border"], "strokeWidth": 1, "rx": 4},
            ))
        cur_y += row_h
    return elements, (cur_y - y) + 4


def service_card(
    x: float, y: float, w: float, name: str, description: str, price: str,
) -> tuple[list[Element], float]:
    h = 88
    pad = 12
    return [
        Rect(
            id=uuid4(), x=x + 8, y=y + 4, w=w - 16, h=h - 8,
            attrs={"fill": COLORS["surface"], "stroke": COLORS["border"], "strokeWidth": 1, "rx": 8},
        ),
        Text(
            id=uuid4(), x=x + 20, y=y + 14, w=w - 130, h=20,
            attrs={"text": name, "fontSize": FONT["size_md"], "color": COLORS["text"], "bold": True},
        ),
        Text(
            id=uuid4(), x=x + 20, y=y + 36, w=w - 130, h=18,
            attrs={"text": description, "fontSize": FONT["size_sm"], "color": COLORS["muted"]},
        ),
        Text(
            id=uuid4(), x=x + w - 120, y=y + 14, w=100, h=20,
            attrs={"text": price, "fontSize": FONT["size_md"], "color": COLORS["accent"], "bold": True},
        ),
    ], h


def info_screen(
    x: float, y: float, w: float, icon_name: str, heading: str, text: str,
) -> list[Element]:
    """Центрированный info-блок (для pending/empty states)."""
    cx = x + w / 2
    return [
        Element(
            id=uuid4(), type="image",
            x=cx - 36, y=y, w=72, h=72,
            attrs={"src": _icon_url(icon_name, COLORS["accent"]), "fit": "contain"},
        ),
        Text(
            id=uuid4(), x=x + 24, y=y + 92, w=w - 48, h=24,
            attrs={"text": heading, "fontSize": FONT["size_xl"], "color": COLORS["text"], "bold": True},
        ),
        Text(
            id=uuid4(), x=x + 24, y=y + 124, w=w - 48, h=18,
            attrs={"text": text, "fontSize": FONT["size_sm"], "color": COLORS["muted"]},
        ),
    ]


def setting_row(
    x: float, y: float, w: float, label: str, value: str, has_chevron: bool = True,
) -> tuple[list[Element], float]:
    h = 56
    pad = 16
    elements: list[Element] = [
        Rect(
            id=uuid4(), x=x + 8, y=y + 4, w=w - 16, h=h - 8,
            attrs={"fill": COLORS["surface"], "stroke": COLORS["border_soft"], "strokeWidth": 1, "rx": 8},
        ),
        Text(
            id=uuid4(), x=x + pad + 4, y=y + 12, w=w / 2 - pad, h=18,
            attrs={"text": label, "fontSize": FONT["size_md"], "color": COLORS["text"]},
        ),
        Text(
            id=uuid4(), x=x + pad + 4, y=y + 32, w=w - 60 - pad, h=16,
            attrs={"text": value, "fontSize": FONT["size_sm"], "color": COLORS["muted"]},
        ),
    ]
    if has_chevron:
        elements.append(Element(
            id=uuid4(), type="image",
            x=x + w - 36, y=y + 20, w=16, h=16,
            attrs={"src": _icon_url("lucide:chevron-right", COLORS["text_faint"]), "fit": "contain"},
        ))
    return elements, h


def metric_card(
    x: float, y: float, w: float, h: float, value: str, label: str, delta: str | None = None,
) -> list[Element]:
    elements = [
        Rect(
            id=uuid4(), x=x, y=y, w=w, h=h,
            attrs={"fill": COLORS["surface"], "stroke": COLORS["border"], "strokeWidth": 1, "rx": 10},
        ),
        Text(
            id=uuid4(), x=x + 14, y=y + 14, w=w - 28, h=16,
            attrs={"text": label, "fontSize": FONT["size_xs"], "color": COLORS["muted"]},
        ),
        Text(
            id=uuid4(), x=x + 14, y=y + 32, w=w - 28, h=28,
            attrs={"text": value, "fontSize": FONT["size_xl"], "color": COLORS["text"], "bold": True},
        ),
    ]
    if delta:
        elements.append(Text(
            id=uuid4(), x=x + 14, y=y + 64, w=w - 28, h=16,
            attrs={"text": delta, "fontSize": FONT["size_xs"], "color": COLORS["success"]},
        ))
    return elements


def admin_table_row(
    x: float, y: float, w: float, cells: list[tuple[str, float]],
    bg: str | None = None,
) -> tuple[list[Element], float]:
    """cells = [(text, width_pct), ...] — суммарно 1.0. bg для зебры/header."""
    h = 40
    pad = 12
    elements: list[Element] = []
    if bg:
        elements.append(Rect(
            id=uuid4(), x=x, y=y, w=w, h=h,
            attrs={"fill": bg, "rx": 0},
        ))
    # bottom divider
    elements.append(Rect(
        id=uuid4(), x=x + pad, y=y + h - 1, w=w - 2 * pad, h=1,
        attrs={"fill": COLORS["border_soft"], "rx": 0},
    ))
    cx = x + pad
    for text, pct in cells:
        cw = (w - 2 * pad) * pct
        elements.append(Text(
            id=uuid4(), x=cx, y=y + 12, w=cw, h=18,
            attrs={"text": text, "fontSize": FONT["size_sm"], "color": COLORS["text"]},
        ))
        cx += cw
    return elements, h


def map_placeholder(
    x: float, y: float, w: float, h: float, pin_label: str,
) -> list[Element]:
    """Заглушка карты с пин-маркером."""
    return [
        Rect(
            id=uuid4(), x=x, y=y, w=w, h=h,
            attrs={"fill": "#e3eaf3", "stroke": COLORS["border"], "strokeWidth": 1, "rx": 8},
        ),
        # фейковые «дороги» — линии
        Rect(id=uuid4(), x=x + 20, y=y + h / 3, w=w - 40, h=2, attrs={"fill": "#ffffff", "rx": 1}),
        Rect(id=uuid4(), x=x + w / 3, y=y + 20, w=2, h=h - 40, attrs={"fill": "#ffffff", "rx": 1}),
        Rect(id=uuid4(), x=x + 30, y=y + 2 * h / 3, w=w / 2, h=2, attrs={"fill": "#ffffff", "rx": 1}),
        # pin
        Element(
            id=uuid4(), type="image",
            x=x + w / 2 - 14, y=y + h / 2 - 14, w=28, h=28,
            attrs={"src": _icon_url("lucide:map-pin", COLORS["danger"]), "fit": "contain"},
        ),
        Rect(
            id=uuid4(), x=x + w / 2 - 60, y=y + h / 2 + 18, w=120, h=24,
            attrs={"fill": COLORS["surface"], "stroke": COLORS["border"], "strokeWidth": 1, "rx": 4},
        ),
        Text(
            id=uuid4(), x=x + w / 2 - 50, y=y + h / 2 + 23, w=100, h=16,
            attrs={"text": pin_label, "fontSize": FONT["size_xs"], "color": COLORS["text"], "bold": True},
        ),
    ]


def chat_icon_btn(x: float, y: float, color_hex: str | None = None) -> Element:
    """Маленькая кнопка-иконка чата (lucide:message-circle) для карточек
    комнаты / брони / hotel_detail."""
    color = color_hex or COLORS["accent"]
    return Element(
        id=uuid4(), type="image",
        x=x, y=y, w=28, h=28,
        attrs={"src": _icon_url("lucide:message-circle", color), "fit": "contain"},
    )


def hotel_head(
    x: float, y: float, w: float, name: str, address: str, photo_h: int = 180,
) -> tuple[list[Element], float]:
    """Hotel detail head: фото-плейсхолдер + название + адрес + chat-btn."""
    pad = 12
    elements: list[Element] = [
        # photo placeholder — hero
        Rect(
            id=uuid4(), x=x, y=y, w=w, h=photo_h,
            attrs={"fill": COLORS["surface_soft"], "stroke": None, "rx": 0},
        ),
        Text(
            id=uuid4(), x=x + w / 2 - 20, y=y + photo_h / 2 - 8, w=40, h=20,
            attrs={"text": "🏨", "fontSize": 32, "color": COLORS["text_faint"]},
        ),
    ]
    # info-block под фото
    info_y = y + photo_h
    name_w = w - 2 * pad - 40  # минус кнопка-чат справа
    elements.extend([
        Rect(
            id=uuid4(), x=x, y=info_y, w=w, h=70,
            attrs={"fill": COLORS["surface"], "stroke": COLORS["border"], "strokeWidth": 1, "rx": 0},
        ),
        Text(
            id=uuid4(), x=x + pad, y=info_y + 12, w=name_w, h=22,
            attrs={"text": name, "fontSize": FONT["size_lg"], "color": COLORS["text"], "bold": True},
        ),
        Text(
            id=uuid4(), x=x + pad, y=info_y + 38, w=name_w, h=18,
            attrs={"text": address, "fontSize": FONT["size_sm"], "color": COLORS["muted"]},
        ),
        chat_icon_btn(x + w - pad - 28, info_y + 22),
    ])
    return elements, photo_h + 70


def hotel_tabs(x: float, y: float, w: float, active: str) -> tuple[list[Element], float]:
    """Topbar tabs Отель / Комнаты / Услуги."""
    h = 44
    items = ["Отель", "Комнаты", "Услуги"]
    cell_w = w / len(items)
    elements: list[Element] = [
        Rect(
            id=uuid4(), x=x, y=y, w=w, h=h,
            attrs={"fill": COLORS["surface"], "stroke": COLORS["border_soft"], "strokeWidth": 1, "rx": 0},
        ),
    ]
    for i, label in enumerate(items):
        cx = x + i * cell_w
        is_active = label == active
        color = COLORS["accent"] if is_active else COLORS["text_faint"]
        text_w = len(label) * 7.5
        elements.append(Text(
            id=uuid4(), x=cx + (cell_w - text_w) / 2, y=y + 14, w=cell_w, h=18,
            attrs={"text": label, "fontSize": FONT["size_md"], "color": color, "bold": is_active},
        ))
        if is_active:
            # underline 2px accent
            elements.append(Rect(
                id=uuid4(), x=cx + cell_w / 4, y=y + h - 2, w=cell_w / 2, h=2,
                attrs={"fill": COLORS["accent"], "rx": 1},
            ))
    return elements, h


def room_card(
    x: float, y: float, w: float, name: str, meta: str, price: str,
    available: bool = True,
) -> tuple[list[Element], float]:
    """Карточка комнаты: фото + name + meta + price + Забронировать-btn + chat-icon."""
    h = 130
    pad = 12
    photo_h = 70
    elements: list[Element] = [
        Rect(
            id=uuid4(), x=x + 8, y=y + 4, w=w - 16, h=h - 8,
            attrs={"fill": COLORS["surface"], "stroke": COLORS["border"], "strokeWidth": 1, "rx": 10},
        ),
        # photo
        Rect(
            id=uuid4(), x=x + 18, y=y + 14, w=photo_h, h=photo_h,
            attrs={"fill": COLORS["surface_soft"], "stroke": COLORS["border_soft"], "strokeWidth": 1, "rx": 6},
        ),
        Text(
            id=uuid4(), x=x + 18 + photo_h / 2 - 12, y=y + 14 + photo_h / 2 - 8, w=24, h=20,
            attrs={"text": "🛏", "fontSize": 22, "color": COLORS["text_faint"]},
        ),
        # name
        Text(
            id=uuid4(), x=x + 18 + photo_h + 12, y=y + 14, w=w - 60 - photo_h - 30, h=20,
            attrs={"text": name, "fontSize": FONT["size_md"], "color": COLORS["text"], "bold": True},
        ),
        # meta
        Text(
            id=uuid4(), x=x + 18 + photo_h + 12, y=y + 36, w=w - 60 - photo_h, h=16,
            attrs={"text": meta, "fontSize": FONT["size_sm"], "color": COLORS["muted"]},
        ),
        # price
        Text(
            id=uuid4(), x=x + 18 + photo_h + 12, y=y + 56, w=w - 60 - photo_h, h=18,
            attrs={"text": price, "fontSize": FONT["size_md"], "color": COLORS["text"], "bold": True},
        ),
        # chat icon top-right
        chat_icon_btn(x + w - 18 - 28, y + 14),
    ]
    # Забронировать button внизу карточки
    btn_y = y + h - 36
    btn_w = w - 36
    if available:
        elements.append(Rect(
            id=uuid4(), x=x + 18, y=btn_y, w=btn_w, h=28,
            attrs={"fill": COLORS["accent"], "stroke": COLORS["accent"], "strokeWidth": 1, "rx": 4},
        ))
        text_w = len("Забронировать") * 8.5
        elements.append(Text(
            id=uuid4(), x=x + 18 + (btn_w - text_w) / 2, y=btn_y + 6, w=btn_w, h=18,
            attrs={"text": "Забронировать", "fontSize": FONT["size_md"], "color": COLORS["accent_text"], "bold": True},
        ))
    else:
        elements.append(Rect(
            id=uuid4(), x=x + 18, y=btn_y, w=btn_w, h=28,
            attrs={"fill": COLORS["disabled_bg"] if "disabled_bg" in COLORS else "#aaaaaa", "stroke": None, "rx": 4},
        ))
        text_w = len("Недоступно") * 8.5
        elements.append(Text(
            id=uuid4(), x=x + 18 + (btn_w - text_w) / 2, y=btn_y + 6, w=btn_w, h=18,
            attrs={"text": "Недоступно", "fontSize": FONT["size_md"], "color": COLORS["surface"], "bold": True},
        ))
    return elements, h


def booking_card(
    x: float, y: float, w: float, code: str, hotel: str, dates: str,
    price: str, status: str,
) -> tuple[list[Element], float]:
    """Карточка брони: code + hotel + dates + price + status + chat-icon + pay-btn."""
    h = 132
    pad = 12
    elements: list[Element] = [
        Rect(
            id=uuid4(), x=x + 8, y=y + 4, w=w - 16, h=h - 8,
            attrs={"fill": COLORS["surface"], "stroke": COLORS["border"], "strokeWidth": 1, "rx": 10},
        ),
        Text(
            id=uuid4(), x=x + 20, y=y + 14, w=w - 80, h=18,
            attrs={"text": f"Код: {code}", "fontSize": FONT["size_sm"], "color": COLORS["muted"]},
        ),
        Text(
            id=uuid4(), x=x + 20, y=y + 34, w=w - 80, h=20,
            attrs={"text": hotel, "fontSize": FONT["size_md"], "color": COLORS["text"], "bold": True},
        ),
        Text(
            id=uuid4(), x=x + 20, y=y + 58, w=w - 40, h=18,
            attrs={"text": dates, "fontSize": FONT["size_sm"], "color": COLORS["text"]},
        ),
        Text(
            id=uuid4(), x=x + 20, y=y + 78, w=w - 40, h=20,
            attrs={"text": price, "fontSize": FONT["size_md"], "color": COLORS["text"], "bold": True},
        ),
        Text(
            id=uuid4(), x=x + 20, y=y + 100, w=w - 80, h=18,
            attrs={"text": status, "fontSize": FONT["size_xs"], "color": COLORS["muted"]},
        ),
        # chat icon top-right
        chat_icon_btn(x + w - 20 - 28, y + 14),
    ]
    return elements, h


def composer(x: float, y: float, w: float, placeholder: str = "Сообщение…") -> tuple[list[Element], float]:
    h = 56
    pad = 8
    btn_w = 110
    ta_w = w - 2 * pad - btn_w - 8
    btn_x = x + pad + ta_w + 8
    btn_label = "Отправить"
    # Без поддержки textAlign center'им text «руками»; кириллица bold ~8.5px/char.
    btn_text_w = len(btn_label) * 8.5
    btn_text_x = btn_x + max(8, (btn_w - btn_text_w) / 2)
    return [
        # граница сверху
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
            id=uuid4(), x=btn_x, y=y + pad, w=btn_w, h=h - 2 * pad,
            attrs={"fill": COLORS["accent"], "stroke": COLORS["accent"], "strokeWidth": 1, "rx": 4},
        ),
        Text(
            id=uuid4(), x=btn_text_x, y=y + pad + 12, w=btn_text_w + 4, h=16,
            attrs={"text": btn_label, "fontSize": FONT["size_md"], "color": COLORS["accent_text"], "bold": True},
        ),
    ], h
