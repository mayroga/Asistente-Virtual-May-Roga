Asistente de Bienestar Virtual con May Roga
Este es un asistente de bienestar virtual impulsado por inteligencia artificial. Ofrece servicios como Risoterapia y Horóscopos Motivacionales basados en las exclusivas Técnicas de Vida (TVid) de Maykel Rodríguez García. El proyecto está diseñado para ser una plataforma profesional, segura y funcional, con un sistema de chat en tiempo real y opciones de pago integradas con Stripe.

Características Principales
Pagos Seguros: Integración completa con Stripe para procesar pagos de forma segura.

Inteligencia Artificial: Utiliza las API de Gemini y OpenAI para generar respuestas de calidad y personalizadas.

Servicios Exclusivos: Ofrece sesiones de risoterapia, horóscopo motivacional y respuestas rápidas.

Acceso Flexible: Permite el acceso mediante pago o a través de un código de acceso especial.

Despliegue Profesional: Configurado para ser fácilmente desplegable en plataformas como Render usando Gunicorn.

Instalación
Clonar el repositorio:

git clone [https://www.atlassian.com/es/git/tutorials/setting-up-a-repository](https://www.atlassian.com/es/git/tutorials/setting-up-a-repository)
cd [nombre-del-proyecto]

Configurar variables de entorno:
Crea un archivo llamado .env en la carpeta principal del proyecto y añade tus claves secretas:

STRIPE_SECRET_KEY=...
STRIPE_PUBLIC_KEY=...
STRIPE_WEBHOOK_SECRET=...
GEMINI_API_KEY=...
OPENAI_API_KEY=...
URL_SITE=https://[tu-url-de-render].onrender.com
MAYROGA_ACCESS_CODE=MAYROGA2024

Instalar dependencias:

pip install -r requirements.txt

Uso
Para ejecutar la aplicación localmente, usa el siguiente comando:

python main.py

Abre tu navegador y ve a http://127.0.0.1:5000 para ver la aplicación en funcionamiento.

Despliegue
Este proyecto está preparado para ser desplegado en Render. Sigue los siguientes pasos:

Sube tu código a GitHub/GitLab.

En Render, crea un nuevo servicio web y conecta tu repositorio.

Configura las variables de entorno con tus claves secretas.

En los comandos de construcción, usa pip install -r requirements.txt.

En los comandos de inicio, usa gunicorn main:app.

Créditos
Maykel Rodríguez García: Creador de las exclusivas Técnicas de Vida (TVid) en las que se basan los servicios de este asistente.
