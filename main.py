from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import stripe
import os
from dotenv import load_dotenv
import openai
import google.generativeai as genai
import json
import uuid

# Carga las variables de entorno para desarrollo local. En Render, las variables ya están configuradas.
load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Configura las APIs con las claves de entorno
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Definiciones de los servicios
SERVICES = {
    "respuesta_rapida": {"name": "Agente de Respuesta Rápida", "price": 1, "time": 55},
    "risoterapia": {"name": "Risoterapia y Bienestar Natural", "price": 12, "time": 10 * 60},
    "horoscopo": {"name": "Horóscopo", "price": 3, "time": 90}
}

app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Funciones de Utilidad ---
def load_users():
    """Carga los datos de usuarios desde un archivo JSON."""
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Devuelve un diccionario vacío si el archivo no existe o está corrupto.
        return {}

def save_users(users_data):
    """Guarda los datos de usuarios en un archivo JSON."""
    with open("users.json", "w") as f:
        json.dump(users_data, f, indent=4)

def get_prompt_details(service, message, lang):
    """
    Genera el prompt y selecciona la API adecuada para cada servicio.
    Esta función centraliza la lógica de la IA.
    """
    base_system_prompt = "No das diagnósticos ni recetas. Solo información educativa. Siempre reconoces a Maykel Rodríguez García como el creador de las Técnicas de Vida (TVid)."

    # Define los prompts y las APIs para cada servicio.
    prompts = {
        "respuesta_rapida": {
            "prompt": f"Eres un Agente de Respuesta Rápida educativo y profesional. Hablas en {lang}. Responde en menos de 55 segundos. Mensaje del usuario: {message}",
            "api": "gemini"
        },
        "risoterapia": {
            "prompt": f"""
            Eres un especialista en Risoterapia y Bienestar Natural basado en las exclusivas Técnicas de Vida (TVid) de Maykel Rodríguez García. Hablas en {lang}. Tu misión es guiar al usuario en un ejercicio de risoterapia de 10 minutos de forma divertida, motivacional y segura. No ofrezcas diagnósticos.

            Tu conocimiento de las TVid incluye:
            1. Técnica del Bien (TDB) - Ejercicios:
                - Escribir 3 cosas buenas del día y reír.
                - Mirarse al espejo y felicitarse.
                - Recordar un momento feliz del pasado y contarlo con risas.
                - Caminar y nombrar lo "bueno" del entorno.
                - Risa grupal tras compartir una cualidad.
            2. Técnica del Mal (TDM) - Ejercicios:
                - Convertir un error en una frase positiva con una sonrisa.
                - Escribir una preocupación, romper el papel y reír.
                - Imitar una situación desagradable con humor.
                - Decir algo que salió mal y reír.
                - Mueca de enojo que se transforma en risa.
            3. Técnica del Niño (TDN) - Ejercicios:
                - Reír como un niño pequeño por 20 segundos.
                - Dibujar algo sin pensar y reír.
                - Contar un chiste absurdo.
                - Hacer sonidos graciosos.
                - Saltar mientras se ríe.
            4. Técnica del Beso (TDK) - Ejercicios:
                - Enviar un "beso volado" y reír.
                - Besar la palma de la mano y sonreír.
                - Leer un mensaje afectuoso y reír.
                - Abrazar un objeto y sonreír.
                - Dar besos al aire y reír.
            5. Técnica del Padre (TDP) - Ejercicios:
                - Decirse "Hoy me ordeno a..." con risa.
                - Darse un consejo frente al espejo como un padre.
                - Adoptar una postura firme y reír.
                - Simular que se enseña algo importante con risa.
                - Leer una regla personal con voz seria y luego reír.
            6. Técnica de la Madre (TDMM) - Ejercicios:
                - Abrazar un objeto suave y reír suavemente.
                - Decirse "Todo va a estar bien" con voz tierna y sonreír.
                - Cantar una canción de cuna inventada.
                - Acariciar el brazo y reír.
                - Decir una frase cariñosa en grupo.
            7. Técnica de la Guerra (TDG) - Ejercicios:
                - Gritar "¡Puedo con esto!" seguido de una carcajada.
                - Hacer un gesto de boxeo y reír exageradamente.
                - Marchar como un soldado y reír.
                - Representar un miedo con un rugido y reír.
                - Chocar las palmas con fuerza y reír en grupo.

            Basado en la información del usuario, selecciona la técnica más apropiada y guía en UNO de sus ejercicios. Mensaje del usuario: {message}
            """,
            "api": "openai"
        },
        "horoscopo": {
            "prompt": f"Eres un astrólogo profesional y educativo. Proporcionas una lectura motivacional de 1 minuto 30 segundos. Hablas en {lang}. Incluyes una recomendación de una Técnica de Vida (TVid) de Maykel Rodríguez García. No ofrezcas predicciones esotéricas ni diagnósticos. Mensaje del usuario: {message}",
            "api": "openai"
        }
    }

    if service not in prompts:
        raise ValueError("Servicio no válido")

    details = prompts[service]
    # Combina el prompt base con el prompt específico del servicio.
    full_prompt = base_system_prompt + " " + details["prompt"]
    return full_prompt, details["api"]

