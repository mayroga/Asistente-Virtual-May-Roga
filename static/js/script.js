const apodoInput = document.getElementById("apodo");
const codeInput = document.getElementById("code");
const accesoBtn = document.getElementById("acceso-directo");

const apodoPagoInput = document.getElementById("apodo-pago");
const servicioSelect = document.getElementById("servicio");
const pagarBtn = document.getElementById("pagar-stripe");

const chatForm = document.getElementById("chat-form");
const mensajeInput = document.getElementById("mensaje");
const chatMessages = document.getElementById("chat-messages");

let usuarioActual = null;
let servicioActual = null;
let accesoValido = false;

// Acceso por código secreto
accesoBtn.addEventListener("click", () => {
    const apodo = apodoInput.value.trim();
    const code = codeInput.value.trim();
    if (!apodo || !code) { alert("Apodo y código obligatorios"); return; }
    usuarioActual = apodo;
    servicioActual = "agente_rapido";
    accesoValido = true;
    alert(`Acceso concedido para ${apodo}`);
});

// Acceso por pago (Stripe)
pagarBtn.addEventListener("click", async () => {
    const apodo = apodoPagoInput.value.trim();
    const servicio = servicioSelect.value;
    if (!apodo) { alert("Apodo obligatorio"); return; }
    try {
        const res = await fetch("/crear-checkout-session", {
            method: "POST",
            body: new URLSearchParams({ apodo, servicio })
        });
        const data = await res.json();
        window.location.href = data.url;
    } catch (err) {
        console.error(err);
        alert("Error al crear sesión de pago");
    }
});

// Enviar mensaje
chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!usuarioActual || !servicioActual) { alert("Acceso no autorizado"); return; }
    const mensaje = mensajeInput.value.trim();
    if (!mensaje) return;
    chatMessages.innerHTML += `<p><b>${usuarioActual}:</b> ${mensaje}</p>`;
    mensajeInput.value = "";

    try {
        const formData = new URLSearchParams();
        formData.append("apodo", usuarioActual);
        formData.append("servicio", servicioActual);
        formData.append("mensaje", mensaje);
        if (codeInput.value) formData.append("code", codeInput.value);

        const res = await fetch("/chat", { method: "POST", body: formData });
        const data = await res.json();
        chatMessages.innerHTML += `<p><b>Agente:</b> ${data.respuesta}</p>`;
        chatMessages.scrollTop = chatMessages.scrollHeight;
    } catch (err) {
        console.error(err);
        chatMessages.innerHTML += `<p><b>Agente:</b> Error al procesar la consulta</p>`;
    }
});

// Limpiar chat
document.getElementById("limpiar-chat").addEventListener("click", () => {
    chatMessages.innerHTML = "";
});
