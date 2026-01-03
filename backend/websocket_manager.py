from fastapi import WebSocket
from typing import Dict, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}  #user_id -> WebSocket
        self.user_info: Dict[str, dict] = {}  #user_id -> {username, avatar, is_admin}
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, user_id: str, user_info: dict):
        await websocket.accept()
        async with self._lock:
            if user_id in self.active_connections:
                try:
                    await self.active_connections[user_id].close()
                except Exception:
                    pass
            
            self.active_connections[user_id] = websocket
            self.user_info[user_id] = user_info
        
        logger.info(f"User {user_info.get('username', user_id)} connected. Total: {len(self.active_connections)}")

        await self.broadcast({
            "type": "user_join",
            "data": {
                "user_id": user_id,
                **user_info,
                "online_count": len(self.active_connections)
            }
        }, exclude=user_id)
    
    async def disconnect(self, user_id: str):
        user_info = {}
        async with self._lock:
            if user_id in self.active_connections:
                del self.active_connections[user_id]
            user_info = self.user_info.pop(user_id, {})
        
        logger.info(f"User {user_info.get('username', user_id)} disconnected. Total: {len(self.active_connections)}")
        
        await self.broadcast({
            "type": "user_leave",
            "data": {
                "user_id": user_id,
                **user_info,
                "online_count": len(self.active_connections)
            }
        })
    
    async def send_personal(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send message to user {user_id}: {e}")
                await self.disconnect(user_id)
    
    async def broadcast(self, message: dict, exclude: Optional[str] = None):
        disconnected = []
        
        async with self._lock:
            connections = dict(self.active_connections)
        
        for user_id, websocket in connections.items():
            if exclude and user_id == exclude:
                continue
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to broadcast to user {user_id}: {e}")
                disconnected.append(user_id)

        for user_id in disconnected:
            await self.disconnect(user_id)
    
    def get_online_users(self) -> list:
        return [
            {"user_id": uid, **info}
            for uid, info in self.user_info.items()
        ]
    
    def get_online_count(self) -> int:
        return len(self.active_connections)
    
    def is_user_online(self, user_id: str) -> bool:
        return user_id in self.active_connections


manager = ConnectionManager()