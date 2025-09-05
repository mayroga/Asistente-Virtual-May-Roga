const backendURL = "https://asistente-virtual-may-roga.onrender.com";
let service = null;
let totalSeconds = 0;
let timerInterval = null;

// Inicializa la sesión y obtiene el servicio comprado o desbloqueado
async function init(sessionId, secretCode = null) {
    try {
        let url = `${backendURL}/get-session?session_id=${sessionId}`;
        if(secretCode) url += `&secret=${secretCode}`;
        const res = await fetch(url);
        const data = await res.json();
        if(data.product){
            service = data.product;
            totalSeconds = getServiceDuration(service);
            startSSE(service, secretCode);
            startTimer(totalSeconds);
        } else {
            displayMessage("Error: no se pudo obtener el servicio.");
        }
    } catch(e) {
        displayMessage("Error de conexión con el servidor.");
        console.error(e);
    }
}

// Muestra los mensajes en pantalla
function displayMessage(msg){
    const output = document.getElementById("assistant-output");
    output.innerHTML += `<p>${msg}</p>`;
    output.scrollTop = output.scrollHeight;
}

// Inicia SSE desde el backend
function startSSE(service, secretCode = null){
    let url = `${backendURL}/assistant-stream?service=${service}`;
    if(secretCode) url += `&secret=${secretCode}`;
    const evtSource = new EventSource(url);

    evtSource.onmessage = (e) => {
        displayMessage(e.data);
        if(e.data.includes("Finalizada")) clearInterval(timerInterval);
    }

    evtSource.onerror = () => {
        displayMessage("Sesión finalizada o error de conexión.");
        evtSource.close();
        clearInterval(timerInterval);
    }
}

// Cronómetro en pantalla
function startTimer(duration){
    let remaining = duration;
    const timerEl = document.getElementById("timer");

    timerInterval = setInterval(()=>{
        let minutes = Math.floor(remaining / 60);
        let seconds = remaining % 60;
        timerEl.innerText = `Tiempo restante: ${minutes}:${seconds < 10 ? '0'+seconds : seconds}`;
        remaining--;
        if(remaining < 0){
            clearInterval(timerInterval);
            timerEl.innerText = "Sesión finalizada ✅";
        }
    },1000);
}

// Retorna duración de cada servicio en segundos
function getServiceDuration(service){
    switch(service){
        case "Risoterapia y Bienestar Natural": return 600; // 10 min
        case "Horóscopo": return 120; // 2 min
        case "Respuesta Rápida": return 55; // 55 seg
        default: return 300; // 5 min default
    }
}

// Reproducir audio pregrabado de ejercicios
function playAudio(audioUrl){
    const audio = new Audio(audioUrl);
    audio.play();
}

// Función para comprar servicio desde botones
async function buyService(product, amount){
    try {
        const res = await fetch(`${backendURL}/create-checkout-session`, {
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body: JSON.stringify({product, amount})
        });
        const data = await res.json();
        if(data.id){
            const stripe = Stripe("{{ stripe_key }}");
            await stripe.redirectToCheckout({ sessionId: data.id });
        } else {
            alert("Error al crear la sesión de pago");
        }
    } catch(e){
        alert("Error conectando al servidor");
        console.error(e);
    }
}
