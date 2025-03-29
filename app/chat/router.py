
from fastapi import APIRouter, Depends, Query, Response

from app.chat.dao import MessageDAO, RoomMessageDAO

from app.chat.schemas import MessageType, SInMessage, SOutMessage, SInMessageToRoom, SOutRoomMessage
from functools import reduce
from app.websocket import manager as ws_manager
from app.chat.schemas import RoomMessageResponse
from fastapi import HTTPException, status
from sqlalchemy import update

from app.chat.models import Message
from fastapi import WebSocket, WebSocketDisconnect

from fastapi import APIRouter, Request, HTTPException
from app.chat.models import Room
from app.database import async_session_maker

from sqlalchemy import select


import logging
from fastapi import APIRouter, Depends
from typing import Annotated
from app.chat.dao import RoomMessageDAO
from app.chat.schemas import SInMessage
from app.users.dependensies import get_current_user_id_dependence


api_chat_router = APIRouter(prefix='/api_v1/chat', tags=['Messages'])
logging.basicConfig(level=logging.INFO)


logger = logging.getLogger(__name__)


@api_chat_router.get('/room_messages/{room_id}', response_model=list[SOutRoomMessage], description='Возвращает все сообщения для указанной комнаты')
async def get_room_messages(room_id: int, user_id: Annotated[int, Depends(get_current_user_id_dependence)]) -> list[SOutRoomMessage]:
    messages = await RoomMessageDAO.get_messages_by_room(room_id)
    return _convert_messages_for_room_format(user_id, messages)


@api_chat_router.post(
    '/send_message_to_room/',
    description='Отправка сообщения в комнату')
async def send_message(
        in_message: SInMessageToRoom,
        sender_id: Annotated[int, Depends(get_current_user_id_dependence)]) -> dict:
    # Логируем начало выполнения функции
    logger.info(f"Начало обработки запроса на отправку сообщения в комнату. "
                f"Отправитель: {sender_id}, Комната: {in_message.room_id}, "
                f"Содержание: {in_message.content}")

    try:

        new_message = await RoomMessageDAO.add(
            room_id=in_message.room_id,
            sender_id=sender_id,
            content=in_message.content
        )

        out_message = convert_room_message_to_out(new_message)



        ws_message = _create_ws_out_message(out_message)
        await ws_manager.broadcast(ws_message)
        logger.info(f"Сообщение успешно создано. ID сообщения: {new_message.id}, "
                    f"Комната: {new_message.room_id}, Отправитель: {new_message.sender_id}")


        logger.debug("Попытка отправки сообщения через WebSocket")


        logger.info("Сообщение успешно отправлено в комнату")

        return {'detail': 'Сообщение в комнату отправлено'}

    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения в комнату: {e}", exc_info=True)
        return {'detail': f'Произошла ошибка: {str(e)}'}


@api_chat_router.post(
    '/send_message/',
    description='Отправка сообщения авторизованным пользователем')
async def send_message(
        in_message: SInMessage,
        sender_id: Annotated[int,
                             Depends(get_current_user_id_dependence)]) -> dict:
    new_message: Message = await MessageDAO.add(
        sender_id=sender_id,
        recipient_id=in_message.interlocutor_id,
        content=in_message.content)
    sent_out_message = _create_sent_out_message(new_message)
    received_out_message = _create_received_out_message(new_message)
    ws_sent_message = _create_ws_out_message(sent_out_message)
    ws_received_message = _create_ws_out_message(received_out_message)
    await ws_manager.send_personal_message(sender_id, ws_sent_message)
    await ws_manager.send_personal_message(new_message.recipient_id, ws_received_message)

    return {'detail': 'Сообщение успешно отправлено'}


@api_chat_router.get(
    '/messages',
    response_model=list[SOutMessage],
    description=
    'Возвращает упорядоченную по времени создания переписку авторизованного пользователя, если указан ID - только переписку с пользователем с ID'
)
async def get_messages(
        user_id: Annotated[int, Depends(get_current_user_id_dependence)],
        interlocutor_id: Annotated[int | None, Query()] \
                = None) -> list[SOutMessage]:
    if interlocutor_id:
        raw_messages: list[Message] = \
            await MessageDAO.find_all_for_user_with_interlocutor(
                user_id=user_id,
                interlocutor_id=interlocutor_id
            )
    else:
        raw_messages: list[Message] = \
            await MessageDAO.find_all_for_user(user_id=user_id)

    messages: list[SOutMessage] = _convert_messages_format(
        user_id, raw_messages)

    return messages


