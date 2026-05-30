"""Full-screen фреймы booking.

Каждая функция возвращает Frame с вложенными child-элементами.
external_ref + id фрейма берётся из refs.json (где живёт persistent mapping
screen_name → {frame_id, external_ref}).
"""
from __future__ import annotations

from uuid import UUID

from auto_designer.booking.components import (
    banner_readonly,
    banner_warn,
    bottom_nav,
    client_card,
    composer,
    msg_bubble_me,
    msg_bubble_them,
    subject_card,
    subtitle_bar,
    tabs,
    topbar,
)
from auto_designer.booking.constants import ARTBOARD_H, ARTBOARD_W, COLORS, FONT
from auto_designer.core.primitives import Element, Frame, Rect, Text


def chat_thread(
    frame_id: UUID,
    external_ref: UUID,
    x: float = 0,
    y: float = 0,
    bot_blocked: bool = False,
) -> Frame:
    """Экран `client/chat/thread/<id>` (Этап 5 client-hotel-chat карты).

    Состав:
      - topbar «Отель Ала-Тоо Бутик-Стэй»
      - (опц.) warn-banner bot_blocked
      - subject_card (бронь BK-001)
      - 3 сообщения (them/me/them)
      - composer внизу
    """
    children: list[Element] = []
    cur_y: float = 0

    # фон artboard'а
    children.append(Rect(
        id=__import__("uuid").uuid4(), x=0, y=0, w=ARTBOARD_W, h=ARTBOARD_H,
        attrs={"fill": COLORS["bg"]},
    ))

    # topbar
    children.extend(topbar(0, cur_y, ARTBOARD_W, "Отель Ала-Тоо Бутик-Стэй"))
    cur_y += 56

    # banner (если bot_blocked)
    if bot_blocked:
        els, dh = banner_warn(
            0, cur_y, ARTBOARD_W,
            "Нажмите Start у @rforge_stay_bot, чтобы получать уведомления.",
        )
        children.extend(els)
        cur_y += dh

    # subject card
    els, dh = subject_card(0, cur_y, ARTBOARD_W, "Бронь BK-2026-001", "12—15 июня · номер 12")
    children.extend(els)
    cur_y += dh

    # messages area
    cur_y += 8
    list_y = cur_y
    els, dh = msg_bubble_them(0, list_y, ARTBOARD_W, "Здравствуйте! Подскажите, пожалуйста, во сколько заезд?")
    children.extend(els)
    list_y += dh + 8
    els, dh = msg_bubble_me(0, list_y, ARTBOARD_W, "В 14:00.")
    children.extend(els)
    list_y += dh + 8
    els, dh = msg_bubble_them(0, list_y, ARTBOARD_W, "Спасибо! Можно с собакой?")
    children.extend(els)
    list_y += dh + 8

    # composer прижат к низу artboard'а
    composer_y = ARTBOARD_H - 56
    els, _ = composer(0, composer_y, ARTBOARD_W)
    children.extend(els)

    return Frame(
        id=frame_id,
        external_ref=external_ref,
        x=x,
        y=y,
        w=ARTBOARD_W,
        h=ARTBOARD_H,
        attrs={"title": "client/chat/thread", "fill": COLORS["bg"]},
        children=children,
    )


_PARTNER_NAV = ["Отели", "Комнаты", "Брони", "Клиенты", "Персонал"]


def partner_clients_list(frame_id: UUID, external_ref: UUID, x: float = 0, y: float = 0) -> Frame:
    """partner/views/clients_list — вкладка «Клиенты» партнёра."""
    children: list[Element] = []

    # фон
    children.append(Rect(
        id=__import__("uuid").uuid4(), x=0, y=0, w=ARTBOARD_W, h=ARTBOARD_H,
        attrs={"fill": COLORS["bg"]},
    ))

    cur_y: float = 0
    children.extend(topbar(0, cur_y, ARTBOARD_W, "rforge_booking_bot"))
    cur_y += 56

    els, dh = subtitle_bar(0, cur_y, ARTBOARD_W, "Клиенты")
    children.extend(els)
    cur_y += dh

    # 4 client cards (вторая — с unread badge)
    sample = [
        ("Yury", "Бронирований: 10 · Последняя: 2026-05-28", False),
        ("Зохид", "Бронирований: 3 · Последняя: 2026-05-22", True),
        ("Иван Петров", "996555123456 · Бронирований: 2 · 2026-06-20", False),
        ("TestClient", "Бронирований: 1 · Последняя: 2026-06-01", False),
    ]
    cur_y += 4
    for name, info, unread in sample:
        els, dh = client_card(0, cur_y, ARTBOARD_W, name, info, unread=unread)
        children.extend(els)
        cur_y += dh + 4

    # bottom nav прижат к низу
    nav_y = ARTBOARD_H - 56
    els, _ = bottom_nav(0, nav_y, ARTBOARD_W, _PARTNER_NAV, active_idx=3)
    children.extend(els)

    return Frame(
        id=frame_id, external_ref=external_ref,
        x=x, y=y, w=ARTBOARD_W, h=ARTBOARD_H,
        attrs={"title": "partner/clients_list", "fill": COLORS["bg"]},
        children=children,
    )


