const chatForm = document.getElementById("chat-form");
const chatMessages = document.getElementById("chat-messages");
const limpiarChatBtn = document.getElementById("limpiar-chat");

let pagoConfirmado = false;

// Manejar chat
chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const apodo = document.getElementById("apodo-pago").value || document.getElementById("apodo").value;
    const mensaje = document.getElementById("mensaje").value;
    const servicio = document.getElementById("servicio").value;
    const codigo = document.getElementById("code")?.value || "";

    if (!apodo) {
        alert("Ingresa tu apodo");
        return;
    }

    const formData = new FormData();
    formData.append("apodo", apodo);
    formData.append("mensaje", mensaje);
    formData.append("servicio", servicio);
    formData.append("codigo", codigo);
    formData.append("pago_confirmado", pagoConfirmado);

    const response = await fetch("/chat", {
        method: "POST",
        body: formData
    });

    const data = await response.json();
    chatMessages.innerHTML += `<p><b>${apodo}:</b> ${mensaje}</p>`;
    chatMessages.innerHTML += `<p><b>Asistente:</b> ${data.respuesta}</p>`;
    chatMessages.scrollTop = chatMessages.scrollHeight;
    chatForm.reset();
});

// Limpiar chat
limpiarChatBtn.addEventListener("click", () => {
    chatMessages.innerHTML = "";
});

// Acceso directo con código secreto
document.getElementById("acceso-directo").addEventListener("click", () => {
    const codigo = document.getElementById("code").value;
    const apodo = document.getElementById("apodo").value;
    if (codigo && apodo) {
        pagoConfirmado = true;
        alert("Acceso concedido para " + apodo);
    } else {
        alert("Ingresa apodo y código secreto.");
    }
});

// Pago con Stripe (simulado para Render)
document.getElementById("pagar-stripe").addEventListener("click", async () => {
    const apodo = document.getElementById("apodo-pago").value;
    const servicio = document.getElementById("servicio").value;
    if (!apodo) { alert("Ingresa tu apodo"); return; }

    const formData = new FormData();
    formData.append("apodo", apodo);
    formData.append("servicio", servicio);

    const response = await fetch("/create-checkout-session", {
        method: "POST",
        body: formData
    });

    const data = await response.json();
    if (data.id) {
        pagoConfirmado = true;
        alert("Pago simulado. Ahora puedes usar el chat.");
    } else {
        alert("Error al crear sesión de pago: " + data.error);
    }
});
