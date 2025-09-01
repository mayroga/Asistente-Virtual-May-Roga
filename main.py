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

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Variables de entorno
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Definiciones de los servicios
SERVICES = {
    "respuesta_rapida": {"name": "Agente de Respuesta Rápida", "price": 1, "time": 55},
    "risoterapia": {"name": "Risoterapia y Bienestar Natural", "price": 12, "time": 10*60},
    "horoscopo": {"name": "Horóscopo", "price": 3, "time": 90}
}

app.mount("/static", StaticFiles(directory="static"), name="static")

# Función para cargar y guardar el estado de los usuarios
def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users(users_data):
    with open("users.json", "w") as f:
        json.dump(users_data, f, indent=4)

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "services": SERVICES})

@app.get("/config")
async def get_config():
    """Expone la clave pública de Stripe de forma segura."""
    # Se ha corregido la variable de entorno de 'STRIPE_PUBLISHABLE_KEY' a 'STRIPE_PUBLIC_KEY'.
    return JSONResponse({"publicKey": os.getenv("STRIPE_PUBLIC_KEY")})

# Función para generar el prompt y el modelo
def get_prompt_details(service, message, lang):
    """Genera el prompt según el servicio y el idioma."""
    base_system_prompt = "No das diagnósticos ni recetas. Solo información educativa. Siempre reconoces a Maykel Rodríguez García como el creador de las Técnicas de Vida (TVid)."
    
    if service == "respuesta_rapida":
        prompt = f"Eres un Agente de Respuesta Rápida educativo y profesional. Hablas en {lang}. Responde en menos de 55 segundos. Mensaje del usuario: {message}"
        api_to_use = "gemini"
    elif service == "risoterapia":
        prompt = f"""
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
        """
        api_to_use = "openai"
    elif service == "horoscopo":
        prompt = f"Eres un astrólogo profesional y educativo. Proporcionas una lectura motivacional de 1 minuto 30 segundos. Hablas en {lang}. Incluyes una recomendación de una Técnica de Vida (TVid) de Maykel Rodríguez García. No ofrezcas predicciones esotéricas ni diagnósticos. Mensaje del usuario: {message}"
        api_to_use = "openai"
    
    return base_system_prompt + " " + prompt, api_to_use

@app.post("/chat")
async def chat(request: Request, apodo: str = Form(...), service: str = Form(...), message: str = Form(...), lang: str = Form(...)):
    users = load_users()
    
    if apodo not in users or service not in users[apodo]["servicios"] or users[apodo]["servicios"][service]["sesiones_restantes"] <= 0:
        return JSONResponse({"error": "Acceso denegado. No tienes sesiones disponibles para este servicio."}, status_code=403)
        
    prompt, api_to_use = get_prompt_details(service, message, lang)
    reply_text = ""
    
    try:
        if api_to_use == "gemini":
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            reply_text = response.text
        else: # Usamos OpenAI
            completion = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            reply_text = completion.choices[0].message.content
            
    except Exception as e:
        return JSONResponse({"error": f"(Error al generar respuesta): {str(e)}"}, status_code=500)
    
    # Generación de voz con OpenAI (siempre)
    try:
        voice_model = "onyx" if lang.lower() == 'es' else "alloy"
        response_stream = openai.audio.speech.create(
            model="tts-1",
            voice=voice_model,
            input=reply_text
        )
        return StreamingResponse(response_stream, media_type="audio/mpeg")
    except Exception as e:
        return JSONResponse({"error": f"(Error al generar el audio): {str(e)}"}, status_code=500)

@app.post("/create-checkout-session")
async def create_checkout_session(service: str = Form(...), apodo: str = Form(...)):
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
        return JSONResponse({"error": f"Error al crear sesión de Stripe: {str(e)}"}, status_code=500)

@app.post("/access-code")
async def access_code(apodo: str = Form(...), code: str = Form(...), service: str = Form(...)):
    # Se ha corregido la variable de entorno de 'SECRET_CODE_NAME' a 'MAYROGA_ACCESS_CODE'.
    if code != os.getenv("MAYROGA_ACCESS_CODE"):
        return JSONResponse({"error": "Código de acceso incorrecto."}, status_code=403)

    users = load_users()
    if apodo not in users:
        users[apodo] = {"servicios": {}}
    if service not in users[apodo]["servicios"]:
        users[apodo]["servicios"][service] = {"sesiones_restantes": 0}

    # Aumentar las sesiones (por ejemplo, 10 sesiones gratis con el código)
    users[apodo]["servicios"][service]["sesiones_restantes"] += 10
    save_users(users)

    return JSONResponse({"message": "Acceso concedido.", "apodo": apodo, "service": service})

@app.get("/success")
async def success(request: Request, session_id: str, apodo: str, service: str):
    users = load_users()
    if apodo in users and users[apodo].get("session_id") == session_id:
        if service not in users[apodo]["servicios"]:
            users[apodo]["servicios"][service] = {"sesiones_restantes": 0}
        
        if service == "respuesta_rapida":
            users[apodo]["servicios"][service]["sesiones_restantes"] += 5
        elif service == "risoterapia":
            users[apodo]["servicios"][service]["sesiones_restantes"] += 1
        elif service == "horoscopo":
            users[apodo]["servicios"][service]["sesiones_restantes"] += 1
        
        save_users(users)
        return templates.TemplateResponse("success.html", {"request": request, "apodo": apodo, "service": service})
    
    return templates.TemplateResponse("index.html", {"request": request, "message": "Pago no válido o ya procesado."})

@app.post("/stripe-webhook")
async def stripe_webhook(request: Request):
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
