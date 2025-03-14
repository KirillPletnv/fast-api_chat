# from typing import Annotated
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect


class ConnectionManager:
    def __init__(self):
        
        self.active_connections: dict[int, list[WebSocket]]  = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        print(f'async def connect(self, user_id: int, websocket: WebSocket): pre')
        await websocket.accept();
        if self.active_connections.get(user_id) is None:
            self.active_connections[user_id] = []
        print(f'async def connect(self, user_id: int, websocket: WebSocket): past')
        self.active_connections[user_id].append(websocket);

    def disconnect(self, user_id: int, websocket: WebSocket):
        if (connection_list:=self.active_connections.get(user_id)) is None:
            return
        connection_list.remove(websocket);
        if not connection_list:
            del self.active_connections[user_id]

    async def send_personal_message(self, user_id: int, message: dict):
        print(f'async def send_personal_message(self, user_id: int, message: dict):')
        if (connection_list:=self.active_connections.get(user_id)) is None:
            return
        
        for connection in connection_list:
            await connection.send_json(message)
    
    async def broadcast(self, message: dict, exclude_user_ids=[]):
        print(f"Broadcasting message: {message}")
        for user_id, connection_list in self.active_connections.items():
            if user_id not in exclude_user_ids:  # Исключаем пользователей из списка
                for connection in connection_list:
                    await connection.send_json(message)

    async def broadcast_to_room(self, message: dict):
        for connection in self.active_connections:
            if connection.room_id == room_id:  # Предположим, что у соединения есть room_id
                await connection.send_json(message)


manager = ConnectionManager()


