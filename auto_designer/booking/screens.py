"""Full-screen фреймы booking.

Каждая функция возвращает Frame с вложенными child-элементами.
external_ref + id фрейма берётся из refs.json (где живёт persistent mapping
screen_name → {frame_id, external_ref}).
"""
from __future__ import annotations

from uuid import UUID

from auto_designer.booking.components import (
    banner_warn,
    composer,
    msg_bubble_me,
    msg_bubble_them,
    subject_card,
    topbar,
)
from auto_designer.booking.constants import ARTBOARD_H, ARTBOARD_W, COLORS
from auto_designer.core.primitives import Element, Frame, Rect


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


# Registry: screen_name → builder. CLI использует.
SCREENS = {
    "chat_thread": chat_thread,
}
