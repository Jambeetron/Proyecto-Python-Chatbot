document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const usernameField = document.querySelector('#id_username');
    const emailField = document.querySelector('#id_email');
    const password1Field = document.querySelector('#id_password1');
    const password2Field = document.querySelector('#id_password2');
    const feedback = document.querySelector('#feedback'); // Contenedor para errores en tiempo real

    // Mostrar errores del servidor en una alerta
    const serverErrorsElement = document.querySelector('#server-errors');
    if (serverErrorsElement) {
        const serverErrors = JSON.parse(serverErrorsElement.getAttribute('data-errors'));
        if (serverErrors.length > 0) {
            alert(`Errores del servidor:\n${serverErrors.join('\n')}`);
        }
    }

    // Validación en tiempo real para username
    usernameField.addEventListener('blur', function () {
        const username = usernameField.value.trim();
        if (username) {
            fetch(`/check-username/?username=${username}`)
                .then(response => response.json())
                .then(data => {
                    if (data.exists) {
                        feedback.textContent = "El nombre de usuario ya está en uso.";
                    } else {
                        feedback.textContent = "";
                    }
                });
        }
    });

    // Validación en tiempo real para email
    emailField.addEventListener('blur', function () {
        const email = emailField.value.trim();
        if (email) {
            fetch(`/check-email/?email=${email}`)
                .then(response => response.json())
                .then(data => {
                    if (data.exists) {
                        feedback.textContent = "El correo electrónico ya está registrado.";
                    } else {
                        feedback.textContent = "";
                    }
                });
        }
    });

    // Validación al enviar el formulario
    form.addEventListener('submit', function (event) {
        let errors = [];

        // Validar el campo de usuario
        if (usernameField.value.trim() === '') {
            errors.push("El campo 'Usuario' no puede estar vacío.");
        }

        // Validar el correo electrónico
        if (emailField.value.trim() === '') {
            errors.push("El campo 'Correo Electrónico' no puede estar vacío.");
        }

        // Validar contraseñas
        if (password1Field.value.trim() === '') {
            errors.push("El campo 'Contraseña' no puede estar vacío.");
        }
        if (password2Field.value.trim() === '') {
            errors.push("El campo 'Confirmar Contraseña' no puede estar vacío.");
        }
        if (password1Field.value !== password2Field.value) {
            errors.push("Las contraseñas no coinciden.");
        }

        // Mostrar errores si los hay
        if (errors.length > 0) {
            event.preventDefault(); // Evitar que el formulario se envíe
            alert(`Errores de validación:\n${errors.join('\n')}`);
        }
    });

    // Mostrar/ocultar contraseñas
    document.querySelectorAll('.toggle-password').forEach((button) => {
        button.addEventListener('click', () => {
            const target = document.querySelector(button.getAttribute('data-target'));
            if (target.type === 'password') {
                target.type = 'text';
                button.textContent = 'Ocultar contraseña';
            } else {
                target.type = 'password';
                button.textContent = 'Visualizar contraseña';
            }
        });
    });
});
