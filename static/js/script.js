document.addEventListener("DOMContentLoaded", function () {
    const chatForm = document.getElementById("chat-form");
    const chatMessages = document.getElementById("chat-messages");

    chatForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        const apodo = document.getElementById("apodo").value;
        const mensaje = document.getElementById("mensaje").value;
        const servicio = document.getElementById("servicio").value;
        const code = document.getElementById("code").value;
        const pagoConfirmado = document.getElementById("pago-confirmado")?.checked || false;

        if (!apodo || !mensaje) return;

        // Mostrar mensaje del usuario
        const userDiv = document.createElement("div");
        userDiv.classList.add("mensaje-usuario");
        userDiv.textContent = `${apodo}: ${mensaje}`;
        chatMessages.appendChild(userDiv);

        // Enviar a backend
        const formData = new FormData();
        formData.append("apodo", apodo);
        formData.append("mensaje", mensaje);
        formData.append("servicio", servicio);
        formData.append("code", code);
        formData.append("pago_confirmado", pagoConfirmado);

        const response = await fetch("/chat", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        const respDiv = document.createElement("div");
        respDiv.classList.add("mensaje-asistente");
        if (data.error) {
            respDiv.textContent = `Error: ${data.error}`;
        } else {
            respDiv.textContent = data.respuesta;
        }
        chatMessages.appendChild(respDiv);

        chatMessages.scrollTop = chatMessages.scrollHeight;
        document.getElementById("mensaje").value = "";
    });
});