def partner_client_edit_chat(
    frame_id: UUID, external_ref: UUID, x: float = 0, y: float = 0,
    can_write: bool = False,
) -> Frame:
    """partner/views/client_edit — карточка клиента с inline-чатом.

    can_write=False → readonly banner (текущий defaultный сценарий для
    staff без `perm_chat_with_clients`).
    """
    children: list[Element] = []
    children.append(Rect(
        id=__import__("uuid").uuid4(), x=0, y=0, w=ARTBOARD_W, h=ARTBOARD_H,
        attrs={"fill": COLORS["bg"]},
    ))

    cur_y: float = 0
    children.extend(topbar(0, cur_y, ARTBOARD_W, "rforge_booking_bot"))
    cur_y += 56

    els, dh = subtitle_bar(0, cur_y, ARTBOARD_W, "Клиент / Карточка клиента")
    children.extend(els)
    cur_y += dh

    # client info card (свёрнут — мы рисуем чат, форму над ним обозначим)
    cur_y += 6
    children.append(Rect(
        id=__import__("uuid").uuid4(), x=8, y=cur_y, w=ARTBOARD_W - 16, h=56,
        attrs={"fill": COLORS["surface"], "stroke": COLORS["border"], "strokeWidth": 1, "radius": 8},
    ))
    children.append(Text(
        id=__import__("uuid").uuid4(), x=20, y=cur_y + 10, w=ARTBOARD_W - 40, h=16,
        attrs={"text": "2026-05-19 → 2026-05-21 (1 гостей)", "fontSize": FONT["size_sm"],
               "color": COLORS["muted"], "fontFamily": FONT["family"]},
    ))
    children.append(Text(
        id=__import__("uuid").uuid4(), x=20, y=cur_y + 30, w=ARTBOARD_W - 40, h=16,
        attrs={"text": "6000 сом", "fontSize": FONT["size_md"],
               "color": COLORS["text"], "fontFamily": FONT["family"], "fontWeight": "600"},
    ))
    cur_y += 70

    # «Чат с отелем» heading
    children.append(Text(
        id=__import__("uuid").uuid4(), x=14, y=cur_y, w=ARTBOARD_W - 28, h=20,
        attrs={"text": "Чат с отелем", "fontSize": FONT["size_lg"],
               "color": COLORS["text"], "fontFamily": FONT["family"], "fontWeight": "600"},
    ))
    cur_y += 28

    # tabs отелей
    els, dh = tabs(0, cur_y, ARTBOARD_W, ["Ала-Тоо Бутик-Стэй", "Манас Гарден Отель"], active_idx=0)
    children.extend(els)
    cur_y += dh

    # readonly banner (если can_write=False)
    if not can_write:
        els, dh = banner_readonly(
            0, cur_y, ARTBOARD_W,
            "Только просмотр. У вас нет прав на отправку сообщений (chat_with_clients).",
        )
        children.extend(els)
        cur_y += dh

    # пара входящих сообщений (от клиента — на стороне партнёра это them)
    cur_y += 6
    msgs = [("30.05, 03:25", "hi"), ("30.05, 03:31", "jhjh"),
            ("30.05, 07:32", "xcvbnm"), ("30.05, 09:20", "nn")]
    for tm, txt in msgs:
        # компактный bubble: используем msg_bubble_them с подменой meta-time
        els, dh = msg_bubble_them(0, cur_y, ARTBOARD_W, txt)
        # last text element в els это body, второй — meta. меняем meta-text.
        for e in els:
            if e.attrs.get("text", "").startswith("Отель ·"):
                e.attrs["text"] = f"Вы · {tm}"  # на стороне партнёра «them» = клиент
        children.extend(els)
        cur_y += dh + 6

    # composer (на partner-screen — disabled если read-only)
    composer_y = ARTBOARD_H - 56 - 56  # навигация + composer
    els, _ = composer(0, composer_y, ARTBOARD_W, placeholder="Сообщение…")
    # если read-only — тонируем фоновый Rect textarea muted'ом
    if not can_write:
        for e in els:
            if e.type == "rect" and e.attrs.get("fill") == COLORS["surface"]:
                e.attrs["fill"] = COLORS["surface_soft"]
    children.extend(els)

    # bottom nav (партнёр, active=Клиенты)
    nav_y = ARTBOARD_H - 56
    els, _ = bottom_nav(0, nav_y, ARTBOARD_W, _PARTNER_NAV, active_idx=3)
    children.extend(els)

    return Frame(
        id=frame_id, external_ref=external_ref,
        x=x, y=y, w=ARTBOARD_W, h=ARTBOARD_H,
        attrs={"title": "partner/client_edit_chat", "fill": COLORS["bg"]},
        children=children,
    )


# Registry: screen_name → builder. CLI использует.
SCREENS = {
    "chat_thread": chat_thread,
    "partner_clients_list": partner_clients_list,
    "partner_client_edit_chat": partner_client_edit_chat,
}

# Default-позиции на доске (для horizontal layout рядом друг с другом).
# При render frame'у передаётся (x, y) — координаты child'ов внутри frame'а
# остаются относительными к frame, board сам их сместит при рендере.
SCREEN_POSITIONS: dict[str, tuple[float, float]] = {
    "chat_thread": (0, 0),
    "partner_clients_list": (ARTBOARD_W + 30, 0),
    "partner_client_edit_chat": (2 * (ARTBOARD_W + 30), 0),
}
