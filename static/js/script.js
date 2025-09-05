// static/js/script.js
const backendURL = "https://asistente-virtual-may-roga.onrender.com";

async function init(sessionId, secretCode=null){
    try{
        const res = await fetch(`${backendURL}/get-session?session_id=${sessionId}`);
        const data = await res.json();
        let service = data.product;

        startSSE(service, secretCode);
    } catch(e){
        document.getElementById("assistant-output").innerText = "Error obteniendo la sesión.";
    }
}

function startSSE(service, secretCode=null){
    let url = `${backendURL}/assistant-stream?service=${encodeURIComponent(service)}`;
    if(secretCode) url += `&secret=${encodeURIComponent(secretCode)}`;

    const evtSource = new EventSource(url);
    const output = document.getElementById("assistant-output");
    const timerDiv = document.getElementById("timer");
    
    let totalTime = 0;
    let elapsed = 0;

    evtSource.onmessage = (e)=>{
        if(e.data.startsWith("Sesión de")){
            timerDiv.innerText = "Sesión finalizada ✅";
            evtSource.close();
            return;
        }
        output.innerHTML += `<p>${e.data}</p>`;
        output.scrollTop = output.scrollHeight;
    }

    evtSource.onerror = ()=>{ evtSource.close(); }

    // Cronómetro visible para cualquier servicio
    totalTime = getServiceDuration(service);
    elapsed = 0;
    const interval = setInterval(()=>{
        if(elapsed >= totalTime){
            clearInterval(interval);
            timerDiv.innerText = "Tiempo finalizado ✅";
            return;
        }
        elapsed++;
        timerDiv.innerText = `Tiempo: ${formatTime(elapsed)} / ${formatTime(totalTime)}`;
    },1000);
}

function getServiceDuration(service){
    switch(service){
        case "Risoterapia y Bienestar Natural": return 600; // 10 min
        case "Horóscopo": return 120; // 2 min
        case "Respuesta Rápida": return 55; // 55 seg
        default: return 300; // default 5 min
    }
}

function formatTime(sec){
    const m = Math.floor(sec/60);
    const s = sec % 60;
    return `${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
}

function playAudio(url){
    const audio = new Audio(url);
    audio.play();
}
