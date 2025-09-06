const backendURL = "https://asistente-virtual-may-roga.onrender.com";
const stripe = Stripe("{{ stripe_key }}"); // Clave pública de Stripe
let currentTimer = null;

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

function startService(serviceName, price, duration){
    startSession(serviceName, null, duration);
}

function startSession(serviceName, secret=null, duration=null){
    const output = document.getElementById("assistant-output");
    const timerEl = document.getElementById("timer");
    output.innerHTML = `<p>Iniciando sesión: ${serviceName}</p>`;
    timerEl.innerText = "";

    let totalSeconds = duration || 300;
    startCountdown(totalSeconds, timerEl);
    startSSE(serviceName, output, secret);
}

function startCountdown(seconds, displayEl){
    if(currentTimer) clearInterval(currentTimer);
    currentTimer = setInterval(()=>{
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        displayEl.innerText = `Tiempo restante: ${mins}:${secs < 10 ? '0'+secs : secs}`;
        if(seconds <= 0) clearInterval(currentTimer);
        seconds--;
    }, 1000);
}

function startSSE(serviceName, outputEl, secret=null){
    const url = `${backendURL}/assistant-stream?service=${encodeURIComponent(serviceName)}${secret ? '&secret=' + secret : ''}`;
    const evtSource = new EventSource(url);

    evtSource.onmessage = (e)=>{
        outputEl.innerHTML += `<p>${e.data}</p>`;
        outputEl.scrollTop = outputEl.scrollHeight;
        if(e.data.startsWith("🎵")){
            const audioSrc = e.data.replace("🎵", "").trim();
            const audio = new Audio(audioSrc);
            audio.play().catch(err=>console.error(err));
        }
    };

    evtSource.onerror = ()=>{
        evtSource.close();
        outputEl.innerHTML += "<p>Sesión finalizada o desconectada</p>";
    };
}

window.buyService = buyService;
window.accessWithCode = accessWithCode;
window.startService = startService;
