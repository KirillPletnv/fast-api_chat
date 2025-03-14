document.addEventListener('DOMContentLoaded', function() {
    const userItems = document.querySelectorAll('.user-item');
    const messageInput = document.querySelector('.message-input');
    const chatHistory = document.querySelector('.chat-history');
    const selectChatMessage = document.querySelector('.select-chat-message');
    const selectedUser = document.querySelector('.selected-user');
    const input = document.querySelector('.message-input input');
    const sendButton = document.querySelector('.message-input button');
    const logoutButton = document.querySelector('.logout-btn');

    // Chat histories for each user
    const chatHistories = {
        'John Doe': [
            { type: 'received', text: 'Hey, how are you?' },
            { type: 'sent', text: 'I\'m good, thanks! How about you?' },
            { type: 'received', text: 'Great! Would you like to grab lunch?' }
        ],
        'Jane Smith': [
            { type: 'received', text: 'Did you finish the project?' },
            { type: 'sent', text: 'Yes, I just sent it to you' },
            { type: 'received', text: 'Perfect, thanks!' }
        ],
        'Mike Johnson': [
            { type: 'sent', text: 'Are we still meeting today?' },
            { type: 'received', text: 'Yes, at 3 PM' },
            { type: 'sent', text: 'Great, see you then!' }
        ],
        'Sarah Williams': [
            { type: 'received', text: 'Happy Birthday!' },
            { type: 'sent', text: 'Thank you so much!' },
            { type: 'received', text: 'Hope you have a great day!' }
        ],
        'David Brown': [
            { type: 'sent', text: 'Can you send me those files?' },
            { type: 'received', text: 'Sure, sending them now' },
            { type: 'sent', text: 'Got them, thanks!' }
        ]
    };

    function displayChatHistory(userName) {
        chatHistory.innerHTML = ''; // Clear current chat history
        const messages = chatHistories[userName];
        if (messages) {
            messages.forEach(message => {
                const messageElement = document.createElement('div');
                messageElement.classList.add('message', message.type);
                messageElement.textContent = message.text;
                chatHistory.appendChild(messageElement);
            });
        }
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    userItems.forEach(item => {
        item.addEventListener('click', function() {
            const userName = this.textContent;
            
            userItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
            
            // Show selected user name
            selectedUser.textContent = `Чат с ${userName}`;
            selectedUser.style.display = 'block';
            
            // Show chat history and message input, hide select message
            chatHistory.style.display = 'block';
            messageInput.style.display = 'flex';
            selectChatMessage.style.display = 'none';

            // Display chat history for selected user
            displayChatHistory(userName);
        });
    });

    function sendMessage() {
        const message = input.value.trim();
        if (message) {
            const activeUser = document.querySelector('.user-item.active');
            if (activeUser) {
                const userName = activeUser.textContent;
                
                // Add message to chat history array
                if (!chatHistories[userName]) {
                    chatHistories[userName] = [];
                }
                chatHistories[userName].push({ type: 'sent', text: message });
                
                // Create and display message element
                const messageElement = document.createElement('div');
                messageElement.classList.add('message', 'sent');
                messageElement.textContent = message;
                chatHistory.appendChild(messageElement);
                
                input.value = '';
                chatHistory.scrollTop = chatHistory.scrollHeight;
            }
        }
    }

    sendButton.addEventListener('click', sendMessage);
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    logoutButton.addEventListener('click', async function() {
        const response = await fetch(
            '/api_v1/auth/logout/',
            {
                method: 'POST'
                // ,
                // headers: {"Content-Type": "application/json"},
                // body: JSON.stringify({
                //     email: email.value,
                //     password: password.value,
                //     password_check: confirmPassword.value,
                //     name: name.value
                //   })
            }
        );
        window.location.href = '/chat'

        // const result = await response.json();
        
        // if (response.ok) {
        //     document.getElementById('registrationForm').reset();
        //     window.location.href = '/chat/login'
        // } else {
        //     alert(result.message || result.detail || 'Ошибка выполнения запроса')
        // }

        // window.location.href = "login.html";
    });
});