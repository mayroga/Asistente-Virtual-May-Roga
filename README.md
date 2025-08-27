# Medico Virtual + Risoterapia + Horóscopo - May Roga LLC

Este proyecto implementa un **Medico Virtual 24/7**, con integración de **Risoterapia** (Técnicas de Vida), **Horóscopo** y **respaldo automático desde JSON**. También incluye **pago con Stripe**.

---

## 📂 Estructura mínima

src/
main.py # Código principal de FastAPI
templates/
index.html # Interfaz del chat
static/
css/
style.css # Estilos
js/
images/
data/
behavior_guide.json # Respaldo general
enfermedades.json # Respaldo de enfermedades
urgencias.json # Respaldo de urgencias
requirements.txt # Dependencias
runtime.txt # Python version
render.yaml # Configuración Render
.env # Variables de entorno


---

## ⚡ Configuración rápida en Render

1. Crear **nuevo servicio web** en Render.  
2. Tipo: `Python`  
3. Repositorio: tu repo con esta estructura  
4. Comando de build:  
5. Comando de start:  
6. Variables de entorno:
- `OPENAI_API_KEY` → tu clave OpenAI  
- `STRIPE_API_KEY` → clave Stripe  
- `SUCCESS_URL` → URL tras pago exitoso  
- `CANCEL_URL` → URL si el pago se cancela  

---

## 🚀 Probar endpoints

- **Ping:**  
6. Variables de entorno:
- `OPENAI_API_KEY` → tu clave OpenAI  
- `STRIPE_API_KEY` → clave Stripe  
- `SUCCESS_URL` → URL tras pago exitoso  
- `CANCEL_URL` → URL si el pago se cancela  

---

## 🚀 Probar endpoints

- **Ping:**  
Debe devolver:  
```json
{"message":"Servidor activo 🚀"}
POST /chat
form-data: message="texto"
Mensaje general → respaldo behavior_guide

Contiene "enfermedad" → respaldo enfermedades

Contiene "urgencia" → respaldo urgencias

"horóscopo" o "risoterapia" → texto fijo

Stripe pago:
POST /create-checkout-session
🔄 Respaldo automático

Si OpenAI falla, el sistema usa los JSON de respaldo (behavior_guide.json, enfermedades.json, urgencias.json)

Garantiza que siempre haya respuesta, incluso sin servicio externo.
💡 Notas

static/ y templates/ son obligatorios para que Render sirva la web.

data/ contiene JSON de respaldo, debe existir.

Se puede ampliar el chat agregando más respuestas en los JSON.

Para producción Stripe, cambiar STRIPE_API_KEY a la clave real.
Listo para deploy final en Render.
Solo push al repo y Render instalará y desplegará automáticamente.

---

Con esto tienes:  

- **Explicación completa de carpetas**  
- **Instrucciones de Render**  
- **Cómo probar chat + respaldo + Stripe**  
- **Listo para producción**  

---

Si quieres, el siguiente paso es que haga **un mini checklist final de 5 minutos** para probar todo y asegurarte que el proyecto ya queda 100% operativo en Render.  

¿Hacemos eso ahora?
