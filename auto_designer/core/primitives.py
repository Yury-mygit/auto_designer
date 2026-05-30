"""Примитивы board: Rect / Text / Image / Group / Frame.

Каждый имеет:
  - .external_ref (UUID или None) — стабильный design-id для upsert.
  - .id (UUID) — internal board element id (генерируется один раз и хранится
    рядом с external_ref в refs.json).
  - .to_payload() → dict — формат для board API
    (POST /boards/{board_id}/elements/by-ref).

Group / Frame — контейнеры, имеют `children` (список Element). При сборке
дерева board parent_id у потомков выставляется на frame_id, а Group просто
группирует элементы для удобства композиции (board не имеет «group» типа,
но мы можем вкладывать всё в один frame с расчётом x/y).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass
class Element:
    """Базовый класс. Конкретные подклассы добавляют свои attrs."""
    id: UUID
    type: str
    x: float = 0.0
    y: float = 0.0
    w: float = 0.0
    h: float = 0.0
    attrs: dict[str, Any] = field(default_factory=dict)
    external_ref: UUID | None = None
    parent_id: UUID | None = None

    def to_payload(self, board_now_ms: int) -> dict[str, Any]:
        """Возвращает body для POST /elements/by-ref."""
        if self.external_ref is None:
            raise ValueError("Element.external_ref is required for upsert-by-ref")
        return {
            "externalRef": str(self.external_ref),
            "id": str(self.id),
            "type": self.type,
            "parentId": str(self.parent_id) if self.parent_id else None,
            "x": self.x,
            "y": self.y,
            "w": self.w,
            "h": self.h,
            "attrs": self.attrs,
            "createdAt": board_now_ms,
            "updatedAt": board_now_ms,
        }


@dataclass
class Rect(Element):
    """Прямоугольник. attrs: fill, stroke, strokeWidth, radius."""
    type: str = "rect"


@dataclass
class Text(Element):
    """Текст. attrs: text, fontSize, fontFamily, color, fontWeight, textAlign."""
    type: str = "text"


@dataclass
class Image(Element):
    """Картинка по URL. attrs: src."""
    type: str = "image"


@dataclass
class Group:
    """Логическая группа (не отдельный board-тип). Используется в композиции:
    компоненты собирают Group из Rect/Text/Image, потом screens вкладывают
    Group в Frame и расставляют offset'ы.
    """
    children: list[Element | "Group"] = field(default_factory=list)
    offset_x: float = 0.0
    offset_y: float = 0.0

    def flatten(self, dx: float = 0.0, dy: float = 0.0) -> list[Element]:
        """Разворачивает дерево групп в плоский список Element'ов с
        накопленным offset'ом."""
        out: list[Element] = []
        for c in self.children:
            if isinstance(c, Group):
                out.extend(c.flatten(dx + self.offset_x, dy + self.offset_y))
            else:
                # копия с применённым offset'ом
                el = Element(
                    id=c.id,
                    type=c.type,
                    x=c.x + dx + self.offset_x,
                    y=c.y + dy + self.offset_y,
                    w=c.w,
                    h=c.h,
                    attrs=dict(c.attrs),
                    external_ref=c.external_ref,
                    parent_id=c.parent_id,
                )
                out.append(el)
        return out


@dataclass
class Frame(Element):
    """Frame на доске board. Контейнер для child-элементов.

    children — Group или Element; при render'е flatten'ятся, parent_id
    выставляется = self.id, координаты child'ов остаются как заданы
    (board координирует child'ов относительно parent frame).
    """
    type: str = "frame"
    children: list[Element | Group] = field(default_factory=list)

    def flat_children(self) -> list[Element]:
        out: list[Element] = []
        for c in self.children:
            if isinstance(c, Group):
                out.extend(c.flatten())
            else:
                out.append(c)
        for el in out:
            el.parent_id = self.id
        return out
