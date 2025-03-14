document.getElementById('loginButton').addEventListener(
    'click',
    submitForm
)

async function submitForm(event) {
    event.preventDefault();

    let isValid = true;
    const email = document.getElementById('email');
    const password = document.getElementById('password');

    // Reset errors
    document.querySelectorAll('.error').forEach(error => error.style.display = 'none');

    // Validate email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.value)) {
        document.getElementById('emailError').style.display = 'block';
        email.parentElement.classList.add('shake');
        setTimeout(() => email.parentElement.classList.remove('shake'), 500);
        isValid = false;
    }

    // Validate password
    if (password.value.length < 1) {
        document.getElementById('passwordError').style.display = 'block';
        password.parentElement.classList.add('shake');
        setTimeout(() => password.parentElement.classList.remove('shake'), 500);
        isValid = false;
    }

    if (isValid) {
        const response = await fetch(
            '/api_v1/auth/login/',
            {
                method: 'POST',
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    email: email.value,
                    password: password.value
                  })
            }
        );

        const result = await response.json();
        
        if (response.ok) {
            document.getElementById('loginForm').reset();
            window.location.href = '/chat'
        } else {
            alert(result.message || result.detail || 'Ошибка выполнения запроса')
        }
        // Redirect to chat page
        // window.location.href = "https://chat.example.com";
    }

    // return false;
}