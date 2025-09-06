const stripe = Stripe("pk_live_51NqPxQBOA5mT4t0PEoRVRc0Sj7DugiHvxhozC3BYh0q0hAx1N3HCLJe4xEp3MSuNMA6mQ7fAO4mvtppqLodrtqEn00pgJNQaxz");
const backendURL = "https://asistente-virtual-may-roga.onrender.com";

// Compra vía Stripe
async function buyService(product, amount){
    try {
        const res = await fetch(`${backendURL}/create-checkout-session`, {
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body: JSON.stringify({product, amount})
        });
        const data = await res.json();
        if(data.id){
            await stripe.redirectToCheckout({ sessionId: data.id });
        } else {
            alert("Error al crear la sesión de pago");
        }
    } catch(e){
        alert("Error conectando al servidor");
    }
}

// Desbloquear todos los servicios con código secreto
async function unlockAllServices(){
    const code = document.getElementById("secret-input").value.trim();
    if(!code){ alert("Ingresa tu código secreto"); return; }
    try {
        const res = await fetch(`${backendURL}/assistant-stream?service=all&secret=${code}`);
        if(res.status === 200){
            startSSE("all", code);
            alert("Todos los servicios desbloqueados ✅");
        } else {
            alert("Código incorrecto ❌");
        }
    } catch(e){
        alert("Error de conexión con el servidor");
    }
}

// SSE en vivo con TTS
function startSSE(service, secret=null){
    const outputEl = document.getElementById("assistant-output");
    outputEl.innerHTML = "";
    const url = `${backendURL}/assistant-stream?service=${encodeURIComponent(service)}${secret ? '&secret=' + secret : ''}`;
    const evtSource = new EventSource(url);

    evtSource.onmessage = (e) => {
        const msg = e.data;
        if(msg.startsWith("🎵")){
            const audioSrc = msg.replace("🎵","").trim();
            const audioBtn = document.createElement("button");
            audioBtn.className = "audio-btn";
            audioBtn.innerText = "Escuchar respuesta";
            audioBtn.onclick = ()=>{ new Audio(audioSrc).play(); }
            outputEl.appendChild(audioBtn);
            outputEl.appendChild(document.createElement("br"));
        } else {
            const p = document.createElement("p");
            p.innerText = msg;
            outputEl.appendChild(p);
        }
        outputEl.scrollTop = outputEl.scrollHeight;
    };

    evtSource.onerror = () => {
        evtSource.close();
        const p = document.createElement("p");
        p.innerText = "Sesión finalizada o desconectada";
        outputEl.appendChild(p);
    };
}
