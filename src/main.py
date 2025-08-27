from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import json
import openai
import stripe
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configuración OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configuración Stripe
stripe.api_key = os.getenv("STRIPE_API_KEY")

# Montar carpeta static correctamente
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "../static")), name="static")

# Cargar JSON de respaldo
data_paths = {
    "behavior_guide": os.path.join(os.path.dirname(__file__), "../data/behavior_guide.json"),
    "enfermedades": os.path.join(os.path.dirname(__file__), "../data/enfermedades.json"),
    "urgencias": os.path.join(os.path.dirname(__file__), "../data/urgencias.json")
}

backups = {}
for key, path in data_paths.items():
    try:
        with open(path, "r", encoding="utf-8") as f:
            backups[key] = json.load(f)
    except Exception as e:
        backups[key] = {"respuestas": [f"No se pudo cargar {key}"]}
        print(f"Error cargando {key}: {e}")

# Página principal
@app.get("/", response_class=HTMLResponse)
async def index():
    with open(os.path.join(os.path.dirname(__file__), "../templates/index.html")) as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

# Endpoint de chat
@app.post("/chat")
async def chat(message: str = Form(...)):
    msg_lower = message.lower()
    
    # Respuestas por botones fijos
    if "horóscopo" in msg_lower:
        return JSONResponse({"respuesta": "Tu horóscopo para hoy: ¡Un día lleno de energía positiva!"})
    elif "risoterapia" in msg_lower:
        return JSONResponse({"respuesta": "Realiza la Técnica del Bien (TDB): sonríe, respira profundo y piensa en algo positivo."})
    elif "emergencia" in msg_lower:
        return JSONResponse({"respuesta": "Si es una emergencia médica real, llama al 911 inmediatamente."})
    
    # Intentar OpenAI
    respuesta = None
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}]
        )
        respuesta = completion.choices[0].message.content
    except Exception as e:
        print(f"OpenAI no respondió: {e}")

    # Si falla OpenAI, usar respaldo automático
    if not respuesta or respuesta.strip() == "":
        # Elegir respaldo según palabra clave
        if "enfermedad" in msg_lower:
            respuesta = backups["enfermedades"]["respuestas"][0]
        elif "urgencia" in msg_lower:
            respuesta = backups["urgencias"]["respuestas"][0]
        else:
            respuesta = backups["behavior_guide"]["respuestas"][0]

    return JSONResponse({"respuesta": respuesta})

# Endpoint de pago simple
@app.post("/create-checkout-session")
async def create_checkout():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'Servicio Medico Virtual 24/7'},
                    'unit_amount': 500,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=os.getenv("SUCCESS_URL"),
            cancel_url=os.getenv("CANCEL_URL"),
        )
        return JSONResponse({"url": session.url})
    except Exception as e:
        return JSONResponse({"error": str(e)})

# Ping de prueba
@app.get("/ping")
async def ping():
    return {"message": "Servidor activo 🚀"}
