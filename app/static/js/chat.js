document.addEventListener('DOMContentLoaded', domLoadEventListener);

let activUserId = null;
let activRoomId = null;
let roomChatHistories = {};
let users = {};

async function domLoadEventListener(event) {
    const users_container = document.querySelector('.users-container');
    const userItems = [];
    const messageInput = document.querySelector('.message-input');
    const chatHistory = document.querySelector('.chat-history');
    const selectChatMessage = document.querySelector('.select-chat-message');
    const selectedUser = document.querySelector('.selected-user');
    const input = document.querySelector('.message-input input');
    const sendButton = document.querySelector('.message-input button');
    const logoutButton = document.querySelector('.logout-btn');


    const me = await get_me();
    if (!me) {
        return;
    }


    const interlocutors = await get_interlocutors();
    if (!interlocutors) {
        return;
    }

    fill_user_container(users_container, interlocutors, userItems);

    const messages = await get_messages();
    if (!messages) {
        return;
    }

    const chatHistories = convert_messages_to_chatHistory(messages, me);
    //get_room_messages(activRoomId);

    userItems.forEach(user => {
        user.addEventListener('click', function () {
            deactivateAllItems();
            userItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
            activUserId = this.getAttribute('user-id');
            activRoomId = null;

            chatHistory.style.display = 'block';
            messageInput.style.display = 'flex';
            selectChatMessage.style.display = 'none';

            displayChatHistory(activUserId, chatHistory, chatHistories, me);
        });
    });



    async function sendMessageEventListenr() {
        const message = input.value.trim();
        if (message) {
            if (activRoomId) {
                // Отправка сообщения в комнату
                const response = await fetch('/api_v1/chat/send_message_to_room/', {
                    method: 'POST',
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        room_id: activRoomId,
                        content: message
                    })
                });

                const result = await response.json();
                if (response.ok) {
                    input.value = '';
                    const newMessage = {
                    type: 'sent',
                    //type: 'sent', // или 'received', в зависимости от логики
                    content: message,
                    created: new Date().toISOString(), // Текущая дата и время
                    room_id: activRoomId,
                };

                // Добавляем сообщение в историю комнаты
                if (!roomChatHistories[activRoomId]) {
                    roomChatHistories[activRoomId] = [];
                }
                roomChatHistories[activRoomId].push(newMessage);

                // Отображаем сообщение в интерфейсе
                //add_message_to_chat_chistory(newMessage, chatHistory, true);
                } else {
                    alert(result.message || result.detail || 'Ошибка выполнения запроса');
                }
            } else if (activUserId) {
                // Отправка сообщения пользователю
                const response = await fetch('/api_v1/chat/send_message/', {
                    method: 'POST',
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        interlocutor_id: activUserId,
                        content: message
                    })
                });
                const result = await response.json();
                if (response.ok) {
                    input.value = '';
                } else {
                    alert(result.message || result.detail || 'Ошибка выполнения запроса');
                }
            }
        }
    }
    sendButton.addEventListener('click', sendMessageEventListenr);

    input.addEventListener('keypress', async function (e) {
        if (e.key === 'Enter') {
            await sendMessageEventListenr();
        }
    });

    logoutButton.addEventListener('click', async function () {
        if (websocket) {
            websocket.close();
        }

        const response = await fetch('/api_v1/auth/logout/', {
            method: 'POST'
        });
        window.location.href = '/chat';
    });

    const websocket = new WebSocket(`ws://5.35.108.213:8080/ws/connect?user_id=${me.id}`);

    websocket.onopen = () => {

    get_rooms();
    console.info('WebSocket соединение установлено');
    }

    websocket.onmessage = (event) => {
        const in_message = JSON.parse(event.data);
        const message_type = in_message.type;

        if (message_type === 'new_message') {
            process_new_message_message(in_message, activUserId, activRoomId, chatHistories, roomChatHistories, chatHistory, me);
        } else if (message_type === 'message_read') {
        // Обработка события "сообщение прочитано"
        updateMessageReadStatus(in_message.message_id);

        } else if (message_type === 'new_user') {
            process_new_user_message(in_message);
        } else if (message_type === 'rooms_list' || message_type === 'rooms_update') {
            updateRoomsList(in_message.rooms, document.querySelector('.rooms-container'), me);
        } else {
            alert(`Не поддерживаемый тип сообщения: ${message_type}`);
        }
    };
    websocket.onclose = (event) => {
        console.info(`[close] Соединение закрыто, код=${event.code} причина=${event.reason}`);
    };
    websocket.onerror = (e) => {
        console.error(e);
    };
}

