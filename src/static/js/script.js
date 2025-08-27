const chatForm = document.getElementById('chat-form');
const chatBox = document.getElementById('chat-box');
const messageInput = document.getElementById('message');

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = messageInput.value.trim();
    if (!message) return;

    // Mostrar mensaje del usuario
    const userMsgDiv = document.createElement('div');
    userMsgDiv.className = 'message user-message';
    userMsgDiv.textContent = message;
    chatBox.appendChild(userMsgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    messageInput.value = '';

    // Enviar al backend
    try {
        const response = await fetch('/api/message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        const data = await response.json();

        // Mostrar mensaje del asistente
        const assistantMsgDiv = document.createElement('div');
        assistantMsgDiv.className = 'message assistant-message';
        assistantMsgDiv.textContent = data.reply || "No hay respuesta.";
        chatBox.appendChild(assistantMsgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;

    } catch (error) {
        console.error('Error enviando mensaje:', error);
    }
});
