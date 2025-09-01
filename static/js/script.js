document.addEventListener('DOMContentLoaded', function() {
    const apodoInput = document.getElementById('apodo');
    const serviceSelector = document.getElementById('service-selector');
    const payButton = document.getElementById('btn-pay-stripe');
    const accessCodeButton = document.getElementById('btn-access-code');
    const chatWrapper = document.getElementById('chat-wrapper');
    const chatForm = document.getElementById('chat-form');
    const chatOutput = document.getElementById('chat-output');
    const chatInput = document.getElementById('chat-input');
    const loadingMessage = document.getElementById('loading-message');

    let currentNickname = '';
    let currentService = '';

    // Función para mostrar mensajes en el chat
    function addMessage(sender, message) {
        const messageElement = document.createElement('p');
        messageElement.classList.add(`${sender}-message`);
        messageElement.textContent = message;
        chatOutput.appendChild(messageElement);
        chatOutput.scrollTop = chatOutput.scrollHeight;
    }

    // Configura el botón de pago de Stripe
    if (payButton) {
        payButton.addEventListener('click', async () => {
            currentNickname = apodoInput.value;
            currentService = serviceSelector.value;

            if (!currentNickname) {
                alert('Por favor, ingresa tu apodo.');
                return;
            }

            try {
                // Esta es la línea corregida
                const response = await fetch('/create-checkout-session/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        nickname: currentNickname,
                        service: currentService
                    }),
                });

                const session = await response.json();
                if (session.error) {
                    alert('Error en la sesión de pago: ' + session.error);
                    return;
                }

                window.location.href = session.url;
            } catch (e) {
                console.error('Error:', e);
                alert('Ocurrió un error al procesar el pago.');
            }
        });
    }

    // Configura el botón para el código de acceso
    if (accessCodeButton) {
        accessCodeButton.addEventListener('click', () => {
            const accessCode = document.getElementById('access-code').value;
            if (accessCode === 'MAYROGA') {
                toggleChat(true);
            } else {
                alert('Código de acceso incorrecto.');
            }
        });
    }

    // Maneja el envío del formulario de chat
    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const userMessage = chatInput.value;
            if (!userMessage) return;

            addMessage('user', userMessage);
            chatInput.value = '';
            loadingMessage.classList.remove('hidden');

            try {
                const response = await fetch('/chat/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        user_message: userMessage,
                        nickname: currentNickname,
                        service: currentService
                    })
                });
                const data = await response.json();

                if (data.error) {
                    addMessage('assistant', `Error: ${data.error}`);
                } else {
                    addMessage('assistant', data.assistant_message);
                }
            } catch (e) {
                addMessage('assistant', 'Error al conectar con el asistente.');
            } finally {
                loadingMessage.classList.add('hidden');
            }
        });
    }

    // Muestra u oculta la sección de chat
    function toggleChat(show) {
        if (show) {
            document.querySelector('.form-container').classList.add('hidden');
            chatWrapper.classList.remove('hidden');
            addMessage('assistant', `Hola ${currentNickname}, bienvenido. ¿En qué puedo ayudarte hoy con tu ${currentService}?`);
        } else {
            document.querySelector('.form-container').classList.remove('hidden');
            chatWrapper.classList.add('hidden');
        }
    }
});
