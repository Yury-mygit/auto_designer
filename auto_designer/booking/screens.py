"""Full-screen фреймы booking.

Каждая функция принимает `frame_id, external_ref, x, y` и возвращает
Frame с вложенными child-элементами.

ВАЖНО про координаты: все child-элементы имеют **абсолютные** координаты
(не относительные к frame). Board считает relX = child.x - frame.x при
render'е, так что мы должны передавать `x + offset_inside_frame` каждому
компоненту. Если забыть и передать просто `0` — relX уйдёт в минус и
content вылезет за края frame.
"""
from __future__ import annotations

from uuid import UUID, uuid4

from auto_designer.booking.components import (
    banner_readonly,
    banner_warn,
    booking_card,
    bottom_nav,
    chat_icon_btn,
    client_card,
    composer,
    form_field,
    hotel_head,
    hotel_list_card,
    hotel_tabs,
    msg_bubble_me,
    msg_bubble_them,
    pay_method,
    primary_button,
    role_card,
    room_card,
    subject_card,
    subtitle_bar,
    tabs,
    topbar,
)
from auto_designer.booking.constants import ARTBOARD_H, ARTBOARD_W, COLORS, FONT
from auto_designer.core.primitives import Element, Frame, Rect, Text


_PARTNER_NAV = ["Отели", "Комнаты", "Брони", "Клиенты", "Персонал"]
_CLIENT_NAV = ["Отель", "Комнаты", "Услуги", "Брони", "Отели"]


def _bg(x: float, y: float) -> Rect:
    """Фон artboard'а — заполняет всю площадь frame'а."""
    return Rect(
        id=uuid4(), x=x, y=y, w=ARTBOARD_W, h=ARTBOARD_H,
        attrs={"fill": COLORS["bg"], "rx": 0},
    )


def chat_thread(
    frame_id: UUID, external_ref: UUID, x: float = 0, y: float = 0,
    bot_blocked: bool = False,
) -> Frame:
    """client/views/chat/thread — лента сообщений + composer."""
    children: list[Element] = [_bg(x, y)]
    cur_y: float = y

    children.extend(topbar(x, cur_y, ARTBOARD_W, "Отель Ала-Тоо Бутик-Стэй"))
    cur_y += 56

    if bot_blocked:
        els, dh = banner_warn(
            x, cur_y, ARTBOARD_W,
            "Нажмите Start у @rforge_stay_bot, чтобы получать уведомления.",
        )
        children.extend(els)
        cur_y += dh

    els, dh = subject_card(x, cur_y, ARTBOARD_W, "Бронь BK-2026-001", "12—15 июня · номер 12")
    children.extend(els)
    cur_y += dh

    cur_y += 8
    els, dh = msg_bubble_them(x, cur_y, ARTBOARD_W, "Здравствуйте! Во сколько заезд?")
    children.extend(els)
    cur_y += dh + 8
    els, dh = msg_bubble_me(x, cur_y, ARTBOARD_W, "В 14:00.")
    children.extend(els)
    cur_y += dh + 8
    els, dh = msg_bubble_them(x, cur_y, ARTBOARD_W, "Спасибо! Можно с собакой?")
    children.extend(els)
    cur_y += dh + 8

    composer_y = y + ARTBOARD_H - 56
    els, _ = composer(x, composer_y, ARTBOARD_W)
    children.extend(els)

    return Frame(
        id=frame_id, external_ref=external_ref,
        x=x, y=y, w=ARTBOARD_W, h=ARTBOARD_H,
        attrs={"title": "client/chat/thread", "fill": COLORS["bg"], "rx": 0},
        children=children,
    )


