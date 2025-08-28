const chatForm = document.getElementById("chat-form");
const chatMessages = document.getElementById("chat-messages");

const accesoDirecto = document.getElementById("acceso-directo");
const pagarStripe = document.getElementById("pagar-stripe");

let apodo = "";
let servicio = "";
let acceso = false;

accesoDirecto.addEventListener("click", () => {
    const inputApodo = document.getElementById("apodo").value;
    const code = document.getElementById("code").value;
    if (!inputApodo || !code) return alert("Ingresa apodo y código");

    fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        body: `apodo=${inputApodo}&servicio=medico&mensaje=Hola&code=${code}`
    }).then(res => res.json()).then(data => {
        if (data.respuesta.includes("Acceso denegado")) alert(data.respuesta);
        else {
            apodo = inputApodo;
            servicio = "medico";
            acceso = true;
            alert("Acceso concedido!");
        }
    });
});

pagarStripe.addEventListener("click", async () => {
    const inputApodo = document.getElementById("apodo-pago").value;
    const selServicio = document.getElementById("servicio").value;
    if (!inputApodo) return alert("Ingresa tu apodo");

    const res = await fetch("/crear-sesion-stripe", {
        method: "POST",
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        body: `apodo=${inputApodo}&servicio=${selServicio}`
    });
    const data = await res.json();
    if (data.error) return alert(data.error);

    const stripe = Stripe("pk_live_51NqPxQBOA5mT4t0PEoRVRc0Sj7DugiHvxhozC3BYh0q0hAx1N3HCLJe4xEp3MSuNMA6mQ7fAO4mvtppqLodrtqEn00pgJNQaxz");
    stripe.redirectToCheckout({ sessionId: data.id });
});

chatForm.addEventListener("submit", async e => {
    e.preventDefault();
    if (!acceso) return alert("Debes pagar o usar un código válido");

    const mensaje = document.getElementById("mensaje").value;
    if (!mensaje) return;

    chatMessages.innerHTML += `<b>${apodo}:</b> ${mensaje}<br>`;

    const formData = new URLSearchParams();
    formData.append("apodo", apodo);
    formData.append("servicio", servicio);
    formData.append("mensaje", mensaje);

    const res = await fetch("/chat", {
        method: "POST",
        body: formData
    });
    const data = await res.json();
    chatMessages.innerHTML += `<b>Asistente:</b> ${data.respuesta}<br>`;
    chatMessages.scrollTop = chatMessages.scrollHeight;
    document.getElementById("mensaje").value = "";
});

document.getElementById("limpiar-chat").addEventListener("click", () => {
    chatMessages.innerHTML = "";
});