def _convert_messages_format(user_id: int, raw_messages: list[Message]) -> list[SOutMessage]:
    def reduce_function(accumulator: list[SOutMessage], raw_message: Message):
        if raw_message.sender_id == user_id:
            message = _create_sent_out_message(raw_message)
        else:
            message = _create_received_out_message(raw_message)
        accumulator.append(message)
        return accumulator
    converted_messages: list[SOutMessage] = reduce(reduce_function, raw_messages, [])
    return converted_messages


def _convert_messages_for_room_format(user_id: int, raw_messages: list[RoomMessageResponse]) -> list[SOutRoomMessage]:
    def reduce_function(accumulator: list[SOutRoomMessage], raw_message: RoomMessageResponse):
        if raw_message.sender_id == user_id:
            message = convert_room_message_to_out(raw_message)
            message.type = MessageType.sent  # Сообщение отправлено текущим пользователем
        else:
            message = convert_room_message_to_out(raw_message)
            message.type = MessageType.received  # Сообщение получено от другого пользователя
        accumulator.append(message)
        return accumulator

    converted_messages: list[SOutRoomMessage] = reduce(reduce_function, raw_messages, [])
    return converted_messages



def convert_room_message_to_out(model_message: RoomMessageResponse) -> SOutRoomMessage:
    return SOutRoomMessage(
        type=MessageType.room,
        created=model_message.created_at,
        room_id=model_message.room_id,
        sender_id=model_message.sender_id,
        content=model_message.content,
        interlocutor_id=model_message.room_id  # Добавляем room_id как interlocutor_id
    )



def _create_sent_out_message(model_message: Message):
    sent_out_message: SOutMessage = SOutMessage(
        id=model_message.id,
        type=MessageType.sent.value,
        created=model_message.created_at,
        interlocutor_id=model_message.recipient_id,
        content=model_message.content,
        is_read=model_message.is_read
    )

    return sent_out_message


def _create_received_out_message(model_message: Message):
    received_out_message: SOutMessage = SOutMessage(
        id=model_message.id,
        type=MessageType.received.value,
        created=model_message.created_at,
        interlocutor_id=model_message.sender_id,
        content=model_message.content,
        is_read=model_message.is_read
    )

    return received_out_message


def _create_ws_out_message(out_message: SOutRoomMessage | SOutMessage):
    out_message.created = out_message.created.isoformat()
    return {
        'type': 'new_message',
        'message': out_message.model_dump()
    }


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



@api_chat_router.post('/create-room')
async def create_room(request: Request):
    logger.info("Получен запрос на создание комнаты")
    try:
        data = await request.json()
        logger.info(f"Данные запроса: {data}")
        # Проверяем наличие обязательного поля 'name'
        if "name" not in data:
            logger.error("Отсутствует обязательное поле 'name'")
            raise HTTPException(status_code=422, detail="Поле 'name' обязательно")

        room_name = data["name"]
        logger.info(f"Попытка создания комнаты с именем: {room_name}")
        async with async_session_maker() as session:
            # Создаем новую комнату
            new_room = Room(name=room_name)
            session.add(new_room)
            await session.commit()
            await session.refresh(new_room)
            logger.info(f"Комната '{room_name}' успешно создана. ID комнаты: {new_room.id}")
            # Возвращаем ответ клиенту
            await room_list_update()
            return {
                "message": "ответ серверу о создании комнаты",
                "room_id": new_room.id,
                "room_name": new_room.name,
            }

    except HTTPException as he:
        logger.error(f"HTTP ошибка: {he.detail}")
        raise he

    except Exception as e:
        logger.error(f"Ошибка при создании комнаты: {e}")
        raise HTTPException(
            status_code=500,
            detail="Не удалось создать комнату",
        )

async def room_list_update():
    async with async_session_maker() as session:
        result = await session.execute(select(Room))
        rooms = result.scalars().all()
        rooms_data = [{"id": room.id, "name": room.name} for room in rooms]
        await ws_manager.broadcast({
            "type": "rooms_update",
            "rooms": rooms_data
        })


@api_chat_router.get('/update-room')
async def create_room():
    await room_list_update()



