from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from app.database import Base


class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True )
    sender_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    recipient_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    content: Mapped[str]
    is_read: Mapped[bool] = mapped_column(default=False)
    
    # __table_args__ = {"implicit_returning": True}
    __mapper_args__ = {"eager_defaults": True}


from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from app.database import Base

class Room(Base):
    __tablename__ = 'rooms'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]  # Название комнаты
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)  # Время создания комнаты


from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from app.database import Base

class RoomMessage(Base):
    __tablename__ = 'room_messages'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    room_id: Mapped[int] = mapped_column(ForeignKey('rooms.id', ondelete="CASCADE"))
    sender_id: Mapped[int] = mapped_column(ForeignKey('users.id'))  # Связь с пользователем (отправитель)
    content: Mapped[str]  # Текст сообщения
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)  # Время отправки сообщения

