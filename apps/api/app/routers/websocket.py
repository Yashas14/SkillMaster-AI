# ════════════════════════════════════════════════════════════
# WebSocket Router — Real-time collaboration
# ════════════════════════════════════════════════════════════

import json
from datetime import UTC, datetime

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.services.websocket_manager import ws_manager

router = APIRouter()


@router.websocket("/connect")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str = Query(...),
    user_name: str = Query("Anonymous"),
):
    """Main WebSocket connection endpoint for real-time features."""
    await ws_manager.connect(websocket, user_id)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            msg_type = message.get("type", "")

            if msg_type == "ping":
                await ws_manager.send_personal(user_id, {
                    "type": "pong",
                    "timestamp": datetime.now(UTC).isoformat(),
                })

            elif msg_type == "join_room":
                room_id = message.get("room_id", "")
                if room_id:
                    await ws_manager.join_room(user_id, room_id)
                    await ws_manager.send_personal(user_id, {
                        "type": "room_joined",
                        "room_id": room_id,
                        "users": ws_manager.get_room_users(room_id),
                    })

            elif msg_type == "leave_room":
                room_id = message.get("room_id", "")
                if room_id:
                    await ws_manager.leave_room(user_id, room_id)

            elif msg_type == "room_message":
                room_id = message.get("room_id", "")
                content = message.get("content", "")
                if room_id and content:
                    await ws_manager.broadcast_to_room(
                        room_id,
                        {
                            "type": "room_message",
                            "room_id": room_id,
                            "user_id": user_id,
                            "user_name": user_name,
                            "content": content,
                            "timestamp": datetime.now(UTC).isoformat(),
                        },
                    )

            elif msg_type == "typing":
                room_id = message.get("room_id", "")
                if room_id:
                    await ws_manager.broadcast_to_room(
                        room_id,
                        {
                            "type": "user_typing",
                            "room_id": room_id,
                            "user_id": user_id,
                            "user_name": user_name,
                        },
                        exclude_user=user_id,
                    )

            elif msg_type == "cursor_position":
                room_id = message.get("room_id", "")
                position = message.get("position", {})
                if room_id:
                    await ws_manager.broadcast_to_room(
                        room_id,
                        {
                            "type": "cursor_update",
                            "user_id": user_id,
                            "user_name": user_name,
                            "position": position,
                        },
                        exclude_user=user_id,
                    )

            elif msg_type == "code_change":
                room_id = message.get("room_id", "")
                changes = message.get("changes", {})
                if room_id:
                    await ws_manager.broadcast_to_room(
                        room_id,
                        {
                            "type": "code_change",
                            "user_id": user_id,
                            "user_name": user_name,
                            "changes": changes,
                            "timestamp": datetime.now(UTC).isoformat(),
                        },
                        exclude_user=user_id,
                    )

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, user_id)
    except Exception:
        ws_manager.disconnect(websocket, user_id)


@router.get("/online")
async def get_online_users():
    """Get count of currently connected users."""
    return {"online_count": ws_manager.get_online_count()}
