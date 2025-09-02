Asistente de Bienestar Virtual con May Roga
Este es un asistente de bienestar virtual profesional y escalable, diseñado para ser desplegado en la nube para múltiples usuarios.

Características Principales
Pagos Seguros: Integración completa con Stripe para procesar pagos de forma segura, redirigiendo al usuario para una experiencia de checkout confiable.

Inteligencia Artificial: Utiliza la API de Gemini (y se puede expandir con otras como OpenAI) para generar respuestas de alta calidad, personalizadas para cada usuario.

Servicios Exclusivos: Ofrece sesiones de risoterapia, horóscopo motivacional y un agente de respuesta rápida, basados en las exclusivas Técnicas de Vida (TVid).

Acceso Flexible: Permite el acceso mediante un pago o un código de acceso especial, gestionando el tiempo de sesión de cada cliente.

Despliegue Profesional: Configurado para ser fácilmente desplegable en plataformas como Render usando el servidor de aplicaciones Gunicorn.

Estructura del Proyecto
main.py: El servidor backend de Python que maneja las rutas de la API de Stripe, el chat en tiempo real y la lógica de negocio.

requirements.txt: Contiene todas las dependencias de Python necesarias para el proyecto.

templates/: Carpeta que almacena los archivos HTML, incluyendo index.html (el frontend principal), success.html y cancel.html para el flujo de pagos.

static/: Carpeta para los archivos estáticos como CSS y JavaScript.

Despliegue en Render
Sigue estos pasos para desplegar tu aplicación en la nube:

Clonar el Repositorio:
Asegúrate de que todo tu código (incluyendo main.py, requirements.txt, templates/ y static/) esté subido a un repositorio en GitHub o GitLab.

Configurar las Variables de Entorno en Render:
En tu cuenta de Render, crea un nuevo "Web Service" y conéctalo a tu repositorio. Luego, ve a la sección de "Environment" (Entorno) y añade las siguientes variables:

STRIPE_SECRET_KEY: Tu clave secreta de Stripe (sk_test_...).

URL_SITE: La URL de tu servicio web en Render (por ejemplo, https://nombre-de-tu-app.onrender.com).

Configurar los Comandos de Render:
Render necesita saber cómo construir y ejecutar tu aplicación. Configura los siguientes comandos:

Build Command (Comando de Construcción): pip install -r requirements.txt

Start Command (Comando de Inicio): gunicorn main:app

Actualizar el Código Frontend (index.html):
Antes de desplegar, debes editar el archivo index.html para que se comunique con tu backend en la nube. Reemplaza los placeholders con tu URL de Render y tu clave pública de Stripe.

// Reemplaza con tu clave pública de Stripe
const stripe = Stripe('pk_test_tu_clave_publica_aqui'); 

// Reemplaza con la URL de tu servicio web en Render
const BACKEND_URL = "[https://tu-url-de-render.onrender.com](https://tu-url-de-render.onrender.com)";

Créditos
Maykel Rodríguez García: Creador de las exclusivas Técnicas de Vida (TVid) en las que se basan los servicios de este asistente.
