let accessGranted = false;
let lastReply = "";

// Acceso
document.getElementById("btn-access").addEventListener("click", () => {
    const code = document.getElementById("access-code").value.trim();
    if (code === "MAYROGA123") {
        accessGranted = true;
        document.getElementById("access-section").style.display = "none";
        document.getElementById("services-section").style.display = "block";
        document.getElementById("chat-section").style.display = "block";
    } else {
        document.getElementById("access-msg").innerText = "Código incorrecto, inténtalo de nuevo.";
    }
});

// Inicializa Stripe
const stripePublicKey = "pk_test_XXXXXXXXXXXXXXXXXXXX"; // reemplaza con tu clave pública
const stripe = Stripe(stripePublicKey);

// Pagos
document.querySelectorAll(".btn-pay").forEach(btn => {
    btn.addEventListener("click", async () => {
        const service = btn.dataset.service;
        try {
            const res = await fetch("/create-checkout-session", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ serviceId: service })
            });
            const data = await res.json();
            if (data.id) {
                await stripe.redirectToCheckout({ sessionId: data.id });
            } else {
                alert("Error al crear sesión de pago.");
            }
        } catch (err) {
            console.error(err);
            alert("Error al conectar con el servidor.");
        }
    });
});

// Chat
document.getElementById("btn-send").addEventListener("click", async () => {
    if (!accessGranted) return;
    const message = document.getElementById("user-message").value.trim();
    if (!message) return;

    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML += `<div class="user-msg"><strong>Tú:</strong> ${message}</div>`;

    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });
        const data = await res.json();
        if (data.reply) {
            lastReply = data.reply;
            chatBox.innerHTML += `<div class="bot-msg"><strong>May Roga:</strong> ${data.reply}</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
        } else if (data.error) {
            chatBox.innerHTML += `<div class="bot-msg error">${data.error}</div>`;
        }
    } catch (err) {
        chatBox.innerHTML += `<div class="bot-msg error">Error al conectar con el servidor.</div>`;
        console.error