function process_new_user_message(in_message) {
    // Логика обработки нового пользователя
}

function process_new_message_message(in_message, activUserId, activRoomId, chatHistories, roomChatHistories, chatHistory, me) {
    const ms = in_message.message;
    if (ms.interlocutor_id) {
        // Личные сообщения
        add_message_to_chat_Histories(ms, chatHistories);
        if (ms.interlocutor_id == activUserId) {
            add_message_to_chat_chistory(ms, chatHistory, true);
        }
        if (ms.sender_id !== me.id) { // Если сообщение от другого пользователя
            //markMessageAsRead(ms.id); // Отправляем запрос на сервер
            ms.is_read = true; // Локально обновляем статус
        }
    } else if (ms.room_id) {
        ms.type = ms.sender_id === me.id ? 'sent' : 'received';
        if (ms.type === 'received') {
            const senderName = users[ms.sender_id] || ms.sender_id; // Используем имя или sender_id, если имя неизвестно
            ms.content = `${senderName}: ${ms.content}`;
        }
        add_message_to_room_chat_Histories(ms, roomChatHistories);
        if (ms.room_id == activRoomId) {
            add_message_to_chat_chistory(ms, chatHistory, true);
        }
    }
}


async function get_me() {
    const me_response = await fetch('/api_v1/users/me', { method: 'GET' });
    const me_result = await me_response.json();

    if (!me_response.ok) {
        alert(me_result.message || me_result.detail || 'Ошибка выполнения запроса авторизации');
        window.location.href = '/chat/login';
        return;
    }

    return me_result;
}

async function get_interlocutors() {
    const interlocutors_response = await fetch('/api_v1/users/all_interlocutors', { method: 'GET' });
    const interlocutors_result = await interlocutors_response.json();

    if (!interlocutors_response.ok) {
        alert(interlocutors_result.message || interlocutors_result.detail || 'Ошибка выполнения запроса собеседников');
        return;
    }
    interlocutors_result.forEach(user => {
        users[user.id] = user.name; // Сохраняем имя пользователя по id
    });

    return interlocutors_result;
}


function fill_user_container(users_container, interlocutors, userItems) {
    interlocutors.forEach(user => {
        const userElement = document.createElement('div');
        userElement.classList.add('user-item');
        userElement.setAttribute('user-id', user.id);
        userElement.textContent = user.name;
        users_container.appendChild(userElement);
        userItems.push(userElement);
    });
}

