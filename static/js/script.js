// Tu clave publicable de Stripe
// Reemplaza 'pk_test_tu_clave_publica_aqui' con tu clave real
const stripe = Stripe('pk_test_tu_clave_publica_aqui');

// La URL de tu servidor backend de Render
// Reemplaza 'https://tu-backend-url.onrender.com' con tu URL real
const BACKEND_URL = 'https://tu-backend-url.onrender.com';

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
                // Se reemplazó 'alert' por 'console.error' para asegurar el funcionamiento en Render
                console.error('Por favor, ingresa tu apodo.');
                return;
            }

            try {
                // Se actualizó la llamada a la API para usar la URL del backend de Render
                const response = await fetch(`${BACKEND_URL}/create-checkout-session`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        service: currentService
                    }),
                });

                const session = await response.json();
                if (session.error) {
                    console.error('Error en la sesión de pago: ' + session.error);
                    return;
                }
                
                // Redirige al usuario a la página de pago de Stripe
                const result = await stripe.redirectToCheckout({
                    sessionId: session.sessionId
                });
                
                if (result.error) {
                    console.error(result.error.message);
                }

            } catch (e) {
                console.error('Ocurrió un error al procesar el pago:', e);
            }
        });
    }

    // Configura el botón para el código de acceso
    if (accessCodeButton) {
        accessCodeButton.addEventListener('click', () => {
            const accessCode = document.getElementById('access-code').value;
            if (accessCode === 'MAYROGA2024') {
                toggleChat(true);
            } else {
                console.error('Código de acceso incorrecto.');
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
