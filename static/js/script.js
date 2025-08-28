// static/js/script.js

let apodoActual = "";
let accesoGratisActivo = false;

function accesoGratis() {
    const apodo = document.getElementById("free-apodo").value;
    const code = document.getElementById("free-code").value;
    if (!apodo || !code) {
        alert("Apodo y código son obligatorios");
        return;
    }
    apodoActual = apodo;
    accesoGratisActivo = true;
    document.getElementById("chat-apodo").innerText = apodoActual;
    document.getElementById("chat-section").style.display = "block";
    document.getElementById("free-status").innerText = "Acceso concedido para " + apodo;
}

function pagarStripe() {
    const apodo = document.getElementById("paid-apodo").value;
    const service = document.getElementById("service-select").value;
    if (!apodo) { alert("Apodo obligatorio"); return; }
    fetch("/create-checkout-session", {
        method: "POST",
        body: new URLSearchParams({ apodo: apodo, service: service })
    })
    .then(res => res.json())
    .then(data => {
        if (data.url) {
            window.location.href = data.url;
        } else {
            alert("Error al crear sesión de pago");
        }
    });
}

function enviarMensaje() {
    const mensaje = document.getElementById("chat-message").value;
    if (!mensaje) return;
    let payload = { apodo: apodoActual, mensaje: mensaje };
    if (accesoGratisActivo) payload.access_code = document.getElementById("free-code").value;
    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        const log = document.getElementById("chat-log");
        log.innerHTML += `<p>${apodoActual}: ${mensaje}</p>`;
        log.innerHTML += `<p>Asistente: ${data.respuesta}</p>`;
        log.scrollTop = log.scrollHeight;
        document.getElementById("chat-message").value = "";
    });
}

function limpiarChat() {
    document.getElementById("chat-log").innerHTML = "";
}