function displayChatHistory(activUserId, chatHistory, chatHistories, me) {
    chatHistory.innerHTML = '';
    const messages = chatHistories[activUserId];
    if (messages) {
        messages.forEach(message => add_message_to_chat_chistory(message, chatHistory, true, me));
    }
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function add_message_to_chat_chistory(message, chatHistory, scrollTop = true, me=undefined) {
    console.log('Displaying message:', message);
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', message.type || 'received');
    messageElement.setAttribute('data-message-id', message.id);

    if (message.room_id && message.type === 'received') {
        // Сообщение в комнате и полученное (имеет имя отправителя в content)
        const [sender, content] = message.content.split(': ');
        const senderElement = document.createElement('span');
        senderElement.classList.add('sender');
        senderElement.textContent = `${sender}: `;
        const contentElement = document.createElement('span');
        contentElement.textContent = content;

        messageElement.appendChild(senderElement);
        messageElement.appendChild(contentElement);
    } else {
        // Личное сообщение или отправленное сообщение в комнате
        messageElement.textContent = message.content;

        if (message.type === 'sent' && !message.room_id) {
            console.log('Message is_read:', message.is_read);
            const readIcon = document.createElement('span');
            readIcon.classList.add('read-icon');

            // Одна галочка, если сообщение не прочитано
            if (!message.is_read) {
                readIcon.textContent = '✓';
            }
            // Две галочки, если сообщение прочитано
            else {
                readIcon.textContent = '✓✓';
            }


            messageElement.appendChild(readIcon);
        }
    }


    if (message.type === 'received' && !message.is_read && typeof me !== 'undefined' && message.sender_id !== me.id) {
        markMessageAsRead(message.id); // Отправляем запрос на сервер
        //message.is_read = true; // Локально обновляем статус
    }

    chatHistory.appendChild(messageElement);
    if (scrollTop) {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
}

function updateRoomsList(rooms, container, me) {
    container.innerHTML = '';
    rooms.forEach(room => {
        const roomElement = document.createElement('div');
        roomElement.classList.add('room-item');
        roomElement.textContent = room.name;
        roomElement.setAttribute('data-room-id', room.id);
        container.appendChild(roomElement);

        // Добавляем обработчик события для выбора комнаты
        roomElement.addEventListener('click', async function () {
            console.log('До выбора комнаты:', { activUserId, activRoomId }); // Отладка
            const chatHistory = document.querySelector('.chat-history');
            const messageInput = document.querySelector('.message-input');
            const selectChatMessage = document.querySelector('.select-chat-message');

            // Убираем класс active у всех комнат
            container.querySelectorAll('.room-item').forEach(item => item.classList.remove('active'));
            // Добавляем класс active к выбранной комнате


            // Обновляем значение активной комнаты
            deactivateAllItems();
            activRoomId = room.id; // <-- Здесь обновляется переменная activRoomId
            activUserId = null;
            this.classList.add('active');
            console.log('После выбора комнаты:', { activUserId, activRoomId }); // Отладка
            // Проверяем, загружены ли сообщения для этой комнаты
            if (!roomChatHistories[activRoomId]) {
                const roomMessages = await get_room_messages(room.id, me);
                if (roomMessages) {
                    roomChatHistories[activRoomId] = roomMessages; // Сохраняем сообщения в кеш
                }
            }

            // Отображаем историю сообщений из кеша
            displayRoomChatHistory(activRoomId, chatHistory, roomChatHistories[activRoomId]);

            chatHistory.style.display = 'block';
            messageInput.style.display = 'flex';
            selectChatMessage.style.display = 'none';

            // Отображаем историю сообщений для выбранной комнаты
            //displayRoomChatHistory(room.id, chatHistory, chatHistories);
        });
    });
}

async function get_room_messages(roomId, me) {
    if (!roomId) {
        console.error('roomId не указан');
        return;
    }

    const response = await fetch(`/api_v1/chat/room_messages/${roomId}`, { method: 'GET' });
    const result = await response.json();

    if (!response.ok) {
        alert(result.message || result.detail || 'Ошибка выполнения запроса сообщений комнаты');
        return;
    }

    // Форматируем сообщения
    const formattedMessages = result.map(ms => {
        if (ms.sender_id !== me.id) {
            const senderName = users[ms.sender_id] || ms.sender_id; // Используем имя или sender_id, если имя неизвестно
            ms.content = `${senderName}: ${ms.content}`;
        }
        return {
            type: ms.sender_id === me.id ? 'sent' : 'received',
            created: ms.created,
            content: ms.content,
            room_id: ms.room_id,
        };
    });

    console.log('Сообщения комнаты:', formattedMessages); // Отладка
    return formattedMessages;
}




async function get_messages() {
    const messages_response = await fetch('/api_v1/chat/messages', { method: 'GET' });
    const messages_result = await messages_response.json();

    if (!messages_response.ok) {
        alert(messages_result.message || messages_result.detail || 'Ошибка выполнения запроса истории сообщений');
        return;
    }

    return messages_result;
}

function convert_messages_to_chatHistory(messages, me) {
    const chatHistories = {};
    messages.forEach(ms => {
        console.log('Message:', ms); // Проверьте, есть ли is_read
        if (ms.interlocutor_id) {
            // Личные сообщения
            if (!chatHistories[ms.interlocutor_id]) {
                chatHistories[ms.interlocutor_id] = [];
            }
            console.log('Message from history:', ms);
            chatHistories[ms.interlocutor_id].push({
                id: ms.id,
                type: ms.type,
                created: ms.created,
                content: ms.content,
                is_read: ms.is_read,
            });
        } else if (ms.room_id) {
            // Сообщения в комнате
            if (!chatHistories[ms.room_id]) {
                chatHistories[ms.room_id] = [];
            }
            // Добавляем имя отправителя к content, если сообщение не отправлено текущим пользователем
            if (ms.sender_id !== me.id) {
                const senderName = users[ms.sender_id] || ms.sender_id; // Используем имя или sender_id, если имя неизвестно
                ms.content = `${senderName}: ${ms.content}`;
            }
            chatHistories[ms.room_id].push({
                type: ms.sender_id === me.id ? 'sent' : 'received',
                created: ms.created,
                content: ms.content,
                room_id: ms.room_id,
            });
        }
    });
    return chatHistories;
}

function add_message_to_chat_Histories(ms, chatHistories) {
    console.log('ms=', ms);
    if (!chatHistories[ms.interlocutor_id]) {
        chatHistories[ms.interlocutor_id] = [];
    }
    chatHistories[ms.interlocutor_id].push({ id: ms.id, type: ms.type, created: ms.created, content: ms.content, is_read: ms.is_read });

}
async function get_rooms() {
    const messages_response = await fetch('/api_v1/chat/update-room', { method: 'GET' });
    if (!messages_response.ok) {
        const result = await response.json();
        alert(messages_result.message || messages_result.detail || 'Ошибка выполнения запроса комнат');
    }
     // Исправлено: добавлено объявление result
    return;
}

function deactivateAllItems() {
    // Деактивируем всех пользователей
    document.querySelectorAll('.user-item').forEach(user => user.classList.remove('active'));
    // Деактивируем все комнаты
    document.querySelectorAll('.room-item').forEach(room => room.classList.remove('active'));
}


function displayRoomChatHistory(roomId, chatHistory, roomMessages) {
    chatHistory.innerHTML = '';
    if (roomMessages) {
        roomMessages.forEach(message => add_message_to_chat_chistory(message, chatHistory, true));
    }
    chatHistory.scrollTop = chatHistory.scrollHeight;
}


function add_message_to_room_chat_Histories(ms, roomChatHistories) {
    if (!roomChatHistories[ms.room_id]) {
        roomChatHistories[ms.room_id] = [];
    }
    roomChatHistories[ms.room_id].push({ type: ms.type, created: ms.created, content: ms.content });
}

async function markMessageAsRead(messageId) {
    const response = await fetch(`/api_v1/chat/mark_as_read/${messageId}`, {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
    });

    if (!response.ok) {
        const result = await response.json();
        console.error('Ошибка при обновлении статуса сообщения:', result.message || result.detail);
    } else {
        // Обновляем интерфейс после успешного обновления статуса
        const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
        if (messageElement) {
            const readIcon = messageElement.querySelector('.read-icon');
            if (readIcon) {
                readIcon.textContent = '✓✓'; // Обновляем галочки
            }
        }
    }
}

function updateMessageReadStatus(messageId, chatHistories) {
    // Находим DOM-элемент сообщения по его ID
    const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
    if (messageElement) {
        // Находим иконку прочтения внутри элемента сообщения
        const readIcon = messageElement.querySelector('.read-icon');
        if (readIcon) {
            // Обновляем иконку на две галочки
            readIcon.textContent = '✓✓';
        }

        // Обновляем статус сообщения в chatHistories (если нужно)
        for (const userId in chatHistories) {
            const messages = chatHistories[userId];
            const message = messages.find(m => m.id === messageId);
            if (message) {
                message.is_read = true;
                break;
            }
        }
    }
}

