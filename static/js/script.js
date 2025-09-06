const backendURL = "https://asistente-virtual-may-roga.onrender.com";
const stripe = Stripe("pk_live_51NqPxQBOA5mT4t0PEoRVRc0Sj7DugiHvxhozC3BYh0q0hAx1N3HCLJe4xEp3MSuNMA6mQ7fAO4mvtppqLodrtqEn00pgJNQaxz");

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
        console.error(e);
    }
}

async function accessWithCode(){
    const code = prompt("Ingrese su código secreto:");
    if(!code) return;
    try {
        const res = await fetch(`${backendURL}/assistant-stream?service=all&secret=${code}`);
        if(res.status === 403){
            alert("Código incorrecto");
            return;
        }
        startSession("Todos los servicios desbloqueados", code);
    } catch(e){
        alert("Error al verificar el código secreto");
        console.error(e);
    }
}

function startService(serviceName){
    startSession(serviceName);
}

function startSession(serviceName, secret=null){
    const output = document.getElementById("assistant-output");
    output.innerHTML = `<p class="assistant-message">Iniciando sesión: ${serviceName}</p>`;

    const evtSource = new EventSource(`${backendURL}/assistant-stream?service=${encodeURIComponent(serviceName)}${secret ? '&secret=' + secret : ''}`);
    evtSource.onmessage = (e)=>{
        const [text, audio] = e.data.split("|");
        const div = document.createElement("div");
        div.className = "assistant-message";
        div.innerHTML = `<p>${text}</p>${audio ? `<button onclick="new Audio('${audio}').play()">▶ Escuchar</button>` : ""}`;
        output.appendChild(div);
        output.scrollTop = output.scrollHeight;
    };
    evtSource.onerror = ()=>{evtSource.close();}
}

window.buyService = buyService;
window.accessWithCode = accessWithCode;
window.startService = startService;
