document.addEventListener("DOMContentLoaded", () => {
    const chatForm = document.getElementById("chat-form");
    const chatMensajes = document.getElementById("chat-mensajes");
    const limpiarChat = document.getElementById("limpiar-chat");

    const accesoDirecto = document.getElementById("acceso-directo");
    const pagarStripe = document.getElementById("pagar-stripe");

    let apodoGlobal = "";
    let pagoConfirmado = false;
    let servicioSeleccionado = "";

    accesoDirecto.addEventListener("click", () => {
        const apodo = document.getElementById("apodo").value.trim();
        const codigo = document.getElementById("codigo").value.trim();
        if (!apodo || !codigo) { alert("Ingresa apodo y código."); return; }
        apodoGlobal = apodo;
        pagoConfirmado = false;
        servicioSeleccionado = "medico";  // default para acceso directo
        alert("Acceso concedido para " + apodoGlobal);
    });

    pagarStripe.addEventListener("click", () => {
        const apodo = document.getElementById("apodo-pago").value.trim();
        const servicio = document.getElementById("servicio").value;
        if (!apodo) { alert("Ingresa tu apodo."); return; }
        apodoGlobal = apodo;
        servicioSeleccionado = servicio;
        pagoConfirmado = true;
        document.getElementById("pago-confirmado").value = "true";
        alert("Pago simulado confirmado para " + apodoGlobal);
    });

    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const mensaje = document.getElementById("mensaje").value.trim();
        if (!mensaje || !apodoGlobal) { alert("Debes estar autenticado."); return; }

        const formData = new FormData();
        formData.append("apodo", apodoGlobal);
        formData.append("mensaje", mensaje);
        formData.append("servicio", servicioSeleccionado);
        formData.append("pago_confirmado", pagoConfirmado ? "true" : "false");
        formData.append("codigo", document.getElementById("codigo").value.trim());

        const response = await fetch("/chat", { method: "POST", body: formData });
        const data = await response.json();

        const div = document.createElement("div");
        div.innerHTML = `<b>${apodoGlobal}:</b> ${mensaje}<br><b>Asistente:</b> ${data.respuesta}`;
        chatMensajes.appendChild(div);
        chatMensajes.scrollTop = chatMensajes.scrollHeight;

        document.getElementById("mensaje").value = "";
    });

    limpiarChat.addEventListener("click", () => { chatMensajes.innerHTML = ""; });
});