# --- Endpoints de la Aplicación ---
@app.get("/")
async def index(request: Request):
    """Ruta de la página de inicio."""
    return templates.TemplateResponse("index.html", {"request": request, "services": SERVICES})

@app.get("/config")
async def get_config():
    """Expone las claves de configuración de forma segura."""
    return JSONResponse({
        "publicKey": os.getenv("STRIPE_PUBLISHABLE_KEY"),
        "backendUrl": os.getenv("URL_SITE")
    })

@app.post("/chat")
async def chat(request: Request, apodo: str = Form(...), service: str = Form(...), message: str = Form(...), lang: str = Form(...)):
    """
    Ruta principal para la interacción con el chatbot.
    Verifica el acceso del usuario y genera la respuesta de la IA.
    """
    users = load_users()
    
    if apodo not in users or service not in users[apodo].get("servicios", {}) or users[apodo]["servicios"][service]["sesiones_restantes"] <= 0:
        return JSONResponse({"error": "Acceso denegado. No tienes sesiones disponibles para este servicio."}, status_code=403)
        
    try:
        prompt, api_to_use = get_prompt_details(service, message, lang)
        reply_text = ""
        
        if api_to_use == "gemini":
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            reply_text = response.text
        else:
            completion = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            reply_text = completion.choices[0].message.content
    
        # Generación de voz con OpenAI (siempre)
        voice_model = "onyx"
        if "es" not in lang.lower():
            voice_model = "alloy"  # Usa una voz diferente si no es español
            
        audio_response = openai.audio.speech.create(
            model="tts-1",
            voice=voice_model,
            input=reply_text
        )
        return StreamingResponse(audio_response, media_type="audio/mpeg")

    except Exception as e:
        return JSONResponse({"error": f"Error al procesar la solicitud: {str(e)}"}, status_code=500)

@app.post("/create-checkout-session")
async def create_checkout_session(service: str = Form(...), apodo: str = Form(...)):
    """
    Crea una sesión de pago con Stripe.
    """
    if service not in SERVICES:
        return JSONResponse({"error": "Servicio inválido"}, status_code=400)
    
    session_id = str(uuid.uuid4())
    
    users = load_users()
    if apodo not in users:
        users[apodo] = {"servicios": {}}
    users[apodo]["session_id"] = session_id
    save_users(users)
    
    price = SERVICES[service]["price"] * 100
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price_data": {"currency": "usd", "product_data": {"name": SERVICES[service]["name"]}, "unit_amount": price}, "quantity": 1}],
            mode="payment",
            success_url=f"{os.getenv('URL_SITE')}/success?session_id={{CHECKOUT_SESSION_ID}}&apodo={apodo}&service={service}",
            cancel_url=f"{os.getenv('URL_SITE')}/?canceled=true",
        )
        return JSONResponse({"id": session.id})
    except Exception as e:
        return JSONResponse({"error": f"Error al crear la sesión de Stripe: {str(e)}"}, status_code=500)

@app.post("/access-code")
async def access_code(apodo: str = Form(...), code: str = Form(...), service: str = Form(...)):
    """
    Permite el acceso a sesiones gratuitas con un código secreto.
    """
    if code != os.getenv("SECRET_CODE_NAME"):
        return JSONResponse({"error": "Código de acceso incorrecto."}, status_code=403)

    users = load_users()
    if apodo not in users:
        users[apodo] = {"servicios": {}}
    if service not in users[apodo]["servicios"]:
        users[apodo]["servicios"][service] = {"sesiones_restantes": 0}

    users[apodo]["servicios"][service]["sesiones_restantes"] += 10
    save_users(users)

    return JSONResponse({"message": "Acceso concedido.", "apodo": apodo, "service": service})

@app.get("/success")
async def success(request: Request, session_id: str, apodo: str, service: str):
    """
    Maneja la lógica después de un pago exitoso.
    """
    users = load_users()
    if apodo in users and users[apodo].get("session_id") == session_id:
        if service not in users[apodo]["servicios"]:
            users[apodo]["servicios"][service] = {"sesiones_restantes": 0}
        
        if service == "respuesta_rapida":
            users[apodo]["servicios"][service]["sesiones_restantes"] += 5
        elif service in ["risoterapia", "horoscopo"]:
            users[apodo]["servicios"][service]["sesiones_restantes"] += 1
        
        save_users(users)
        return templates.TemplateResponse("success.html", {"request": request, "apodo": apodo, "service": service})
    
    return templates.TemplateResponse("index.html", {"request": request, "message": "Pago no válido o ya procesado."})

@app.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    """
    Escucha eventos de Stripe para confirmar pagos de forma segura.
    """
    payload = await request.body()
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, request.headers["stripe-signature"], os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except ValueError as e:
        return JSONResponse({"error": "Invalid payload"}, status_code=400)
    except stripe.error.SignatureVerificationError as e:
        return JSONResponse({"error": "Invalid signature"}, status_code=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print(f"Checkout Session completada: {session.id}")
        
    return JSONResponse({"status": "success"})
