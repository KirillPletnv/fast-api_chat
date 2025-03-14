document.getElementById('registerButton').addEventListener(
    'click',
    submitForm
)
async function submitForm(event) {
    event.preventDefault();

    let isValid = true;
    const name = document.getElementById('name');
    const email = document.getElementById('email');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirmPassword');

    // Reset errors
    document.querySelectorAll('.error').forEach(error => error.style.display = 'none');

    // Validate name
    if (name.value.length < 1) {
        document.getElementById('nameError').style.display = 'block';
        name.parentElement.classList.add('shake');
        setTimeout(() => name.parentElement.classList.remove('shake'), 500);
        isValid = false;
    }

    // Validate email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.value)) {
        document.getElementById('emailError').style.display = 'block';
        email.parentElement.classList.add('shake');
        setTimeout(() => email.parentElement.classList.remove('shake'), 500);
        isValid = false;
    }

    // Validate password
    if (password.value.length < 8) {
        document.getElementById('passwordError').style.display = 'block';
        password.parentElement.classList.add('shake');
        setTimeout(() => password.parentElement.classList.remove('shake'), 500);
        isValid = false;
    }

    // Validate password confirmation
    if (password.value !== confirmPassword.value) {
        document.getElementById('confirmPasswordError').style.display = 'block';
        confirmPassword.parentElement.classList.add('shake');
        setTimeout(() => confirmPassword.parentElement.classList.remove('shake'), 500);
        isValid = false;
    }

    if (isValid) {
        
        const response = await fetch(
            '/api_v1/auth/register/',
            {
                method: 'POST',
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    email: email.value,
                    password: password.value,
                    password_check: confirmPassword.value,
                    name: name.value
                  })
            }
        );

        const result = await response.json();
        
        if (response.ok) {
            document.getElementById('registrationForm').reset();
            window.location.href = '/chat/login'
        } else {
            alert(result.message || result.detail || 'Ошибка выполнения запроса')
        }
        // const successMessage = document.getElementById('successMessage');
        // successMessage.style.display = 'block';
        // document.getElementById('registrationForm').reset();

        // Simulate form submission
        // setTimeout(() => {
        //     successMessage.style.display = 'none';
        // }, 3000);
    }

    // return false;
}