// =============================
// Variables globales
// =============================
let CURRENT_TOKEN = null;
let CURRENT_NICKNAME = null;

// =============================
// Función para iniciar sesión
// =============================
async function startSession() {
    const nickname = document.getElementById("nickname").value.trim();
    const code = document.getElementById("code").value.trim();

    if (!nickname) {
        alert("Ingresa tu apodo");
        return;
    }

    const payload = { nickname, code };
    try {
        const res = await fetch("/api/start-session", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.token) {
            CURRENT_TOKEN = data.token;
            CURRENT_NICKNAME = nickname;
            alert("Sesión iniciada correctamente");
            document.getElementById("session-section").style.display = "none";
            document.getElementById("services-section").style.display = "block";
        } else if (data.requires_payment) {
            alert("Este apodo requiere pago. Selecciona un servicio para pagar.");
            CURRENT_NICKNAME = nickname;
            document.getElementById("session-section").style.display = "none";
            document.getElementById("services-section").style.display = "block";
        }
    } catch (err) {
        console.error(err);
        alert("Error iniciando sesión");
    }
}

// =============================
// Función para enviar mensaje al Asistente
// =============================
async function sendMessage(service) {
    const inputId = service + "-input";
    const outputId = service + "-output";
    const messageInput = document.getElementById(inputId);

    if (!messageInput.value.trim()) {
        alert("Escribe tu mensaje");
        return;
    }

    const payload = {
        token: CURRENT_TOKEN,
        message: messageInput.value.trim()
    };

    try {
        const res = await fetch("/api/message", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        document.getElementById(outputId).innerText = data.reply;
        messageInput.value = "";
    } catch (err) {
        console.error(err);
        alert("Error enviando mensaje");
    }
}

// =============================
// Función para iniciar pago
// =============================
async function payService(servicio, priceCents) {
    if (!CURRENT_NICKNAME) {
        alert("Debes iniciar sesión primero");
        return;
    }

    const url = `/pay/create-session?nickname=${CURRENT_NICKNAME}&servicio=${servicio}&price_cents=${priceCents}`;
    try {
        const res = await fetch(url);
        const data = await res.json();
        if (data.url) {
            window.location.href = data.url;
        } else {
            alert("Error creando sesión de pago");
        }
    } catch (err) {
        console.error(err);
        alert("Error iniciando pago");
    }
}

// =============================
// Función para Quickresponse
// =============================
async function quickResponse() {
    const code = document.getElementById("quick-code").value.trim();
    const nickname = document.getElementById("quick-nickname").value.trim();
    if (!nickname || !code) {
        alert("Ingresa tu apodo y código");
        return;
    }

    window.location.href = `/quickresponse?nickname=${nickname}&code=${code}`;
}

// =============================
// Event listeners
// =============================
document.getElementById("start-btn")?.addEventListener("click", startSession);
document.getElementById("asistente-btn")?.addEventListener("click", () => sendMessage("asistente"));
document.getElementById("risoterapia-btn")?.addEventListener("click", () => sendMessage("risoterapia"));
document.getElementById("horoscopo-btn")?.addEventListener("click", () => sendMessage("horoscopo"));
document.getElementById("pay-asistente")?.addEventListener("click", () => payService("asistente", 500));
document.getElementById("pay-risoterapia")?.addEventListener("click", () => payService("risoterapia", 1200));
document.getElementById("pay-horoscopo")?.addEventListener("click", () => payService("horoscopo", 300));
document.getElementById("quick-btn")?.addEventListener("click", quickResponse);

// =============================
// Responsive helpers
// =============================
window.addEventListener("resize", () => {
    const width = window.innerWidth;
    if (width < 600) {
        document.body.style.fontSize = "16px";
    } else if (width < 900) {
        document.body.style.fontSize = "18px";
    } else {
        document.body.style.fontSize = "20px";
    }
});
