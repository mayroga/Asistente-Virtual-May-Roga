let pagoConfirmado = false;
const stripePublicKey = "pk_live_51NqPxQBOA5mT4t0PEoRVRc0Sj7DugiHvxhozC3BYh0q0hAx1N3HCLJe4xEp3uNMA6mQ7fAO4mvtppqLodrtqEn00pgJNQaxz";
const stripe = Stripe(stripePublicKey);

document.getElementById("acceso-directo").addEventListener("click", () => {
    const apodo = document.getElementById("apodo").value;
    const code = document.getElementById("code").value;
    if (!apodo || !code) { alert("Llena apodo y código"); return; }
    pagoConfirmado = true;
    document.getElementById("pago-confirmado").value = "true";
    alert(`Acceso concedido para ${apodo}`);
});

document.getElementById("pagar-stripe").addEventListener("click", async () => {
    const apodo = document.getElementById("apodo-pago").value;
    const service = document.getElementById("servicio").value;
    if (!apodo) { alert("Escribe tu apodo"); return; }

    let price = 0;
    if (service === "agente_rapido") price = 100; // $1 en centavos
    else if (service === "risoterapia") price = 1200;
    else if (service === "horoscopo") price = 300;

    try {
        const res = await fetch("/create-checkout-session", {
            method: "POST",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify({price, service, apodo})
        });
        const data = await res.json();
        const result = await stripe.redirectToCheckout({ sessionId: data.id });
        if (result.error) alert(result.error.message);
    } catch(e) { alert(e); }
});

document.getElementById("chat-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const apodo = document.getElementById("apodo").value || document.getElementById("apodo-pago").value;
    const service = document.getElementById("servicio").value;
    const message = document.getElementById("mensaje").value;
    if (!apodo || !message) return;

    const responseDiv = document.getElementById("chat-messages");
    responseDiv.innerHTML += `<b>${apodo}:</b> ${message}<br>`;
    document.getElementById("mensaje").value = "";

    try {
        const res = await fetch("/chat", {
            method: "POST",
            body: new URLSearchParams({
                apodo,
                service,
                message,
                pago_confirmado: pagoConfirmado ? "true" : "false",
                code: document.getElementById("code").value
            })
        });
        const data = await res.json();
        responseDiv.innerHTML += `<b>Agente:</b> ${data.response}<br>`;
        responseDiv.scrollTop = responseDiv.scrollHeight;
    } catch(e) {
        responseDiv.innerHTML += `<b>Agente:</b> Error: ${e}<br>`;
    }
});

document.getElementById("limpiar-chat").addEventListener("click", () => {
    document.getElementById("chat-messages").innerHTML = "";
});
