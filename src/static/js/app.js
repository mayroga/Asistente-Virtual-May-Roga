// src/static/js/app.js
(function () {
  function q(sel) { return document.querySelector(sel); }
  function el(id) { return document.getElementById(id); }

  const meta = {
    service: (document.querySelector('meta[name="service"]') || {}).content || "",
    token: (document.querySelector('meta[name="token"]') || {}).content || "",
    nickname: (document.querySelector('meta[name="nickname"]') || {}).content || ""
  };

  const chatForm = el("chatForm");
  const msgInput = el("message");
  const chatLog = el("chatLog");

  if (chatForm && msgInput && chatLog && meta.service) {
    chatForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const text = msgInput.value.trim();
      if (!text) return;

      // pinta mensaje del usuario
      const you = document.createElement("div");
      you.textContent = (meta.nickname ? meta.nickname + ": " : "Tú: ") + text;
      chatLog.appendChild(you);

      try {
        const resp = await fetch(`/api/${meta.service}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token: meta.token, message: text })
        });
        const data = await resp.json();

        const bot = document.createElement("div");
        bot.textContent = "May Roga: " + (data.reply || "(sin respuesta)");
        chatLog.appendChild(bot);
      } catch (err) {
        const errDiv = document.createElement("div");
        errDiv.textContent = "Error de red.";
        chatLog.appendChild(errDiv);
      }

      msgInput.value = "";
      chatLog.scrollTop = chatLog.scrollHeight;
    });
  }

  // Botones de home (si existen)
  const btnAsistente = el("goAsistente");
  const btnRiso = el("goRisoterapia");
  const btnHoro = el("goHoroscopo");
  const btnQuick = el("goQuick");

  const nickInput = el("nickInput");
  const codeInput = el("codeInput");

  function go(path) {
    const nick = (nickInput && nickInput.value || "").trim();
    const code = (codeInput && codeInput.value || "").trim();
    if (!nick) {
      alert("Primero escribe tu apodo/sobrenombre.");
      return;
    }
    const url = code ? `${path}?nickname=${encodeURIComponent(nick)}&code=${encodeURIComponent(code)}`
                     : `${path}?nickname=${encodeURIComponent(nick)}`;
    window.location.href = url;
  }

  if (btnAsistente) btnAsistente.addEventListener("click", () => go("/asistente"));
  if (btnRiso) btnRiso.addEventListener("click", () => go("/risoterapia"));
  if (btnHoro) btnHoro.addEventListener("click", () => go("/horoscopo"));
  if (btnQuick) btnQuick.addEventListener("click", () => go("/quickresponse"));
})();