def partner_clients_list(
    frame_id: UUID, external_ref: UUID, x: float = 0, y: float = 0,
) -> Frame:
    """partner/views/clients_list — вкладка «Клиенты»."""
    children: list[Element] = [_bg(x, y)]
    cur_y: float = y

    children.extend(topbar(x, cur_y, ARTBOARD_W, "rforge_booking_bot"))
    cur_y += 56

    els, dh = subtitle_bar(x, cur_y, ARTBOARD_W, "Клиенты")
    children.extend(els)
    cur_y += dh

    sample = [
        ("Yury", "Бронирований: 10 · Последняя: 2026-05-28", False),
        ("Зохид", "Бронирований: 3 · Последняя: 2026-05-22", True),
        ("Иван Петров", "996555123456 · Бронирований: 2", False),
        ("TestClient", "Бронирований: 1 · Последняя: 2026-06-01", False),
    ]
    cur_y += 4
    for name, info, unread in sample:
        els, dh = client_card(x, cur_y, ARTBOARD_W, name, info, unread=unread)
        children.extend(els)
        cur_y += dh + 4

    nav_y = y + ARTBOARD_H - 56
    els, _ = bottom_nav(x, nav_y, ARTBOARD_W, _PARTNER_NAV, active_idx=3)
    children.extend(els)

    return Frame(
        id=frame_id, external_ref=external_ref,
        x=x, y=y, w=ARTBOARD_W, h=ARTBOARD_H,
        attrs={"title": "partner/clients_list", "fill": COLORS["bg"], "rx": 0},
        children=children,
    )


def partner_client_edit_chat(
    frame_id: UUID, external_ref: UUID, x: float = 0, y: float = 0,
    can_write: bool = False,
) -> Frame:
    """partner/views/client_edit_chat — карточка клиента с inline-чатом.

    can_write=False → readonly banner + disabled composer.
    """
    children: list[Element] = [_bg(x, y)]
    cur_y: float = y

    children.extend(topbar(x, cur_y, ARTBOARD_W, "rforge_booking_bot"))
    cur_y += 56

    els, dh = subtitle_bar(x, cur_y, ARTBOARD_W, "Клиент / Карточка клиента")
    children.extend(els)
    cur_y += dh

    # client info card (сжато)
    cur_y += 6
    children.append(Rect(
        id=uuid4(), x=x + 8, y=cur_y, w=ARTBOARD_W - 16, h=56,
        attrs={"fill": COLORS["surface"], "stroke": COLORS["border"], "strokeWidth": 1, "rx": 8},
    ))
    children.append(Text(
        id=uuid4(), x=x + 20, y=cur_y + 10, w=ARTBOARD_W - 40, h=16,
        attrs={"text": "2026-05-19 → 2026-05-21 (1 гостей)",
               "fontSize": FONT["size_sm"], "color": COLORS["muted"]},
    ))
    children.append(Text(
        id=uuid4(), x=x + 20, y=cur_y + 30, w=ARTBOARD_W - 40, h=16,
        attrs={"text": "6000 сом", "fontSize": FONT["size_md"],
               "color": COLORS["text"], "bold": True},
    ))
    cur_y += 70

    # «Чат с отелем» heading
    children.append(Text(
        id=uuid4(), x=x + 14, y=cur_y, w=ARTBOARD_W - 28, h=20,
        attrs={"text": "Чат с отелем", "fontSize": FONT["size_lg"],
               "color": COLORS["text"], "bold": True},
    ))
    cur_y += 28

    els, dh = tabs(x, cur_y, ARTBOARD_W, ["Ала-Тоо Бутик-Стэй", "Манас Гарден Отель"], active_idx=0)
    children.extend(els)
    cur_y += dh

    if not can_write:
        els, dh = banner_readonly(
            x, cur_y, ARTBOARD_W,
            "Только просмотр. У вас нет прав (chat_with_clients).",
        )
        children.extend(els)
        cur_y += dh

    # пара сообщений клиента (на стороне партнёра это them — слева)
    cur_y += 6
    msgs = [("hi", "03:25"), ("jhjh", "03:31"), ("xcvbnm", "07:32"), ("nn", "09:20")]
    for txt, tm in msgs:
        els, dh = msg_bubble_them(x, cur_y, ARTBOARD_W, txt)
        # на стороне партнёра «them» = клиент. Подменяем meta-label «Отель» → «Клиент».
        for e in els:
            if e.attrs.get("text", "").startswith("Отель · "):
                e.attrs["text"] = f"Клиент · {tm}"
        children.extend(els)
        cur_y += dh + 4

    # composer (disabled если read-only)
    composer_y = y + ARTBOARD_H - 56 - 56  # bottom-nav + composer
    els, _ = composer(x, composer_y, ARTBOARD_W)
    if not can_write:
        for e in els:
            if e.type == "rect" and e.attrs.get("fill") == COLORS["surface"]:
                e.attrs["fill"] = COLORS["surface_soft"]
    children.extend(els)

    nav_y = y + ARTBOARD_H - 56
    els, _ = bottom_nav(x, nav_y, ARTBOARD_W, _PARTNER_NAV, active_idx=3)
    children.extend(els)

    return Frame(
        id=frame_id, external_ref=external_ref,
        x=x, y=y, w=ARTBOARD_W, h=ARTBOARD_H,
        attrs={"title": "partner/client_edit_chat", "fill": COLORS["bg"], "rx": 0},
        children=children,
    )


