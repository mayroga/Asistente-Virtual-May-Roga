const accesoBtn = document.getElementById("acceso-directo");
const pagoBtn = document.getElementById("pagar-stripe");
const chatForm = document.getElementById("chat-form");
const chatMessages = document.getElementById("chat-messages");
let apodoActivo = null;
let servicioActivo = null;
let stripe = Stripe("TU_STRIPE_PUBLIC_KEY"); // reemplaza por tu public key

// Acceso gratis
accesoBtn.onclick = async () => {
    const apodo = document.getElementById("apodo").value;
    const code = document.getElementById("code").value;
    const res = await fetch("/acceso-gratis", {
        method: "POST",
        body: new URLSearchParams({apodo, code})
    });
    const data = await res.json();
    document.getElementById("acceso-mensaje").innerText = data.mensaje;
    if(data.status === "ok") apodoActivo = apodo;
};

// Pago Stripe
pagoBtn.onclick = async () => {
    const apodo = document.getElementById("apodo-pago").value;
    const servicio = document.getElementById("servicio").value;
    const res = await fetch("/create-payment-intent", {
        method: "POST",
        body: new URLSearchParams({apodo, servicio})
    });
    const data = await res.json();
    const {error, client_secret} = data;
    if(error) { document.getElementById("pago-mensaje").innerText = error; return; }

    const result = await stripe.confirmCardPayment(client_secret, {
        payment_method: {
            card: {
                // Aquí debes usar un elemento de Stripe real para tarjeta
            }
        }
    });

    if(result.error){
        document.getElementById("pago-mensaje").innerText = result.error.message;
    } else {
        if(result.paymentIntent.status === 'succeeded'){
            await fetch("/confirm-payment", {method:"POST", body: new URLSearchParams({apodo})});
            document.getElementById("pago-mensaje").innerText = "Pago confirmado.";
            apodoActivo = apodo;
            servicioActivo = servicio;
        }
    }
};

// Chat
chatForm.onsubmit = async (e) => {
    e.preventDefault();
    if(!apodoActivo) { alert("Debes tener acceso por pago o código secreto."); return; }
    const mensaje = document.getElementById("mensaje").value;
    chatMessages.innerHTML += `<p><strong>${apodoActivo}:</strong> ${mensaje}</p>`;
    const res = await fetch("/chat", {
        method:"POST",
        body: new URLSearchParams({apodo: apodoActivo, servicio: servicioActivo, mensaje})
    });
    const data = await res.json();
    chatMessages.innerHTML += `<p><strong>Asistente:</strong> ${data.respuesta}</p>`;
    chatMessages.scrollTop = chatMessages.scrollHeight;
    document.getElementById("mensaje").value = "";
};

// Limpiar chat
document.getElementById("limpiar-chat").onclick = () => {
    chatMessages.innerHTML = "";
};
