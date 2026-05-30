"""Палитра, шрифты, размеры booking — копия `:root` из
`rf-booking-frontend/src/styles/base.css`. Синхронизировать вручную
при правках на фронте.
"""

# Цвета (light theme, как в base.css :root)
COLORS = {
    "bg": "#f5f5f5",
    "surface": "#ffffff",
    "surface_soft": "#fafafa",
    "text": "#222222",
    "muted": "#666666",
    "text_muted": "#666666",
    "text_faint": "#888888",
    "border": "#dddddd",
    "border_soft": "#eeeeee",
    "accent": "#1a73e8",
    "accent_text": "#ffffff",
    "success": "#2e7d32",
    "danger": "#d32f2f",
    "warn_bg": "#fff4d6",
    "warn_text": "#6a4a00",
    "warn_border": "#f0c060",
}

# Размеры
DIM = {
    "topbar_h": 56,
    "bottomnav_h": 60,
    "card_radius": 8,
    "btn_radius": 4,
    "input_radius": 6,
    "msg_radius": 12,
}

# Шрифты
FONT = {
    "family": "-apple-system, 'Segoe UI', Roboto, sans-serif",
    "size_xs": 11,
    "size_sm": 12,
    "size_md": 14,
    "size_lg": 18,
    "size_xl": 24,
}

# Размер artboard для mobile-mockup screen'ов (примерно iPhone 14 viewport)
ARTBOARD_W = 390
ARTBOARD_H = 800
