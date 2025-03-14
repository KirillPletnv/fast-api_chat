from app.dao.base import BaseDAO
from app.chat.models import Message
from app.database import async_session_maker
from sqlalchemy import select, union_all
import logging

class MessageDAO(BaseDAO):
    model = Message

    @classmethod
    async def find_all_for_user_with_interlocutor(
            cls, user_id: int, interlocutor_id: int) -> list[Message]:
        async with async_session_maker() as session:
            query1 = select(cls.model)\
                .filter_by(sender_id=user_id, recipient_id=interlocutor_id)
            query2 = select(cls.model)\
                .filter_by(sender_id=interlocutor_id, recipient_id=user_id)
            u = union_all(query1, query2).order_by(Message.created_at)

            stmt = select(Message).from_statement(u)
            result = await session.execute(stmt)
        return result.scalars()

    @classmethod
    async def find_all_for_user(cls, user_id: int) -> list[Message]:
        async with async_session_maker() as session:
            query1 = select(cls.model)\
                .filter_by(sender_id=user_id)
            query2 = select(cls.model)\
                .filter_by(recipient_id=user_id)
            u = union_all(query1, query2).order_by(Message.created_at)

            stmt = select(Message).from_statement(u)
            result = await session.execute(stmt)
        return result.scalars()




from app.chat.models import RoomMessage

logger = logging.getLogger(__name__)

class RoomMessageDAO(BaseDAO):
    model = RoomMessage

    @staticmethod
    async def get_messages_by_room(room_id: int) -> list[RoomMessage]:
        async with async_session_maker() as session:
            query = select(RoomMessage).where(RoomMessage.room_id == room_id)
            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def add(room_id: int, sender_id: int, content: str) -> RoomMessage:
        # Логируем начало операции
        logger.info(f"Попытка добавления сообщения в комнату. "
                    f"Комната: {room_id}, Отправитель: {sender_id}, "
                    f"Содержание: {content}")

        async with async_session_maker() as session:
            try:
                # Создаем новое сообщение
                new_message = RoomMessage(
                    room_id=room_id,
                    sender_id=sender_id,
                    content=content
                )

                # Логируем создание объекта сообщения
                logger.debug(f"Создан объект сообщения: {new_message}")

                # Добавляем сообщение в сессию
                session.add(new_message)

                # Логируем попытку фиксации изменений в базе данных
                logger.debug("Попытка фиксации изменений в базе данных")

                # Фиксируем изменения
                await session.commit()

                # Логируем успешную фиксацию изменений
                logger.info(f"Сообщение успешно добавлено в комнату. ID сообщения: {new_message.id}")

                # Обновляем объект сообщения
                await session.refresh(new_message)

                # Логируем обновление объекта сообщения
                logger.debug(f"Объект сообщения обновлен: {new_message}")

                return new_message

            except Exception as e:
                # Логируем ошибку, если что-то пошло не так
                logger.error(f"Ошибка при добавлении сообщения в комнату: {e}", exc_info=True)
                raise