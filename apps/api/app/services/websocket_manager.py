# ════════════════════════════════════════════════════════════
# WebSocket Manager — Real-time collaboration
# ════════════════════════════════════════════════════════════

from __future__ import annotations

import contextlib
import json
from datetime import UTC, datetime
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    """Manage WebSocket connections for real-time collaboration features."""

    def __init__(self) -> None:
        # user_id -> list of active connections
        self._connections: dict[str, list[WebSocket]] = {}
        # room_id -> set of user_ids
        self._rooms: dict[str, set[str]] = {}
        # user_id -> set of room_ids
        self._user_rooms: dict[str, set[str]] = {}

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        await websocket.accept()
        if user_id not in self._connections:
            self._connections[user_id] = []
        self._connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        if user_id in self._connections:
            self._connections[user_id] = [
                ws for ws in self._connections[user_id] if ws != websocket
            ]
            if not self._connections[user_id]:
                del self._connections[user_id]

        # Leave all rooms
        if user_id in self._user_rooms:
            for room_id in list(self._user_rooms[user_id]):
                self._rooms.get(room_id, set()).discard(user_id)
            del self._user_rooms[user_id]

    async def join_room(self, user_id: str, room_id: str) -> None:
        if room_id not in self._rooms:
            self._rooms[room_id] = set()
        self._rooms[room_id].add(user_id)

        if user_id not in self._user_rooms:
            self._user_rooms[user_id] = set()
        self._user_rooms[user_id].add(room_id)

        await self.broadcast_to_room(
            room_id,
            {
                "type": "user_joined",
                "user_id": user_id,
                "room_id": room_id,
                "timestamp": datetime.now(UTC).isoformat(),
            },
            exclude_user=user_id,
        )

    async def leave_room(self, user_id: str, room_id: str) -> None:
        if room_id in self._rooms:
            self._rooms[room_id].discard(user_id)
            if not self._rooms[room_id]:
                del self._rooms[room_id]

        if user_id in self._user_rooms:
            self._user_rooms[user_id].discard(room_id)

        await self.broadcast_to_room(
            room_id,
            {
                "type": "user_left",
                "user_id": user_id,
                "room_id": room_id,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

    async def send_personal(self, user_id: str, message: dict[str, Any]) -> None:
        if user_id in self._connections:
            payload = json.dumps(message)
            for ws in self._connections[user_id]:
                with contextlib.suppress(Exception):
                    await ws.send_text(payload)

    async def broadcast_to_room(
        self,
        room_id: str,
        message: dict[str, Any],
        exclude_user: str | None = None,
    ) -> None:
        if room_id not in self._rooms:
            return
        payload = json.dumps(message)
        for uid in self._rooms[room_id]:
            if uid == exclude_user:
                continue
            if uid in self._connections:
                for ws in self._connections[uid]:
                    with contextlib.suppress(Exception):
                        await ws.send_text(payload)

    async def broadcast_all(self, message: dict[str, Any]) -> None:
        payload = json.dumps(message)
        for _uid, connections in self._connections.items():
            for ws in connections:
                with contextlib.suppress(Exception):
                    await ws.send_text(payload)

    def get_room_users(self, room_id: str) -> list[str]:
        return list(self._rooms.get(room_id, set()))

    def get_online_count(self) -> int:
        return len(self._connections)


ws_manager = ConnectionManager()
