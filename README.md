# auto_designer

Python pkg + CLI для рисования макетов на доске
[board](https://board.dev.raftforge.art). Аналог Figma «через код»:

- `core/` — примитивы (Rect/Text/Image/Group/Frame), board client, layout.
- `<project>/` — project-specific компоненты + экраны
  (booking, g4, ...). Стабильные `external_ref` хранятся в
  `<project>/refs.json` (в git).
- `cli.py` — команды `auto-design render/list/refs`.

Не runtime сервис — клиентский tooling. Если будет нужен MCP для LLM —
он живёт на стороне board (см. карту `cards/board/feature/2026-05-30-board-mcp-server.md`).

## Установка (локально)

```bash
cd /root/web/dev/auto_designer
pip install -e .
```

Теперь доступна команда `auto-design`.

## Конфиг (env)

- `BOARD_API_TOKEN` — API key board'а (см. `/root/secrets/secrets.md`).
- `BOARD_API_URL` — `https://board.dev.raftforge.art/api/v1` (default).
- `BOARD_ID_BOOKING` — UUID доски проекта (для booking сейчас
  `49df558a-edf7-4c0a-a84a-1c905a0bc83d`).

## Quick start

```bash
export BOARD_API_TOKEN=...
export BOARD_ID_BOOKING=49df558a-edf7-4c0a-a84a-1c905a0bc83d

auto-design list booking
auto-design render booking chat_thread
auto-design refs booking
```

После `render` PNG лежит на `https://board.dev.raftforge.art/api/v1/frames/<frame_id>.png`
(публичная ссылка, без auth).

## Как добавить screen

1. Описать функцию в `auto_designer/<project>/screens.py`, она должна
   принимать `frame_id: UUID, external_ref: UUID` и возвращать `Frame`.
2. Добавить в `SCREENS` dict.
3. Запустить `auto-design render <project> <screen>` — frame_id и
   external_ref сгенерируются автоматически (первый раз), записаны в
   `refs.json`, далее — стабильные.

## Как добавить компонент

В `<project>/components.py` — функция, принимает `(x, y, w, ...)`,
возвращает `list[Element]` (плоский список без external_ref, координаты
абсолютные относительно frame'а).

## Структура

```
auto_designer/
├── auto_designer/
│   ├── core/
│   │   ├── primitives.py      Rect, Text, Image, Group, Frame
│   │   ├── board_client.py    httpx → board API (upsert/get/delete by ref)
│   │   └── layout.py          vstack / hstack
│   ├── booking/
│   │   ├── constants.py       COLORS, DIM, FONT (синхрон с base.css)
│   │   ├── components.py      topbar, msg_bubble_*, composer, ...
│   │   ├── screens.py         SCREENS = {"chat_thread": ...}
│   │   └── refs.json          { screen → {frame_id, external_ref} }
│   ├── cli.py                 click-based CLI
│   └── __init__.py
├── pyproject.toml
└── README.md
```

## Карты

- Bootstrap pkg: `open_cards/cards/auto_designer/feature/2026-05-30-auto-designer-pkg-bootstrap.md`
- board stable refs (pre-condition): `Agent_C/history/2026-05-30-board-external-ref-stable-id.md`
- booking mockups migration (consumer): `open_cards/cards/booking/refactor/2026-05-30-booking-mockups-external-ref-migration.md`

## Известные ограничения pilot

- При `render` upsert'ятся только сами frame'ы (через `refs.json`);
  child-элементы (rect/text внутри) каждый раз получают новые `external_ref`
  → старые child'ы остаются на доске как «zombies». Полная стратегия
  child-refs — отдельной итерацией.
- Только один проект (`booking`) и один screen (`chat_thread`)
  реализованы в pilot. Остальные screens добавляем по карте #30.
