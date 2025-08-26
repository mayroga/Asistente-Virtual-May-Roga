const el = (id) => document.getElementById(id);
const gate = el("gate");
const chat = el("chat");
const gateMsg = el("gate-msg");
const btnStart = el("btn-start");
const btnPay = el("btn-pay");
const chatlog = el("chatlog");
const sendBtn = el("send");
const msgInput = el("msg");
const badge = el("sessionBadge");

let TOKEN = null;
let NICKNAME = null;
let ACCESS = null; // "free" o "paid"

function showMsg(target, text, type="info") {
  target.textContent = text;
  target.className = "msg " + type;
}

function addBubble(text, who="ai") {
  const b = document.createElement("div");
  b.className = "bubble " + (who === "user" ? "user" : "ai");
  b.innerHTML = text;
  chatlog.appendChild(b);
  chatlog.scrollTop = chatlog.scrollHeight;
}

async function startSession() {
  const nickname = (el("nickname").value || "").trim();
  const code = (el("freecode").value || "").trim();
  if (!nickname) return showMsg(gateMsg, "Debes escribir tu apodo/sobrenombre/número.", "error");

  try {
    const res = await fetch("/api/start-session", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({nickname, code})
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Error al iniciar");

    if (data.requires_payment) {
      NICKNAME = nickname;
      TOKEN = null;
      ACCESS = null;
      showMsg(gateMsg, "Se requiere pago para habilitar el chat. Presiona “Pagar sesión”.", "warn");
      btnPay.style.display = "inline-block";
      return;
    }
    // acceso concedido
    TOKEN = data.token;
    NICKNAME = nickname;
    ACCESS = data.access; // free o paid
    gate.classList.add("hidden");
    chat.classList.remove("hidden");
    badge.textContent = ACCESS === "free" ? "Acceso: Código especial" : "Acceso: Pago confirmado";
    addBubble("Hola " + NICKNAME + ". Soy el Médico Virtual May Roga. Cuéntame qué sientes: inicio, intensidad, si hay fiebre, dificultad para respirar, vómitos persistentes o sangrado. Te orientaré de forma profesional y clara.");
  } catch (e) {
    showMsg(gateMsg, e.message, "error");
  }
}

async function paySession() {
  const nickname = (el("nickname").value || "").trim();
  if (!nickname) return showMsg(gateMsg, "Escribe tu apodo para asociar el pago.", "error");
  try {
    const res = await fetch(`/pay/create-session?nickname=${encodeURIComponent(nickname)}`, {method:"POST"});
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Error al crear la sesión de pago");
    window.location.href = data.url;
  } catch (e) {
    showMsg(gateMsg, e.message, "error");
  }
}

async function sendMessage() {
  const text = (msgInput.value || "").trim();
  if (!text) return;
  addBubble(text, "user");
  msgInput.value = "";
  try {
    const res = await fetch("/api/message", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({token: TOKEN, message: text})
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Error en el chat");
    addBubble(data.reply, "ai");
  } catch (e) {
    addBubble("Ocurrió un problema. Intenta de nuevo. Si persiste, busca atención presencial.", "ai");
  }
}

function getParam(name) {
  const url = new URL(window.location.href);
  return url.searchParams.get(name);
}

async function resumeIfPaid() {
  const paid = getParam("paid");
  const nickname = getParam("nickname");
  if (paid === "1" && nickname) {
    // El webhook habrá marcado el apodo como pagado; pedimos acceso
    el("nickname").value = nickname;
    showMsg(gateMsg, "Pago confirmado. Presiona “Iniciar” para entrar al chat.", "success");
    btnPay.style.display = "none";
  }
}

btnStart.addEventListener("click", startSession);
btnPay.addEventListener("click", paySession);
sendBtn.addEventListener("click", sendMessage);
msgInput.addEventListener("keydown", (e)=>{ if (e.key==="Enter") sendMessage(); });

resumeIfPaid();

