// static/js/script.js

document.addEventListener('DOMContentLoaded', () => {
    const apodoInput = document.getElementById('apodo');
    const serviceSelector = document.getElementById('service-selector');
    const accessCodeInput = document.getElementById('access-code');
    const btnAccessCode = document.getElementById('btn-access-code');
    const btnPayStripe = document.getElementById('btn-pay-stripe');
    const chatWrapper = document.getElementById('chat-wrapper');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatOutput = document.getElementById('chat-output');
    const loadingMessage = document.getElementById('loading-message');

    let stripe;

    // Inicializar Stripe con la clave pública del backend
    fetch('/config')
        .then((response) => response.json())
        .then((data) => {
            if (data.publicKey) {
                stripe = Stripe(data.publicKey);
            } else {
                console.error("No se pudo obtener la clave pública de Stripe.");
            }
        });

    btnAccessCode.addEventListener('click', async () => {
        const apodo = apodoInput.value.trim();
        const service = serviceSelector.value;
        const code = accessCodeInput.value.trim();

        if (!apodo) {
            alert('Por favor, ingresa tu apodo.');
            return;
        }
        if (!code) {
            alert('Por favor, ingresa el código de acceso.');
            return;
        }

        try {
            const formData = new FormData();
            formData.append('apodo', apodo);
            formData.append('code', code);
            formData.append('service', service);

            const response = await fetch('/access-code', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                chatWrapper.classList.remove('hidden');
                alert(data.message);
            } else {
                alert(data.error);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al conectar con el servidor. Inténtalo de nuevo.');
        }
    });

    btnPayStripe.addEventListener('click', async () => {
        const apodo = apodoInput.value.trim();
        const service = serviceSelector.value;

        if (!apodo) {
            alert('Por favor, ingresa tu apodo.');
            return;
        }

        try {
            const formData = new FormData();
            formData.append('service', service);
            formData.append('apodo', apodo);

            const response = await fetch('/create-checkout-session', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.id) {
                const result = await stripe.redirectToCheckout({ sessionId: data.id });
                if (result.error) {
                    alert(result.error.message);
                }
            } else {
                alert(data.error || 'Error al crear la sesión de pago.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('No se pudo conectar con el servidor de pagos.');
        }
    });

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const apodo = apodoInput.value.trim();
        const service = serviceSelector.value;
        const message = chatInput.value;

        if (!message) return;

        const userMessageDiv = document.createElement('div');
        userMessageDiv.className = 'user-message';
        userMessageDiv.textContent = message;
        chatOutput.appendChild(userMessageDiv);
        chatInput.value = '';
        chatOutput.scrollTop = chatOutput.scrollHeight;

        loadingMessage.classList.remove('hidden');

        const lang = detectLanguage(message);

        try {
            const formData = new FormData();
            formData.append('apodo', apodo);
            formData.append('service', service);
            formData.append('message', message);
            formData.append('lang', lang);

            const response = await fetch('/chat', {
                method: 'POST',
                body: formData
            });

            loadingMessage.classList.add('hidden');

            if (response.ok) {
                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);

                const audio = new Audio(audioUrl);
                audio.play();
                
                const assistantMessageDiv = document.createElement('div');
                assistantMessageDiv.className = 'assistant-message';
                assistantMessageDiv.textContent = 'Asistente: Escuchando la respuesta...';
                chatOutput.appendChild(assistantMessageDiv);
                chatOutput.scrollTop = chatOutput.scrollHeight;

            } else {
                const errorData = await response.json();
                const errorMessageDiv = document.createElement('div');
                errorMessageDiv.className = 'assistant-message';
                errorMessageDiv.style.backgroundColor = '#EF9A9A';
                errorMessageDiv.textContent = `Error: ${errorData.error}`;
                chatOutput.appendChild(errorMessageDiv);
            }
        } catch (error) {
            console.error('Error:', error);
            loadingMessage.classList.add('hidden');
            const errorMessageDiv = document.createElement('div');
            errorMessageDiv.className = 'assistant-message';
            errorMessageDiv.style.backgroundColor = '#EF9A9A';
            errorMessageDiv.textContent = 'Error de conexión. Inténtalo de nuevo.';
            chatOutput.appendChild(errorMessageDiv);
        }
    });

    function detectLanguage(text) {
        const spanishKeywords = ['hola', 'gracias', 'salud', 'risoterapia', 'ayuda'];
        const englishKeywords = ['hello', 'thanks', 'health', 'risotherapy', 'help'];
        
        const textLower = text.toLowerCase();
        
        let spanishCount = spanishKeywords.filter(word => textLower.includes(word)).length;
        let englishCount = englishKeywords.filter(word => textLower.includes(word)).length;

        if (spanishCount > englishCount) {
            return 'es';
        }
        if (englishCount > spanishCount) {
            return 'en';
        }
        return 'es';
    }

    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('apodo') && urlParams.get('service')) {
        const apodo = urlParams.get('apodo');
        const service = urlParams.get('service');
        apodoInput.value = apodo;
        serviceSelector.value = service;
        chatWrapper.classList.remove('hidden');
    }

});
