function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener("DOMContentLoaded", function () {
    const chat = document.getElementById("chat");
    if (!chat.hasChildNodes()) {
        const noMensajes = document.createElement("div");
        noMensajes.id = "no-mensajes";
        noMensajes.textContent = "No hay mensajes previos.";
        chat.appendChild(noMensajes);
    }
});

// Evento al presionar el botón "Enviar"
document.getElementById("enviar").addEventListener("click", function () {
    const mensaje = document.getElementById("mensaje").value.trim();

    if (!mensaje) {
        alert("Por favor, escribe un mensaje.");
        return;
    }

    fetch("/procesar_mensaje/", {
        method: "POST",
        body: JSON.stringify({ mensaje }),
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.respuesta) {
                agregarMensaje(data.usuario, mensaje);
                agregarMensaje("bot", data.respuesta); // Agrega la respuesta del bot
            } else {
                agregarMensaje("bot", "Hubo un problema al procesar tu mensaje. Inténtalo nuevamente.");
            }
        })
        .catch((error) => {
            agregarMensaje("bot", "Hubo un error al enviar el mensaje.");
            console.error("Error:", error);
        });

    document.getElementById("mensaje").value = ""; // Limpia el campo de texto
});

// Función para agregar mensajes al chat
function agregarMensaje(remitente, mensaje) {
    const chat = document.getElementById("chat");
    const noMensajes = document.getElementById("no-mensajes");

    // Elimina el mensaje de "No hay mensajes previos" si existe
    if (noMensajes) {
        noMensajes.remove();
    }

    const nuevoMensaje = document.createElement("div");
    nuevoMensaje.className = remitente === "usuario" ? "usuario" : "bot";
    nuevoMensaje.innerHTML = `<strong>${remitente.toUpperCase()}:</strong> ${mensaje}`;
    chat.appendChild(nuevoMensaje); // Añade al final del chat
    chat.scrollTop = chat.scrollHeight; // Desplaza hacia el final del chat
}

document.querySelector(".btn-danger").addEventListener("click", function (event) {
    if (!confirm("¿Estás seguro de que deseas borrar todos los mensajes?")) {
        event.preventDefault();
    }
});
