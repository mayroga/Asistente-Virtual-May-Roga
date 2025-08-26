const chatBox = document.getElementById("chat-box");

function sendMessage() {
  const input = document.getElementById("user-input");
  const message = input.value.trim();
  if (message === "") return;

  // Mensaje del usuario
  appendMessage(message, "user-message");

  // Simulación de respuesta del asistente
  setTimeout(() => {
    appendMessage("Soy tu Médico Virtual May Roga. Estoy aquí para orientarte.", "bot-message");
  }, 700);

  input.value = "";
}

function appendMessage(text, className) {
  const msg = document.createElement("div");
  msg.classList.add("message", className);
  msg.textContent = text;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}
