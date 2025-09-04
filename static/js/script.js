// --- Variables globales ---
let lastReply = "";
const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const ttsBtn = document.getElementById("btn-tts");
const userId = localStorage.getItem("userId") || `user_${Date.now()}`;
localStorage.setItem("userId", userId);

// --- Función para agregar mensajes al chat ---
function addMessage(message, sender="user", isError=false) {
    const p = document.createElement("p");
    p.textContent = message;
    p.className = sender === "user" ? "user-msg" : "bot-msg";
    if(isError) p.classList.add("error");
    chatBox.appendChild(p);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// --- Enviar mensaje ---
async function sendMessage() {
    const message = userInput.value.trim();
    if(!message) return;
    addMessage(message, "user");
    userInput.value = "";

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ userId, message })
        });
        const data = await response.json();

        if(response.status === 429) {
            addMessage(data.error || "Límite alcanzado, intenta de nuevo.", "bot", true);
        } else if(data.reply) {
            addMessage(data.reply, "bot");
            lastReply = data.reply;
        } else if(data.error) {
            addMessage(data.error, "bot", true);
        } else {
            addMessage("Error inesperado, inténtalo más tarde.", "bot", true);
        }
    } catch (err) {
        addMessage("No se pudo conectar con el servidor.", "bot", true);
        console.error(err);
    }
}

// --- Evento botón enviar ---
sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (e) => {
    if(e.key === "Enter") sendMessage();
});

// --- Texto a voz ---
ttsBtn.addEventListener("click", () => {
    if(!lastReply) return;
    const utterance = new SpeechSynthesisUtterance(lastReply);
    utterance.lang = 'es-ES';
    speechSynthesis.speak(utterance);
});

// --- Mostrar mensaje inicial ---
addMessage("Bienvenido al Asistente May Roga. Escribe tu mensaje y presiona enviar.", "bot");
