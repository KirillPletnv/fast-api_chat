async function sendMessageEventListenr() {
    const message = input.value.trim();
    if (message) {
        const activeUser = document.querySelector('.user-item.active');
        const activeRoom = document.querySelector('.room-item.active');

        if (activeUser) {
            // Логика для отправки сообщения пользователю
            const userId = activeUser.getAttribute('user-id');
            const response = await fetch('/api_v1/chat/send_message/', {
                method: 'POST',
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    interlocutor_id: userId,
                    content: message
                })
            });

            const result = await response.json();

            if (response.ok) {
                input.value = ''; // Очищаем поле ввода
            } else {
                alert(result.message || result.detail || 'Ошибка выполнения запроса');
            }
        } else if (activeRoom) {
            // Логика для отправки сообщения в комнату
            const roomId = activeRoom.getAttribute('data-room-id');
            const response = await fetch('/api_v1/chat/send_message_to_room/', {
                method: 'POST',
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    room_id: roomId,
                    content: message
                })
            });

            const result = await response.json();

            if (response.ok) {
                input.value = ''; // Очищаем поле ввода
            } else {
                alert(result.message || result.detail || 'Ошибка выполнения запроса');
            }
        } else {
            alert('Выберите пользователя или комнату для отправки сообщения.');
        }
    }
}