@api_chat_router.websocket("/ws/rooms")
async def websocket_rooms(websocket: WebSocket):
    await websocket.accept()
    try:
        # Отправляем текущий список комнат при подключении
        async with async_session_maker() as session:
            result = await session.execute(select(Room))
            rooms = result.scalars().all()
            await websocket.send_json({
                "type": "rooms_list",
                "rooms": [{"id": room.id, "name": room.name} for room in rooms]
            })

        # Ожидаем сообщений от клиента (если нужно)
        while True:
            data = await websocket.receive_text()
            # Обработка входящих сообщений (если необходимо)

    except WebSocketDisconnect:
        print(f"Клиент отключился")
    except Exception as e:
        print(f"WebSocket ошибка: {e}")


@api_chat_router.post('/mark_as_read/{message_id}', description='Обновляет статус сообщения на "прочитано"')
async def mark_message_as_read(message_id: int, user_id: Annotated[int, Depends(get_current_user_id_dependence)]) -> dict:
    async with async_session_maker() as session:
        # Получаем сообщение по ID
        message = await session.get(Message, message_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сообщение не найдено"
            )

        # Проверяем, что текущий пользователь является получателем
        if message.recipient_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы не можете пометить это сообщение как прочитанное"
            )

        # Обновляем статус сообщения
        await session.execute(
            update(Message)
            .where(Message.id == message_id)
            .values(is_read=True)
        )
        await session.commit()

        logger.info(f"Сообщение {message_id} помечено как прочитанное пользователем {user_id}")
        await ws_manager.broadcast(
            {
                "type": "message_read",  # Тип события
                "message_id": message_id,  # ID сообщения
                "read_by": user_id,  # ID пользователя, который прочитал сообщение
                "sender_id": message.sender_id  # ID отправителя сообщения
            },
            exclude_user_ids=[user_id]  # Исключаем текущего пользователя
        )
        return {"detail": "Сообщение помечено как прочитанное"}


import os
from datetime import datetime
from fastapi import UploadFile, File
from fastapi.responses import FileResponse
from fastapi import Form
from fastapi.responses import JSONResponse


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)



@api_chat_router.post("/upload-file/")
async def upload_file(
    file_name: str = Form(..., min_length=1, max_length=100),
    file: UploadFile = File(...), dependencies=Depends(get_current_user_id_dependence)):
    try:
        logger.info(f"Начало загрузки файла. Имя: {file_name}, размер: {file.size} байт")


        if not file_name or any(c in file_name for c in '/\\?%*:|"<>'):
            raise HTTPException(status_code=400, detail="Недопустимое имя файла")


        original_extension = os.path.splitext(file.filename)[1]

        final_filename = f"{file_name}{original_extension}"
        file_path = os.path.join(UPLOAD_DIR, final_filename)
        if os.path.exists(file_path):
            logger.warning(f"Файл уже существует: {final_filename}")
            raise HTTPException(status_code=400, detail="Файл с таким именем уже существует")



        if os.path.exists(file_path):
            logger.warning(f"Файл уже существует: {file_name}")
            raise HTTPException(status_code=400, detail="Файл с таким именем уже существует")


        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        logger.info(f"Файл сохранен: {file_name}, размер: {len(content)} байт")

        return JSONResponse({
            "status": "success",
            "filename": file_name,
            "saved_at": datetime.now().isoformat(),
            "size": len(content)
        })

    except HTTPException as he:
        logger.error(f"HTTP ошибка: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Ошибка загрузки: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@api_chat_router.get("/list-files/")
async def list_files():
    try:
        logger.info("Запрос списка файлов")

        files = []
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(file_path):
                file_info = {
                    "name": filename,
                    "size": os.path.getsize(file_path),
                    "upload_date": datetime.fromtimestamp(
                        os.path.getmtime(file_path)
                    ).isoformat()
                }
                files.append(file_info)
                logger.debug(f"Найден файл: {filename}, размер: {file_info['size']} байт")

        logger.info(f"Возвращено {len(files)} файлов")
        return {"files": files}

    except Exception as e:
        logger.error(f"Ошибка получения списка файлов: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Не удалось получить список файлов: {str(e)}"
        )


@api_chat_router.get("/download-file/{filename}")
async def download_file(filename: str):
    try:
        logger.info(f"Запрос на скачивание файла: {filename}")

        file_path = os.path.join(UPLOAD_DIR, filename)

        if not os.path.exists(file_path):
            logger.error(f"Файл не найден: {filename}")
            raise HTTPException(status_code=404, detail="Файл не найден")

        logger.info(f"Отправка файла: {filename}")
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/octet-stream"
        )

    except HTTPException as he:
        logger.error(f"Ошибка скачивания (HTTP): {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Ошибка скачивания файла: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Не удалось скачать файл: {str(e)}"
        )