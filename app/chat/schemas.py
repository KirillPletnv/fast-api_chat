from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    received = 'received'  # Сообщение получено
    sent = 'sent'          # Сообщение отправлено
    room = 'room'          # Сообщение в комнате



class SInMessageToRoom(BaseModel):
    room_id: int = Field(..., description='ID комнаты')
    content: str = Field(..., min_length=1, max_length=200, description='Текст сообщения, от 1 до 200 знаков')

class SOutRoomMessage(BaseModel):
    type: MessageType = Field(default=MessageType.room, description='Тип сообщения: "room"')
    created: datetime = Field(..., description='Дата и время создания сообщения')
    room_id: int = Field(..., description='ID комнаты')
    sender_id: int = Field(..., description='ID отправителя')
    content: str = Field(..., min_length=1, max_length=200, description='Текст сообщения, от 1 до 200 знаков')
    #interlocutor_id: int | None = Field(None, description='ID комнаты (для унификации с SOutMessage)')

class RoomMessageResponse(BaseModel):
    id: int
    room_id: int
    sender_id: int
    content: str
    created_at: datetime
    interlocutor_id: int

class SInMessage(BaseModel):
    interlocutor_id: int = Field(..., description='ID получателя сообщения')
    content: str = Field(..., min_length=1, max_length=200, description='Текст сообщения, от 1 до 200 знаков')

class SOutMessage(BaseModel):
      id: int = Field()
      type: MessageType = Field(..., description='Тип сообщения: "received" или "sent"')
      created: datetime = Field(..., description='Дата и время создания сообщения') 
      interlocutor_id: int = Field(..., description='ID собеседника')
      content: str = Field(..., min_length=1, max_length=200, description='Текст сообщения, от 1 до 200 знаков')
      is_read: bool = Field(default=False, description='Статус прочтения сообщения')
