Asistente Virtual May Roga 🌿 (Versión Definitiva)

Asistente virtual de risoterapia y bienestar natural, diseñado para atender múltiples usuarios simultáneamente, ofrecer servicios instantáneos tras pago, y aplicar las Técnicas de Vida (TVid) de May Roga LLC, su fundador Maykel Rodríguez García (Licenciado en Enfermería y MBA).

Servicios
Servicio	Duración	Precio	Qué ofrece
Respuesta Rápida	55 seg	$2	Respuesta inmediata a preguntas de vida o estado emocional
Risoterapia y Bienestar Natural	10 min	$12	Sesión guiada de risa y bienestar aplicando TVid
Horóscopo y Consejos de Vida	2 min	$6	Consejos personalizados y motivación diaria
Servicio Personalizado	20 min	$50	Sesión individual adaptada a necesidades del usuario
Servicio Corporativo	3 sesiones de 15–25 min	$750	Atención a empresas con varias sesiones programadas
Servicio Grupal	15 min	$450	Sesión grupal de hasta 10 personas con interacción dinámica
Características

Multiusuario con cola de solicitudes y límite de solicitudes simultáneas.

Detección automática de idioma y generación de voz TTS con acento local.

Mensajes en vivo con opción de reproducir audio inmediato.

Respuestas siempre basadas en técnicas TVid y dualidad positiva/negativa.

Pagos integrados con Stripe (checkout por servicio).

Historial de mensajes registrado en Firebase.

Pantalla limpia y adaptada a móviles y cualquier dispositivo.

Código secreto personal para acceso total al sistema (administrador).

Requisitos

Python 3.11+

Claves de entorno:

STRIPE_SECRET_KEY=<tu_stripe_secret>
STRIPE_PUBLISHABLE_KEY=<tu_stripe_publishable>
GEMINI_API_KEY=<tu_api_gemini>
MAYROGA_ACCESS_CODE=<tu_codigo_secreto>
FIREBASE_CONFIG=<tu_json_firebase>


Librerías (requirements.txt):

fastapi==0.111.0
uvicorn==0.23.0
stripe==11.4.0
firebase-admin==6.5.0
httpx==0.28.1
openai==1.27.0


Instalar dependencias:

pip install -r requirements.txt

Estructura de archivos
/main.py           -> Servidor principal FastAPI con TTS y SSE
/templates/index.html -> Página principal y chat
/templates/success.html -> Página de pago exitoso
/templates/cancel.html  -> Página de pago cancelado
/static/css/style.css
/static/js/script.js
/static/audios/  -> Audios generados automáticamente
requirements.txt
README.md

Despliegue en Render

Subir repo a GitHub.

Crear Web Service en Render con Python 3.11+.

Configurar variables de entorno mencionadas.

Build Command: pip install -r requirements.txt

Start Command: gunicorn main:app --bind 0.0.0.0:$PORT

Deploy y tu servicio estará 24/7 listo para uso.

Uso

Visitar / para abrir la página principal.

Seleccionar un servicio y pagar con Stripe (o usar código secreto si eres administrador).

Iniciar la sesión de chat.

Recibir mensajes del asistente con opción de audio TTS para escuchar cada respuesta.

Finalizar sesión con evaluación y sugerencias de próximas sesiones.

Notas importantes

Límite de solicitudes simultáneas: 3 por usuario, con cola automática.

Firebase guarda historial de chat.

Respuestas IA entre 30 y 90 segundos, respetando técnicas TVid.

Texto y voz detectan automáticamente el idioma del usuario.

Listo para producción definitiva, sin pruebas ni placeholders.

🔹 Diagrama de flujo del sistema
flowchart TD
    A[Usuario entra a la web] --> B{Selecciona servicio}
    B --> |Stripe| C[Crear sesión de pago]
    B --> |Código secreto admin| D[Acceso total al sistema]
    C --> E[Pagar con Stripe]
    E --> F[Pago exitoso -> inicia chat]
    D --> F
    F --> G[Asistente genera mensaje en texto]
    G --> H[Detecta idioma automáticamente]
    H --> I[Genera audio TTS con acento local]
    I --> J[Mensaje en pantalla + botón "Escuchar"]
    J --> K[Usuario lee o escucha mensaje]
    K --> L[Aplica Técnicas TVid y dualidad positivo/negativo]
    L --> M[Temporizador de sesión en vivo]
    M --> N[Fin de sesión]
    N --> O[Evaluación de satisfacción]
    O --> P[Sugerencias futuras y gamificación]


Con este README tienes todo documentado:

Servicios, precios y duración.

Multiusuario y detección de idioma.

TTS en vivo con acento nativo.

Código secreto y Stripe.

Flujo de interacción completo.

Compatible con Render y Google Sites.

✅ Proyecto listo para producción definitiva.
