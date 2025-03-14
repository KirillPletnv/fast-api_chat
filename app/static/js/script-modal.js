// Получаем модальное окно
var modal = document.getElementById("myModal");
// Получаем кнопку, которая открывает модальное окно
var btn = document.getElementById("openModal");
// Получаем элемент <span>, который закрывает модальное окно
var span = document.getElementsByClassName("close")[0];
// Когда пользователь нажимает на кнопку, открываем модальное окно
btn.onclick = function() {
    modal.style.display = "block";
}
// Когда пользователь нажимает на <span> (x), закрываем модальное окно
span.onclick = function() {
    modal.style.display = "none";
}
// Когда пользователь кликает вне модального окна, закрываем его
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}
// Находим форму и модальное окно
var createRoomForm = document.getElementById("createRoomForm");
createRoomForm.onsubmit = async function(event) {
    event.preventDefault();
    // Получаем данные из формы
    var roomName = document.getElementById("roomName").value;
    var userId = 6; // Замените на реальный ID пользователя (можно получить из токена или сессии)
    try {
        const response = await fetch("api_v1/chat/create-room", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                name: roomName,
                user_id: userId, // Передаём ID пользователя
            }),
        });
        if (!response.ok) {
            throw new Error("Ошибка при создании комнаты");
        }
        const result = await response.json();
        alert(result.message); // Показываем сообщение от сервера
        // Закрываем модальное окно после успешного создания
        //modal.style.display = "none";
        // Обновляем список комнат (если нужно)
        // Например, можно вызвать функцию для загрузки списка комнат
        //loadRooms();
    } catch (error) {
        console.error("Ошибка:", error);
        alert("Не удалось создать комнату");
    }
};