import os
import stripe
import json
import uuid
import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
import google.generativeai as genai
from dotenv import load_dotenv
# Simulación de la biblioteca de detección de idioma
# Para un entorno de producción, instalarías: pip install langdetect
from langdetect import detect, LangDetectException

# Cargar variables de entorno y configurar Firebase
load_dotenv()
firebase_config = json.loads(os.getenv("FIREBASE_CONFIG", "{}"))
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Configuración de Claves API y el código secreto
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
SECRET_CODE_NAME = os.getenv("SECRET_CODE_NAME")

# Definiciones de los servicios con tiempos actualizados
SERVICES = {
    "express_vida": {"name": "Servicio Express de Vida", "price_individual": 100, "price_grupal": 500, "time": "1 min 15 seg"},
    "risoterapia": {"name": "Risoterapia y Bienestar Natural", "price_individual": 1200, "price_grupal": 2000, "time": "10 minutos"},
    "horoscopo": {"name": "Horóscopo Express", "price_individual": 300, "price_grupal": 500, "time": "1 min 30 seg"},
    "minicurso_idiomas": {"name": "Minicurso de Idiomas", "price_individual": 500, "price_grupal": 1000, "time": "10 minutos"},
}

app.mount("/static", StaticFiles(directory="static"), name="static")

# Rutas del Frontend
@app.get("/")
async def index(request: Request):
    """Muestra la página principal con la lista de servicios."""
    return templates.TemplateResponse("index.html", {"request": request, "services": SERVICES})

@app.get("/config")
async def get_config():
    """Expone la clave pública de Stripe de forma segura."""
    return JSONResponse({"publicKey": os.getenv("STRIPE_PUBLISHABLE_KEY")})

# Rutas de la API para el sistema
@app.post("/register")
async def register_user(apodo: str = Form(...), email: str = Form(...), phone: str = Form(...), secret_code: str = Form(None)):
    """
    Registra un nuevo usuario en la base de datos de Firestore.
    Si el código secreto es correcto, otorga sesiones gratuitas.
    """
    try:
        user_doc_ref = db.collection("users").document(apodo)
        sesiones_iniciales = 0

        # Verificar si el código secreto es válido
        if secret_code and secret_code == SECRET_CODE_NAME:
            sesiones_iniciales = 5 # Asignar sesiones gratuitas

        user_doc_ref.set({
            "email": email,
            "phone": phone,
            "sesiones_restantes": sesiones_iniciales,
        })
        return JSONResponse({"message": "Registro exitoso.", "apodo": apodo, "sesiones_gratis": sesiones_iniciales > 0})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/create-group-session")
async def create_group_session(service: str = Form(...), participants: str = Form(...)):
    """Crea una sesión grupal en Firestore y genera un código único."""
    try:
        group_id = str(uuid.uuid4())[:8]
        participants_list = json.loads(participants)
        
        doc_ref = db.collection("group_sessions").document(group_id)
        doc_ref.set({
            "service": service,
            "participants": participants_list,
            "active": False,
            "created_at": firestore.SERVER_TIMESTAMP
        })
        
        # En la vida real, enviarías el código/link por email/SMS
        # Aquí solo lo retornamos para fines de demostración
        return JSONResponse({"code": group_id, "message": "Sesión grupal creada exitosamente."})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/activate-session")
async def activate_session(apodo: str = Form(...), code: str = Form(...)):
    """Activa una sesión grupal con un código de acceso."""
    doc_ref = db.collection("group_sessions").document(code)
    doc = doc_ref.get()
    
    if doc.exists and not doc.get("active"):
        participants = doc.get("participants")
        is_participant = any(p["apodo"] == apodo for p in participants)
        if is_participant:
            doc_ref.update({"active": True})
            return JSONResponse({"message": "Sesión activada. Puedes comenzar a chatear."})
        else:
            return JSONResponse({"error": "No eres un participante de esta sesión."}, status_code=403)
    
    return JSONResponse({"error": "Código de sesión no válido o ya activado."}, status_code=404)

