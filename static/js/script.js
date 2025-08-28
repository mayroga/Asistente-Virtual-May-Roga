const chatForm = document.getElementById("chat-form");
const chatMessages = document.getElementById("chat-messages");
const limpiarBtn = document.getElementById("limpiar-chat");
const accesoBtn = document.getElementById("acceso-directo");
const pagarBtn = document.getElementById("pagar-stripe");
const stripe = Stripe("pk_live_51NqPxQBOA5mT4t0PEoRVRc0Sj7DugiHvxhozC3BYh0q0hAx1N3HCLJe4xEp3uNMA6mQ7fAO4mvtppqLodrtqEn00pgJNQaxz");

let usuario = "";
let servicioActivo = "";

// Acceso directo gratis
accesoBtn.addEventListener("click", () => {
    const apodo = document.getElementById("apodo").value;
    const code = document.getElementById("code").value;
    if(apodo && code){
        usuario = apodo;
        servicioActivo = "respuesta_rapida";
        alert(`Acceso concedido para ${usuario}`);
    } else {
        alert("Apodo y código obligatorios.");
    }
});

// Pago Stripe
pagarBtn.addEventListener("click", async () => {
    const apodo = document.getElementById("apodo-pago").value;
    const servicio = document.getElementById("servicio").value;
    if(!apodo){ alert("Ingresa tu apodo"); return; }
    usuario = apodo;
    servicioActivo = servicio;

    const res = await fetch("/create-checkout-session", {
        method: "POST",
        body: new URLSearchParams({apodo, service: servicio})
    });
    const data = await res.json();
    stripe.redirectToCheckout({sessionId: data.id});
});

// Enviar mensaje
chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const mensaje = document.getElementById("mensaje").value;
    if(!usuario || !servicioActivo){ alert("Primero accede o paga el servicio"); return; }

    chatMessages.innerHTML += `<b>${usuario}:</b> ${mensaje}<br>`;
    const formData = new URLSearchParams({apodo: usuario, service: servicioActivo, message: mensaje});
    const res = await fetch("/chat", {method:"POST", body: formData});
    const data = await res.json();
    chatMessages.innerHTML += `<b>Agente:</b> ${data.reply}<br>`;
    chatMessages.scrollTop = chatMessages.scrollHeight;
    document.getElementById("mensaje").value = "";
});

// Limpiar chat
limpiarBtn.addEventListener("click", () => chatMessages.innerHTML = "");