def client_hotel_detail(
    frame_id: UUID, external_ref: UUID, x: float = 0, y: float = 0,
) -> Frame:
    """client/views/hotel/detail — view отеля, tab «Отель»."""
    children: list[Element] = [_bg(x, y)]
    cur_y = y

    children.extend(topbar(x, cur_y, ARTBOARD_W, "Отель Ала-Тоо Бутик-Стэй"))
    cur_y += 56

    els, dh = hotel_head(
        x, cur_y, ARTBOARD_W,
        name="Ала-Тоо Бутик-Стэй",
        address="Бишкек, ул. Жибек-Жолу 100",
    )
    children.extend(els)
    cur_y += dh

    els, dh = hotel_tabs(x, cur_y, ARTBOARD_W, active="Отель")
    children.extend(els)
    cur_y += dh

    # description
    cur_y += 12
    children.append(Text(
        id=uuid4(), x=x + 14, y=cur_y, w=ARTBOARD_W - 28, h=20,
        attrs={"text": "Описание", "fontSize": FONT["size_md"],
               "color": COLORS["text"], "bold": True},
    ))
    cur_y += 24
    # длинный текст разбиваем построчно (board без word-wrap)
    desc_lines = [
        "Уютный бутик-отель в центре Бишкека.",
        "5 номеров с авторским дизайном.",
        "Завтрак включён, парковка рядом.",
    ]
    for line in desc_lines:
        children.append(Text(
            id=uuid4(), x=x + 14, y=cur_y, w=ARTBOARD_W - 28, h=18,
            attrs={"text": line, "fontSize": FONT["size_sm"], "color": COLORS["muted"]},
        ))
        cur_y += 20

    nav_y = y + ARTBOARD_H - 56
    els, _ = bottom_nav(x, nav_y, ARTBOARD_W, _CLIENT_NAV, active_idx=0)
    children.extend(els)

    return Frame(
        id=frame_id, external_ref=external_ref,
        x=x, y=y, w=ARTBOARD_W, h=ARTBOARD_H,
        attrs={"title": "client/hotel/detail", "fill": COLORS["bg"], "rx": 0},
        children=children,
    )


