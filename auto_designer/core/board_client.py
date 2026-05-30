"""HTTP-клиент к board (https://board.dev.raftforge.art).

Минимум для auto_designer: upsert_by_ref / get_by_ref / delete_by_ref на
endpoints из карты `cards/board/feature/2026-05-30-board-external-ref-stable-id.md`.

Auth — Bearer API token. По умолчанию читается из env `BOARD_API_TOKEN`,
URL — `BOARD_API_URL` (fallback `https://board.dev.raftforge.art/api/v1`).
"""
from __future__ import annotations

import os
from typing import Any
from uuid import UUID

import httpx


class BoardAPIError(Exception):
    def __init__(self, status: int, body: dict | str):
        self.status = status
        self.body = body
        super().__init__(f"board API {status}: {body!r}")


class BoardClient:
    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        timeout: float = 15.0,
    ):
        self.base_url = (
            base_url
            or os.environ.get("BOARD_API_URL")
            or "https://board.dev.raftforge.art/api/v1"
        ).rstrip("/")
        self.token = token or os.environ.get("BOARD_API_TOKEN")
        if not self.token:
            raise RuntimeError(
                "BOARD_API_TOKEN не задан (env или передать в BoardClient(token=...))"
            )
        self._client = httpx.Client(
            timeout=timeout,
            headers={"Authorization": f"Bearer {self.token}"},
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "BoardClient":
        return self

    def __exit__(self, *a) -> None:
        self.close()

    def _check(self, r: httpx.Response) -> dict:
        if r.status_code >= 400:
            try:
                body = r.json()
            except Exception:
                body = r.text
            raise BoardAPIError(r.status_code, body)
        if r.status_code == 204:
            return {}
        return r.json()

    def upsert_by_ref(
        self, board_id: UUID, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """POST /boards/{board_id}/elements/by-ref — upsert.
        payload должен содержать externalRef, id, type, x, y, w, h, attrs,
        createdAt, updatedAt (см. Element.to_payload).
        """
        r = self._client.post(
            f"{self.base_url}/boards/{board_id}/elements/by-ref",
            json=payload,
        )
        return self._check(r)

    def get_by_ref(self, board_id: UUID, external_ref: UUID) -> dict[str, Any] | None:
        """GET /boards/{board_id}/elements/by-ref/{external_ref}.
        Возвращает dict или None если 404.
        """
        r = self._client.get(
            f"{self.base_url}/boards/{board_id}/elements/by-ref/{external_ref}"
        )
        if r.status_code == 404:
            return None
        return self._check(r)

    def delete_by_ref(self, board_id: UUID, external_ref: UUID) -> bool:
        """DELETE /boards/{board_id}/elements/by-ref/{external_ref}.
        Возвращает True если удалили, False если уже не было."""
        r = self._client.delete(
            f"{self.base_url}/boards/{board_id}/elements/by-ref/{external_ref}"
        )
        if r.status_code == 404:
            return False
        self._check(r)
        return True

    def get_board(self, board_id: UUID) -> dict[str, Any]:
        """GET /boards/{board_id} — board + все elements. Используется для
        sweep zombies в CLI render."""
        r = self._client.get(f"{self.base_url}/boards/{board_id}")
        return self._check(r)

    def frame_png_url(self, frame_id: UUID) -> str:
        """Public URL для PNG-рендера фрейма (без auth)."""
        # `frames` endpoint живёт на /api/v1, тот же origin
        return f"{self.base_url}/frames/{frame_id}.png"
