// Variables globales
let accessGranted = false;
let lastReply = "";

// --- Acceso con código secreto ---
document.getElementById("btn-access").addEventListener("click", () => {
    const code = document.getElementById("access-code").value.trim();
    // Ejemplo simple: compara con "MAYROGA123" (más adelante puedes usar users.json)
    if (code === "MAYROGA123") {
        accessGranted = true;
        document.getElementById("access-section").style.display = "none";
        document.getElementById("services-section").style.display = "block";
        document.getElementById("chat-section").style.display = "block";
    } else {
        document.getElementById("access-msg").innerText = "Código incorrecto, inténtalo de nuevo.";
    }
});

// --- Selección de servicios ---
document.querySelectorAll(".btn-service").forEach(btn => {
    btn.addEventListener("click", async () => {
        const service = btn.dataset.service;
        alert(`Servicio seleccionado: ${service}. Próximamente se integrará el pago con Stripe.`);
        // Aquí más adelante se puede abrir Stripe Checkout
    });
});

// --- Enviar mensaje al asistente ---
document.getElementById("btn-send").addEventListener("click", async () => {
    if (!accessGranted) return;
    const message = document.getElementById("user-message").value.trim();
    if (!message) return;

    // Mostrar mensaje del usuario
    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML += `<div class="user-msg"><strong>Tú:</strong> ${message}</div>`;

    // Llamada al endpoint /api/chat
    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });
        const data = await res.json();
        if (data.reply) {
            lastReply = data.reply;
            chatBox.innerHTML += `<div class="bot-msg"><strong>May Roga:</strong> ${data.reply}</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
        } else if (data.error) {
            chatBox.innerHTML += `<div class="bot-msg error">${data.error}</div>`;
        }
    } catch (err) {
        chatBox.innerHTML += `<div class="bot-msg error">Error al conectar con el servidor.</div>`;
        console.error(err);
    }

    document.getElementById("user-message").value = "";
});

// --- Botón Text-to-Speech ---
document.getElementById("btn-tts").addEventListener("click", () => {
    if (!lastReply) return;
    const utterance = new SpeechSynthesisUtterance(lastReply);
    speechSynthesis.speak(utterance);
});
