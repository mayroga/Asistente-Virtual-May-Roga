// script.js - Interacción del chat Médico Virtual May Roga

const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", function(e) {
    if (e.key === "Enter") sendMessage();
});

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    appendMessage("Tú", message);
    userInput.value = "";

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message })
        });
        const data = await response.json();
        appendMessage("Médico Virtual", data.reply);
    } catch (err) {
        appendMessage("Médico Virtual", "❌ Error de conexión, intenta nuevamente.");
        console.error(err);
    }
}

function appendMessage(sender, message) {
    const msgDiv = document.createElement("div");
    msgDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// DOM
const nicknameInput = document.getElementById('nickname');
const freecodeInput = document.getElementById('freecode');
const btnStart = document.getElementById('btn-start');
const svcButtons = document.querySelectorAll('.svc');
const gateMsg = document.getElementById('gate-msg');

const chatSection = document.getElementById('chat');
const chatLog = document.getElementById('chatlog');
const msgInput = document.getElementById('msg');
const sendBtn = document.getElementById('send');

let selectedService = null;
let sessionToken = null;

// detectar idioma del navegador
const userLang = navigator.language || navigator.userLanguage || "es";

// elegir servicio
svcButtons.forEach(b=>{
  b.addEventListener('click', ()=> {
    svcButtons.forEach(x=>x.classList.remove('active'));
    b.classList.add('active');
    selectedService = b.dataset.service;
    gateMsg.innerText = `Servicio seleccionado: ${selectedService}`;
  });
});

// iniciar / pagar
btnStart.addEventListener('click', async ()=>{
  const nickname = nicknameInput.value.trim();
  const code = freecodeInput.value.trim();
  if(!nickname) return alert("Ingresa apodo.");

  // free pass
  if(code === "MKM991775"){
    const r = await fetch("/api/start-session",{method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({nickname, code})});
    const j = await r.json();
    if(j.token){ sessionToken = j.token; showChat(nickname); return; }
  }

  // si es consulta desde botones
  if(!selectedService) return alert("Selecciona un servicio.");
  // crear sesión en Stripe (POST preferible, main.py acepta GET/POST)
  const resp = await fetch(`/pay/create-session?nickname=${encodeURIComponent(nickname)}&servicio=${encodeURIComponent(selectedService)}`);
  const data = await resp.json();
  if(data.url){ window.location.href = data.url; } else alert("Error creando sesión.");
});

function showChat(nickname){
  document.getElementById('gate').classList.add('hidden');
  chatSection.classList.remove('hidden');
  document.getElementById('sessionBadge').innerText = nickname;
  appendBot(`✅ Acceso habilitado para ${nickname}. Bienvenido/a.`);
}

function appendBot(text){
  const d = document.createElement('div'); d.className='bot'; d.innerHTML = `<strong>Asistente:</strong> ${text}`; chatLog.appendChild(d); chatLog.scrollTop = chatLog.scrollHeight;
}
function appendUser(text){
  const d = document.createElement('div'); d.className='user'; d.innerHTML = `<strong>Tú:</strong> ${text}`; chatLog.appendChild(d); chatLog.scrollTop = chatLog.scrollHeight;
}

// enviar mensaje
sendBtn.addEventListener('click', async ()=>{
  const text = msgInput.value.trim();
  if(!text) return;
  appendUser(text); msgInput.value='';

  // enviar idioma con payload
  const payload = { token: sessionToken, message: text, lang: userLang };
  try{
    const r = await fetch("/api/message", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(payload)});
    const j = await r.json();
    appendBot(j.reply);
  }catch(e){
    appendBot("❌ Error de conexión. Intenta de nuevo.");
    console.error(e);
  }
});
