// =========================
// Variables globales
// =========================
const form = document.getElementById('medicoForm');
const resultadoDiv = document.getElementById('resultado');
let sessionToken = null;

// =========================
// Función para mostrar resultados
// =========================
function mostrarResultado(data) {
  resultadoDiv.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
}

// =========================
// Enviar formulario
// =========================
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const apodo = document.getElementById('apodo').value.trim();
  const servicio = document.getElementById('servicio').value;
  const codigo = document.getElementById('codigo').value.trim();

  if (!apodo || !servicio) {
    alert("Debes indicar apodo y servicio.");
    return;
  }

  // =========================
  // 1) Intento de acceso gratuito por código
  // =========================
  if (codigo === "MKM991775") {
    const payload = { nickname: apodo, code: codigo };
    const resp = await fetch("/api/start-session", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload)
    });
    const data = await resp.json();
    if (data.token) {
      sessionToken = data.token;
      alert("✅ Acceso gratuito habilitado");
    }
  }

  // =========================
  // 2) Si no tiene token → crear sesión de pago
  // =========================
  if (!sessionToken) {
    try {
      const sessionRes = await fetch(`/pay/create-session?nickname=${encodeURIComponent(apodo)}`);
      const sessionData = await sessionRes.json();
      if (sessionData.url) {
        window.location.href = sessionData.url; // Redirige a Stripe
        return;
      } else {
        alert("Error al crear sesión de pago.");
        return;
      }
    } catch (err) {
      alert("Error al conectar con Stripe: " + err.message);
      return;
    }
  }

  // =========================
  // 3) Enviar mensaje al “cerebro” híbrido
  // =========================
  const userMessage = `Quiero información sobre ${servicio}.`; // ejemplo de texto
  try {
    const chatRes = await fetch("/api/message", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ token: sessionToken, message: userMessage })
    });
    const chatData = await chatRes.json();
    mostrarResultado(chatData);
  } catch (err) {
    alert("Error al enviar mensaje al servidor: " + err.message);
  }
});
