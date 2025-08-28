const payBtn = document.getElementById("pay");
const nicknameInput = document.getElementById("nickname");
const serviceSelect = document.getElementById("service");
const chatContainer = document.getElementById("chat-container");
const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send");
const clearBtn = document.getElementById("clear");

payBtn.addEventListener("click", async () => {
    const nickname = nicknameInput.value.trim();
    const service = serviceSelect.value;
    if (!nickname) return alert("Debes ingresar un apodo");

    try {
        const formData = new FormData();
        formData.append("nickname", nickname);
        formData.append("service", service);

        const res = await fetch("/create-checkout-session", {
            method: "POST",
            body: formData
        });
        const data = await res.json();
        if (data.url) {
            window.location.href = data.url;
        } else {
            alert("Error creando sesión de pago: " + (data.error || "desconocido"));
        }
    } catch (err) {
        alert("Error en pago: " + err);
    }
});

sendBtn.addEventListener("click", async () => {
    const message = userInput.value.trim();
    if (!message) return;
    const nickname = nicknameInput.value.trim();
    const service = serviceSelect.value;

    chatBox.innerHTML += `<p><strong>${nickname}:</strong> ${message}</p>`;
    userInput.value = "";

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message, nickname, service})
        });
        const data = await res.json();
        chatBox.innerHTML += `<p><strong>Asistente:</strong> ${data.reply}</p>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (err) {
        chatBox.innerHTML += `<p style="color:red;">Error: ${err}</p>`;
    }
});

clearBtn.addEventListener("click", () => {
    chatBox.innerHTML = "";
});