def client_hotel_rooms(
    frame_id: UUID, external_ref: UUID, x: float = 0, y: float = 0,
) -> Frame:
    """client/views/hotel/rooms — список комнат."""
    children: list[Element] = [_bg(x, y)]
    cur_y = y

    children.extend(topbar(x, cur_y, ARTBOARD_W, "Отель Ала-Тоо Бутик-Стэй"))
    cur_y += 56

    els, dh = hotel_tabs(x, cur_y, ARTBOARD_W, active="Комнаты")
    children.extend(els)
    cur_y += dh

    # дата-фильтр placeholder
    cur_y += 8
    children.append(Rect(
        id=uuid4(), x=x + 8, y=cur_y, w=ARTBOARD_W - 16, h=36,
        attrs={"fill": COLORS["surface"], "stroke": COLORS["border_soft"], "strokeWidth": 1, "rx": 6},
    ))
    children.append(Text(
        id=uuid4(), x=x + 20, y=cur_y + 10, w=ARTBOARD_W - 40, h=18,
        attrs={"text": "🗓  12 июня → 15 июня · 1 гость",
               "fontSize": FONT["size_sm"], "color": COLORS["text"]},
    ))
    cur_y += 44

    rooms = [
        ("Стандарт двухместный", "Вместимость: 2 · 1 кровать · 2 этаж", "3000 сом/ночь", True),
        ("Люкс с балконом", "Вместимость: 3 · 2 кровати · 3 этаж", "5500 сом/ночь", True),
        ("Эконом одноместный", "Вместимость: 1 · 1 кровать · 1 этаж", "1800 сом/ночь", False),
    ]
    for name, meta, price, avail in rooms:
        els, dh = room_card(x, cur_y, ARTBOARD_W, name, meta, price, available=avail)
        children.extend(els)
        cur_y += dh + 6

    nav_y = y + ARTBOARD_H - 56
    els, _ = bottom_nav(x, nav_y, ARTBOARD_W, _CLIENT_NAV, active_idx=1)
    children.extend(els)

    return Frame(
        id=frame_id, external_ref=external_ref,
        x=x, y=y, w=ARTBOARD_W, h=ARTBOARD_H,
        attrs={"title": "client/hotel/rooms", "fill": COLORS["bg"], "rx": 0},
        children=children,
    )


def client_bookings(
    frame_id: UUID, external_ref: UUID, x: float = 0, y: float = 0,
) -> Frame:
    """client/views/bookings — мои брони."""
    children: list[Element] = [_bg(x, y)]
    cur_y = y

    children.extend(topbar(x, cur_y, ARTBOARD_W, "Мои бронирования"))
    cur_y += 56

    cur_y += 8
    bookings = [
        ("BK-2026-001", "Ала-Тоо Бутик-Стэй", "12 — 15 июня · 1 гость", "9000 сом", "Ожидает оплаты"),
        ("BK-2026-002", "Манас Гарден Отель", "20 — 22 июня · 2 гостя", "11000 сом", "Подтверждено"),
        ("WRN9XXKY", "Ала-Тоо Бутик-Стэй", "2026-05-19 → 2026-05-21 (1)", "6000 сом", "Завершено"),
    ]
    for code, hotel, dates, price, status in bookings:
        els, dh = booking_card(x, cur_y, ARTBOARD_W, code, hotel, dates, price, status)
        children.extend(els)
        cur_y += dh + 8

    nav_y = y + ARTBOARD_H - 56
    els, _ = bottom_nav(x, nav_y, ARTBOARD_W, _CLIENT_NAV, active_idx=3)
    children.extend(els)

    return Frame(
        id=frame_id, external_ref=external_ref,
        x=x, y=y, w=ARTBOARD_W, h=ARTBOARD_H,
        attrs={"title": "client/bookings", "fill": COLORS["bg"], "rx": 0},
        children=children,
    )


