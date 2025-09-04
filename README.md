Asistente Virtual May Roga 🌿

Este proyecto es un asistente virtual de risoterapia y bienestar natural, que ofrece:

Respuestas rápidas de vida (55 segundos, $2)

Risoterapia y bienestar natural (10 minutos, $12)

Horóscopo y consejos (1 minuto 30 segundos, $5)

El asistente utiliza IA profesional (Gemini/OpenAI), técnicas de vida TVid, escucha sin juzgar, y ofrece respuestas claras, respetuosas y motivadoras. Permite pagos Stripe, guarda historial en Firebase, y tiene voz TTS opcional para escuchar respuestas.

🚀 Características

Multiusuario con cola de solicitudes y límite de solicitudes simultáneas.

Detecta automáticamente el idioma del usuario.

Guarda historial de mensajes y respuestas en Firebase.

Pagos integrados con Stripe (checkout por producto/servicio).

Chat profesional siguiendo las técnicas TVid y la dualidad positivo/negativo.

Text-to-speech (escuchar respuestas con un botón).

Compatible con Render y otros hosting que soporten Flask.

🛠 Requisitos

Python 3.11+

Claves de entorno:

STRIPE_SECRET_KEY=<tu_stripe_secret>
STRIPE_PUBLISHABLE_KEY=<tu_stripe_publishable>
GEMINI_API_KEY=<tu_api_gemini>
__firebase_config__=<tu_json_firebase>


Librerías (ver requirements.txt):

Flask==3.0.3
Flask-CORS==4.0.1
gunicorn==22.0.0
stripe==11.4.0
firebase-admin==6.5.0
google-generativeai==0.7.1
google-cloud-firestore==2.16.0
httpx==0.28.1


Instalar dependencias:

pip install -r requirements.txt

🖥 Estructura de archivos
/main.py          -> Servidor Flask principal
/templates/
    index.html       -> Página principal y chat
    success.html     -> Página de pago exitoso
    cancel.html      -> Página de pago cancelado
/static/
    css/style.css
    js/script.js
requirements.txt
README.md

⚡ Despliegue en Render

Subir repo a GitHub.

Crear un Web Service en Render con Python 3.11+.

Configurar variables de entorno mencionadas arriba.

Configurar Build Command:

pip install -r requirements.txt


Configurar Start Command:

gunicorn main:app --bind 0.0.0.0:$PORT


Deploy. El servicio estará disponible 24/7 en la URL de Render.

💬 Uso

Visitar / para ver la página principal.

Seleccionar un servicio y pagar con Stripe.

Enviar mensajes en el chat.

Presionar “Escuchar respuesta” para TTS.

⚠️ Notas importantes

Limite de solicitudes simultáneas por usuario: 3

Cola automática para multiusuario

Firebase registra historial de chat

Respuestas de IA de 30 a 90 segundos, respetando Tvid

Texto y voz en español (detecta idioma automáticamente)

✅ Listo para producción

Con este README y los archivos proporcionados, tu Asistente Virtual May Roga está listo para:

Operar 24/7

Atender muchos usuarios simultáneamente

Cobrar automáticamente por servicios

Mantener profesionalismo y coherencia con tus técnicas TVid
