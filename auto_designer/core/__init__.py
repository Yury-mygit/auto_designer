"""Core lib: примитивы (SVG-shapes), клиент board API, layout helpers."""
from auto_designer.core.primitives import Element, Frame, Group, Image, Rect, Text
from auto_designer.core.board_client import BoardClient

__all__ = ["Element", "Frame", "Group", "Image", "Rect", "Text", "BoardClient"]