def entry(frame_id: UUID, external_ref: UUID, x: float = 0, y: float = 0) -> Frame:
    """entry — выбор роли (multi-role hub после login)."""
    children: list[Element] = [_bg(x, y)]
    cur_y = y

    children.extend(topbar(x, cur_y, ARTBOARD_W, "RForge Stay"))
    cur_y += 56

    cur_y += 16
    children.append(Text(
        id=uuid4(), x=x + 16, y=cur_y, w=ARTBOARD_W - 32, h=24,
        attrs={"text": "Выберите режим", "fontSize": FONT["size_xl"],
               "color": COLORS["text"], "bold": True},
    ))
    cur_y += 8
    children.append(Text(
        id=uuid4(), x=x + 16, y=cur_y + 28, w=ARTBOARD_W - 32, h=18,
        attrs={"text": "У вас несколько ролей. Откройте нужную.",
               "fontSize": FONT["size_sm"], "color": COLORS["muted"]},
    ))
    cur_y += 60

    roles = [
        ("Клиент", "Поиск отелей и мои бронирования", "lucide:user-round"),
        ("Партнёр", "Управление моими отелями", "lucide:briefcase"),
        ("Администратор", "Все отели и пользователи", "lucide:shield"),
    ]
    for label, desc, icon in roles:
        els, dh = role_card(x, cur_y, ARTBOARD_W, label, desc, icon)
        children.extend(els)
        cur_y += dh + 10

    return Frame(
        id=frame_id, external_ref=external_ref,
        x=x, y=y, w=ARTBOARD_W, h=ARTBOARD_H,
        attrs={"title": "entry", "fill": COLORS["bg"], "rx": 0},
        children=children,
    )


def client_hotels(frame_id: UUID, external_ref: UUID, x: float = 0, y: float = 0) -> Frame:
    """client/hotels — список всех отелей (главная клиента)."""
    children: list[Element] = [_bg(x, y)]
    cur_y = y

    children.extend(topbar(x, cur_y, ARTBOARD_W, "Отели"))
    cur_y += 56

    cur_y += 8
    hotels = [
        ("Ала-Тоо Бутик-Стэй", "Бишкек, центр", "5 номеров · от 1800 сом"),
        ("Манас Гарден Отель", "Бишкек, Чуй", "12 номеров · от 2500 сом"),
        ("Иссык-Куль Резорт", "Чолпон-Ата", "30 номеров · от 4000 сом"),
        ("Алтын-Арашан Лодж", "Каракол", "8 номеров · от 3200 сом"),
    ]
    for name, city, meta in hotels:
        els, dh = hotel_list_card(x, cur_y, ARTBOARD_W, name, city, meta)
        children.extend(els)
        cur_y += dh + 4

    nav_y = y + ARTBOARD_H - 56
    els, _ = bottom_nav(x, nav_y, ARTBOARD_W, _CLIENT_NAV, active_idx=4)
    children.extend(els)

    return Frame(
        id=frame_id, external_ref=external_ref,
        x=x, y=y, w=ARTBOARD_W, h=ARTBOARD_H,
        attrs={"title": "client/hotels", "fill": COLORS["bg"], "rx": 0},
        children=children,
    )


