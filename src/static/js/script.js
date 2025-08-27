document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("chat-form");
    const inputMessage = document.getElementById("message");
    const chatBox = document.getElementById("chat-box");
    const nickname = document.getElementById("nickname");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        if (!nickname.value.trim()) {
            alert("Ingresa tu apodo primero.");
            return;
        }

        const message = inputMessage.value.trim();
        if (!message) return;

        // Mostrar mensaje del usuario en la pantalla
        const userMsg = document.createElement("div");
        userMsg.className = "user-message";
        userMsg.textContent = `Tú: ${message}`;
        chatBox.appendChild(userMsg);

        inputMessage.value = "";
        chatBox.scrollTop = chatBox.scrollHeight;

        // Enviar mensaje al backend
        try {
            const resp = await fetch("/api/message", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({nickname: nickname.value, message})
            });
            const data = await resp.json();

            const replyMsg = document.createElement("div");
            replyMsg.className = "bot-message";
            replyMsg.textContent = data.reply ? `Asistente: ${data.reply}` : `Error: ${data.error}`;
            chatBox.appendChild(replyMsg);
            chatBox.scrollTop = chatBox.scrollHeight;

        } catch (err) {
            console.error(err);
            const errorMsg = document.createElement("div");
            errorMsg.className = "bot-message";
            errorMsg.textContent = "Error al enviar mensaje.";
            chatBox.appendChild(errorMsg);
        }
    });
});
