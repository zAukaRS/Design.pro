document.addEventListener('DOMContentLoaded', function () {
    const emailInput = document.getElementById('id_email');
    const emailError = document.getElementById('email-error');

    emailInput.addEventListener('input', function () {
        const email = emailInput.value;

        if (email) {
            fetch(`/check-email/?email=${encodeURIComponent(email)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.exists) {
                        emailError.textContent = "Этот email уже зарегистрирован.";
                        emailError.style.color = "red";
                    } else {
                        emailError.textContent = "";
                    }
                })
                .catch(error => {
                    console.error('Ошибка при проверке email:', error);
                });
        } else {
            emailError.textContent = "";
        }
    });
});