def client_hotel_book(frame_id: UUID, external_ref: UUID, x: float = 0, y: float = 0) -> Frame:
    """client/hotel/book — форма подтверждения бронирования."""
    children: list[Element] = [_bg(x, y)]
    cur_y = y

    children.extend(topbar(x, cur_y, ARTBOARD_W, "Бронирование"))
    cur_y += 56

    # room summary card
    cur_y += 8
    children.append(Rect(
        id=uuid4(), x=x + 8, y=cur_y, w=ARTBOARD_W - 16, h=66,
        attrs={"fill": COLORS["surface"], "stroke": COLORS["border"], "strokeWidth": 1, "rx": 8},
    ))
    children.append(Text(
        id=uuid4(), x=x + 20, y=cur_y + 12, w=ARTBOARD_W - 40, h=20,
        attrs={"text": "Стандарт двухместный", "fontSize": FONT["size_md"],
               "color": COLORS["text"], "bold": True},
    ))
    children.append(Text(
        id=uuid4(), x=x + 20, y=cur_y + 36, w=ARTBOARD_W - 40, h=18,
        attrs={"text": "Ала-Тоо Бутик-Стэй · 3000 сом/ночь",
               "fontSize": FONT["size_sm"], "color": COLORS["muted"]},
    ))
    cur_y += 78

    # form fields
    els, dh = form_field(x, cur_y, ARTBOARD_W, "Заезд", "12 июня 2026")
    children.extend(els)
    cur_y += dh
    els, dh = form_field(x, cur_y, ARTBOARD_W, "Выезд", "15 июня 2026")
    children.extend(els)
    cur_y += dh
    els, dh = form_field(x, cur_y, ARTBOARD_W, "Гости", "1 гость")
    children.extend(els)
    cur_y += dh
    els, dh = form_field(x, cur_y, ARTBOARD_W, "Пожелания", "Можно с собакой", multiline=True)
    children.extend(els)
    cur_y += dh + 8

    # total
    children.append(Rect(
        id=uuid4(), x=x + 12, y=cur_y, w=ARTBOARD_W - 24, h=44,
        attrs={"fill": COLORS["surface_soft"], "stroke": COLORS["border"], "strokeWidth": 1, "rx": 8},
    ))
    children.append(Text(
        id=uuid4(), x=x + 24, y=cur_y + 14, w=ARTBOARD_W / 2, h=20,
        attrs={"text": "Итого", "fontSize": FONT["size_md"], "color": COLORS["text"]},
    ))
    children.append(Text(
        id=uuid4(), x=x + ARTBOARD_W - 130, y=cur_y + 14, w=110, h=20,
        attrs={"text": "9 000 сом", "fontSize": FONT["size_lg"],
               "color": COLORS["text"], "bold": True},
    ))

    # primary button прижат к низу
    btn_y = y + ARTBOARD_H - 64
    els, _ = primary_button(x, btn_y, ARTBOARD_W, "Подтвердить бронь")
    children.extend(els)

    return Frame(
        id=frame_id, external_ref=external_ref,
        x=x, y=y, w=ARTBOARD_W, h=ARTBOARD_H,
        attrs={"title": "client/hotel/book", "fill": COLORS["bg"], "rx": 0},
        children=children,
    )


def client_pay(frame_id: UUID, external_ref: UUID, x: float = 0, y: float = 0) -> Frame:
    """client/pay — экран оплаты."""
    children: list[Element] = [_bg(x, y)]
    cur_y = y

    children.extend(topbar(x, cur_y, ARTBOARD_W, "Оплата"))
    cur_y += 56

    # summary
    cur_y += 12
    children.append(Rect(
        id=uuid4(), x=x + 8, y=cur_y, w=ARTBOARD_W - 16, h=80,
        attrs={"fill": COLORS["surface"], "stroke": COLORS["border"], "strokeWidth": 1, "rx": 8},
    ))
    children.append(Text(
        id=uuid4(), x=x + 20, y=cur_y + 12, w=ARTBOARD_W - 40, h=18,
        attrs={"text": "Код брони: BK-2026-001", "fontSize": FONT["size_sm"], "color": COLORS["muted"]},
    ))
    children.append(Text(
        id=uuid4(), x=x + 20, y=cur_y + 32, w=ARTBOARD_W - 40, h=20,
        attrs={"text": "Ала-Тоо Бутик-Стэй · 3 ночи", "fontSize": FONT["size_md"],
               "color": COLORS["text"], "bold": True},
    ))
    children.append(Text(
        id=uuid4(), x=x + ARTBOARD_W - 140, y=cur_y + 56, w=120, h=20,
        attrs={"text": "9 000 сом", "fontSize": FONT["size_lg"],
               "color": COLORS["accent"], "bold": True},
    ))
    cur_y += 92

    # methods heading
    children.append(Text(
        id=uuid4(), x=x + 14, y=cur_y, w=ARTBOARD_W - 28, h=20,
        attrs={"text": "Способ оплаты", "fontSize": FONT["size_md"],
               "color": COLORS["text"], "bold": True},
    ))
    cur_y += 26

    methods = [
        ("MBANK", "M·B", True),
        ("Optima", "OPT", False),
        ("Bakai", "BAI", False),
        ("Карта Visa / Mastercard", "VISA", False),
    ]
    for name, logo, sel in methods:
        els, dh = pay_method(x, cur_y, ARTBOARD_W, name, logo, selected=sel)
        children.extend(els)
        cur_y += dh + 4

    # primary button прижат к низу
    btn_y = y + ARTBOARD_H - 64
    els, _ = primary_button(x, btn_y, ARTBOARD_W, "Оплатить 9 000 сом")
    children.extend(els)

    return Frame(
        id=frame_id, external_ref=external_ref,
        x=x, y=y, w=ARTBOARD_W, h=ARTBOARD_H,
        attrs={"title": "client/pay", "fill": COLORS["bg"], "rx": 0},
        children=children,
    )