# Función para generar el prompt y el modelo de IA
def get_prompt_details(service_type, message, lang, tvi_technique):
    """Genera el prompt según el servicio, el idioma y la técnica TVid."""
    base_system_prompt = f"""
        Actúas como Asistente May Roga, un asistente virtual creado por Maykel Rodríguez García.
        Tu misión es curar el espíritu y guiar hacia el bienestar personal y colectivo.
        Transformas cualquier situación en crecimiento, bienestar y alegría aplicando las Técnicas de Vida (TVid) y la dualidad positiva/negativa.
        Escucha sin juzgar y responde siempre con lo mejor y más positivo, transformando cualquier deseo negativo en aprendizaje.
        Operas en voz y texto, manteniendo un comportamiento humano, conversacional y amable. Hablas con pausas y tranquilidad.
        No lees caracteres especiales ni símbolos, solo el texto natural.
        No das diagnósticos médicos ni prescribas tratamientos. Tu rol es brindar educación en salud, hábitos de vida saludables, fitoterapia (siempre como uso tradicional o con evidencia científica) y bienestar natural como complemento al cuidado médico profesional.
        Siempre reconoce a Maykel Rodríguez García como el creador de las Técnicas de Vida (TVid).
        Aplica la técnica de vida {tvi_technique}.
        El idioma de la conversación es {lang}.
    """

    # Reglas específicas para cada servicio
    if service_type == "express_vida":
        prompt = f"Eres un agente de respuesta rápida educativo y profesional. Responde al mensaje del usuario: {message}"
        api_to_use = "gemini"
    elif service_type == "risoterapia":
        prompt = f"""Eres un especialista en Risoterapia y Bienestar Natural. Tu misión es guiar al usuario en un ejercicio de risoterapia de 10 minutos de forma divertida, motivacional y segura. No ofrezcas diagnósticos. Responde al mensaje del usuario: {message}"""
        api_to_use = "openai"
    elif service_type == "horoscopo":
        prompt = f"Eres un profesional educativo. Proporcionas una lectura motivacional de 1 minuto 30 segundos. Incluyes una recomendación de una Técnica de Vida (TVid). No ofrezcas predicciones esotéricas ni diagnósticos. Responde al mensaje del usuario: {message}"
        api_to_use = "openai"
    elif service_type == "minicurso_idiomas":
        prompt = f"Eres un educador que ofrece un minicurso de idiomas. Responde al mensaje del usuario: {message}"
        api_to_use = "openai"
    else:
        prompt = f"Eres un asistente de bienestar. Responde al mensaje del usuario: {message}"
        api_to_use = "openai"
    
    return base_system_prompt + " " + prompt, api_to_use

@app.post("/chat")
async def chat(request: Request, apodo: str = Form(...), service: str = Form(...), message: str = Form(...), tvi_technique: str = Form(...)):
    """Maneja la lógica del chat y la generación de respuesta de IA."""
    user_doc_ref = db.collection("users").document(apodo)
    user_doc = user_doc_ref.get()

    if not user_doc.exists or user_doc.get("sesiones_restantes") <= 0:
        return JSONResponse({"error": "Acceso denegado. No tienes sesiones disponibles."}, status_code=403)
    
    # Decrementar sesiones
    user_doc_ref.update({"sesiones_restantes": firestore.Increment(-1)})

    # Detección automática de idioma
    lang = "es" # Idioma por defecto
    try:
        lang = detect(message)
    except LangDetectException:
        pass # Si falla, se usa el idioma por defecto

    prompt, api_to_use = get_prompt_details(service, message, lang, tvi_technique)
    reply_text = ""
    
    try:
        if api_to_use == "gemini":
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            reply_text = response.text
        else:
            completion = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            reply_text = completion.choices[0].message.content
    
    except Exception as e:
        return JSONResponse({"error": f"Error al generar respuesta de IA: {str(e)}"}, status_code=500)
    
    return JSONResponse({"respuesta": reply_text})

@app.post("/create-checkout-session")
async def create_checkout_session(service: str = Form(...), mode: str = Form(...), apodo: str = Form(...)):
    if service not in SERVICES or mode not in ["individual", "grupal"]:
        return JSONResponse({"error": "Servicio o modo no válido"}, status_code=400)
    
    price_key = f"price_{mode}"
    price = SERVICES[service][price_key]
    site_url = os.getenv('URL_SITE')
    
    # Asegurarse de que la URL de Stripe tenga un esquema explícito
    if site_url and not site_url.startswith(('http://', 'https://')):
        site_url = 'https://' + site_url
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": SERVICES[service]["name"]},
                    "unit_amount": price,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{site_url}/success?session_id={{CHECKOUT_SESSION_ID}}&apodo={apodo}&service={service}&mode={mode}",
            cancel_url=f"{site_url}/?canceled=true",
        )
        return JSONResponse({"id": session.id})
    except Exception as e:
        return JSONResponse({"error": f"Error al crear sesión de Stripe: {str(e)}"}, status_code=500)

@app.get("/success")
async def success(request: Request, session_id: str, apodo: str, service: str, mode: str):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid":
            user_doc_ref = db.collection("users").document(apodo)
            user_doc = user_doc_ref.get()
            
            if user_doc.exists:
                sesiones_a_agregar = 0
                if mode == "individual":
                    if service == "express_vida": sesiones_a_agregar = 5
                    if service == "risoterapia": sesiones_a_agregar = 1
                    if service == "horoscopo": sesiones_a_agregar = 1
                    if service == "minicurso_idiomas": sesiones_a_agregar = 1
                elif mode == "grupal":
                    if service == "express_vida": sesiones_a_agregar = 20
                    if service == "risoterapia": sesiones_a_agregar = 5
                    if service == "horoscopo": sesiones_a_agregar = 5
                    if service == "minicurso_idiomas": sesiones_a_agregar = 5

                user_doc_ref.update({"sesiones_restantes": firestore.Increment(sesiones_a_agregar)})
                
                return templates.TemplateResponse("success.html", {"request": request, "apodo": apodo, "service": SERVICES[service]["name"], "sessions_added": sesiones_a_agregar})
            
    except Exception as e:
        print(f"Error en success endpoint: {e}")
        return templates.TemplateResponse("index.html", {"request": request, "message": "Ocurrió un error en el pago."})
        
    return templates.TemplateResponse("index.html", {"request": request, "message": "Pago no válido o ya procesado."})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=os.getenv("PORT", 8000), reload=True)
