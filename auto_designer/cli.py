"""CLI: `auto-design <command>`.

Команды:
  - render <project> <screen>       — пересоздать (upsert) один screen
  - render <project> --all          — все screens
  - list <project>                  — доступные screens + статус (есть ли ref'ы)
  - refs <project>                  — refs.json + PNG-URL фреймов

Конфиг через env:
  - BOARD_API_URL   (def: https://board.dev.raftforge.art/api/v1)
  - BOARD_API_TOKEN (required)
  - BOARD_ID_<PROJECT_UPPER>  — board UUID для project, например
    BOARD_ID_BOOKING=49df558a-edf7-4c0a-a84a-1c905a0bc83d
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from uuid import UUID, uuid4, uuid5

import click

from auto_designer.booking import screens as booking_screens
from auto_designer.core import BoardClient
from auto_designer.core.primitives import Frame


PROJECT_SCREENS = {
    "booking": booking_screens.SCREENS,
}


def _refs_path(project: str) -> Path:
    return Path(__file__).parent / project / "refs.json"


def _load_refs(project: str) -> dict[str, dict[str, str]]:
    p = _refs_path(project)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_refs(project: str, refs: dict[str, dict[str, str]]) -> None:
    _refs_path(project).write_text(json.dumps(refs, indent=2, ensure_ascii=False) + "\n")


def _board_id(project: str) -> UUID:
    env = f"BOARD_ID_{project.upper()}"
    val = os.environ.get(env)
    if not val:
        raise click.ClickException(f"Env {env} не задан (UUID доски для проекта {project})")
    return UUID(val)


def _ensure_refs(project: str, screen: str, refs: dict) -> tuple[UUID, UUID]:
    """Возвращает (frame_id, external_ref). Генерит если впервые."""
    entry = refs.get(screen)
    if entry is None:
        frame_id = uuid4()
        external_ref = uuid4()
        refs[screen] = {"frame_id": str(frame_id), "external_ref": str(external_ref)}
        return frame_id, external_ref
    return UUID(entry["frame_id"]), UUID(entry["external_ref"])


@click.group()
def cli() -> None:
    """auto-design: рисуем макеты на board (https://board.dev.raftforge.art)."""


@cli.command("list")
@click.argument("project")
def cmd_list(project: str) -> None:
    """Список доступных screens у проекта + есть ли уже ref'ы."""
    if project not in PROJECT_SCREENS:
        raise click.ClickException(f"Unknown project: {project}. Known: {list(PROJECT_SCREENS)}")
    refs = _load_refs(project)
    for name in PROJECT_SCREENS[project]:
        marker = "●" if name in refs else "○"
        click.echo(f"  {marker} {name}")


@cli.command("refs")
@click.argument("project")
def cmd_refs(project: str) -> None:
    """Показать refs.json + PNG-URL фреймов."""
    if project not in PROJECT_SCREENS:
        raise click.ClickException(f"Unknown project: {project}")
    refs = _load_refs(project)
    base = os.environ.get("BOARD_API_URL", "https://board.dev.raftforge.art/api/v1").rstrip("/")
    for name, entry in refs.items():
        click.echo(f"{name}:")
        click.echo(f"  external_ref: {entry['external_ref']}")
        click.echo(f"  frame_id:     {entry['frame_id']}")
        click.echo(f"  png:          {base}/frames/{entry['frame_id']}.png")


@cli.command("render")
@click.argument("project")
@click.argument("screen", required=False)
@click.option("--all", "render_all", is_flag=True, help="Render all screens.")
def cmd_render(project: str, screen: str | None, render_all: bool) -> None:
    """Render (upsert) screen(s) на доску проекта."""
    if project not in PROJECT_SCREENS:
        raise click.ClickException(f"Unknown project: {project}")
    if not render_all and not screen:
        raise click.ClickException("Specify <screen> or --all")
    targets = list(PROJECT_SCREENS[project]) if render_all else [screen]
    bad = [t for t in targets if t not in PROJECT_SCREENS[project]]
    if bad:
        raise click.ClickException(f"Unknown screens: {bad}")

    refs = _load_refs(project)
    board_id = _board_id(project)
    # Layout dictionary: project-specific screens могут декларировать
    # дефолтные позиции (см. booking/screens.SCREEN_POSITIONS).
    layout: dict[str, tuple[float, float]] = {}
    try:
        layout = __import__(
            f"auto_designer.{project}.screens", fromlist=["SCREEN_POSITIONS"]
        ).SCREEN_POSITIONS
    except (AttributeError, ImportError):
        pass

    with BoardClient() as client:
        for name in targets:
            frame_id, external_ref = _ensure_refs(project, name, refs)
            builder = PROJECT_SCREENS[project][name]
            x0, y0 = layout.get(name, (0.0, 0.0))
            frame: Frame = builder(
                frame_id=frame_id, external_ref=external_ref, x=x0, y=y0
            )
            now_ms = int(time.time() * 1000)

            # 1) upsert frame
            client.upsert_by_ref(board_id, frame.to_payload(now_ms))

            # 2) upsert children. Каждый получает:
            #   - детерминированный external_ref = uuid5(frame_ref, str(index)).
            #     Тот же индекс → тот же ref на повторных render'ах → upsert
            #     обновляет, не плодит zombies.
            #   - attrs.auto = True. Marker «auto-managed»: sweep удалит этих
            #     при сокращении состава screen'а, ручные правки дизайнера
            #     (без marker'а) останутся неприкосновенными.
            children = frame.flat_children()
            new_refs: set[str] = set()
            for i, child in enumerate(children):
                child.external_ref = uuid5(external_ref, str(i))
                child.attrs = {**child.attrs, "auto": True}
                new_refs.add(str(child.external_ref))
                client.upsert_by_ref(board_id, child.to_payload(now_ms))

            # 3) sweep zombies — auto-managed elements этого frame'а с
            # external_ref'ом, которого больше нет в new set.
            board = client.get_board(board_id)
            sweeped = 0
            for el in board.get("elements", []):
                if el.get("parentId") != str(frame_id):
                    continue
                if not el.get("attrs", {}).get("auto"):
                    continue
                ext = el.get("externalRef")
                if ext and ext not in new_refs:
                    if client.delete_by_ref(board_id, UUID(ext)):
                        sweeped += 1

            tail = f" (sweeped {sweeped})" if sweeped else ""
            click.echo(f"  ✓ {name} → frame {frame_id} ({len(children)} children){tail}")
            _save_refs(project, refs)
        click.echo("Done.")