def partner_hotels_list(frame_id: UUID, external_ref: UUID, x: float = 0, y: float = 0) -> Frame:
    """partner/hotels_list — мои отели (партнёр)."""
    children: list[Element] = [_bg(x, y)]
    cur_y = y

    children.extend(topbar(x, cur_y, ARTBOARD_W, "rforge_booking_bot"))
    cur_y += 56

    els, dh = subtitle_bar(x, cur_y, ARTBOARD_W, "Мои отели")
    children.extend(els)
    cur_y += dh

    cur_y += 4
    hotels = [
        ("Ала-Тоо Бутик-Стэй", "Бишкек, ул. Жибек-Жолу 100", "5 номеров · опубликовано"),
        ("Манас Гарден Отель", "Бишкек, Чуй 200", "12 номеров · опубликовано"),
        ("Озеро Делюкс", "Чолпон-Ата", "3 номера · черновик"),
    ]
    for name, city, meta in hotels:
        els, dh = hotel_list_card(x, cur_y, ARTBOARD_W, name, city, meta)
        children.extend(els)
        cur_y += dh + 4

    # «+» добавить отель — кнопка plus floating
    cur_y += 12
    els, _ = primary_button(x, cur_y, ARTBOARD_W, "+ Добавить отель")
    children.extend(els)

    nav_y = y + ARTBOARD_H - 56
    els, _ = bottom_nav(x, nav_y, ARTBOARD_W, _PARTNER_NAV, active_idx=0)
    children.extend(els)

    return Frame(
        id=frame_id, external_ref=external_ref,
        x=x, y=y, w=ARTBOARD_W, h=ARTBOARD_H,
        attrs={"title": "partner/hotels_list", "fill": COLORS["bg"], "rx": 0},
        children=children,
    )


SCREENS = {
    "chat_thread": chat_thread,
    "partner_clients_list": partner_clients_list,
    "partner_client_edit_chat": partner_client_edit_chat,
    "client_hotel_detail": client_hotel_detail,
    "client_hotel_rooms": client_hotel_rooms,
    "client_bookings": client_bookings,
    "entry": entry,
    "client_hotels": client_hotels,
    "client_hotel_book": client_hotel_book,
    "client_pay": client_pay,
    "partner_hotels_list": partner_hotels_list,
}

# 3×N grid layout.
_ROW_GAP = 60
_R1 = 0
_R2 = ARTBOARD_H + _ROW_GAP
_R3 = 2 * (ARTBOARD_H + _ROW_GAP)
_C1 = 0
_C2 = ARTBOARD_W + 30
_C3 = 2 * (ARTBOARD_W + 30)

SCREEN_POSITIONS: dict[str, tuple[float, float]] = {
    "chat_thread": (_C1, _R1),
    "partner_clients_list": (_C2, _R1),
    "partner_client_edit_chat": (_C3, _R1),
    "client_hotel_detail": (_C1, _R2),
    "client_hotel_rooms": (_C2, _R2),
    "client_bookings": (_C3, _R2),
    "entry": (_C1, _R3),
    "client_hotels": (_C2, _R3),
    "client_hotel_book": (_C3, _R3),
    "client_pay": (_C1, _R3 + ARTBOARD_H + _ROW_GAP),
    "partner_hotels_list": (_C2, _R3 + ARTBOARD_H + _ROW_GAP),
}
