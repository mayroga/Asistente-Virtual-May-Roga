// static/js/script.js

document.addEventListener("DOMContentLoaded", () => {
    const startBtn = document.getElementById("start");
    const nicknameInput = document.getElementById("nickname");
    const serviceSelect = document.getElementById("service");
    const chatContainer = document.getElementById("chat-container");
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send");
    const clearBtn = document.getElementById("clear");
    const payBtn = document.getElementById("pay");

    let apodo = "";
    let service = "";

    startBtn.addEventListener("click", () => {
        apodo = nicknameInput.value.trim();
        service = serviceSelect.value;

        if (!apodo) {
            alert("Debes ingresar un apodo.");
            return;
        }

        chatContainer.style.display = "block";
        startBtn.disabled = true;
        nicknameInput.disabled = true;
        serviceSelect.disabled = true;
        appendMessage("Sistema", `Acceso concedido para ${apodo}. Selecciona un servicio y realiza el pago para iniciar.`);
    });

    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });

    clearBtn.addEventListener("click", () => {
        chatBox.innerHTML = "";
    });

    payBtn.addEventListener("click", async () => {
        // Tomamos el precio del servicio seleccionado
        const price = parseFloat(serviceSelect.selectedOptions[0].text.split("$")[1]);
        try {
            const res = await fetch("/create-payment-intent", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: new URLSearchParams({ amount: price })
            });
            const data = await res.json();
            if (data.client_secret) {
                alert("Pago simulado: cliente listo para pagar con Stripe (client_secret recibido).");
            } else {
                alert("Error al crear Payment Intent: " + data.error);
            }
        } catch (err) {
            alert("Error en pago: " + err);
        }
    });

    async function sendMessage() {
        const msg = userInput.value.trim();
        if (!msg) return;
        appendMessage(apodo, msg);
        userInput.value = "";

        try {
            const res = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: msg, nickname: apodo, service: service })
            });
            const data = await res.json();
            appendMessage("Asistente", data.reply);
        } catch (err) {
            appendMessage("Sistema", "Error al enviar el mensaje: " + err);
        }
    }

    function appendMessage(sender, msg) {
        const div = document.createElement("div");
        div.innerHTML = `<strong>${sender}:</strong> ${msg}`;
        chatBox.appendChild(div);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});
