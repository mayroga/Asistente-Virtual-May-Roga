from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
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

# Página principal
@app.get("/", response_class=HTMLResponse)
async def index():
    with open(os.path.join(os.path.dirname(__file__), "../templates/index.html")) as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

# Endpoint de chat
@app.post("/chat")
async def chat(message: str = Form(...)):
    if "horóscopo" in message.lower():
        respuesta = "Tu horóscopo para hoy: ¡Un día lleno de energía positiva!"
    elif "risoterapia" in message.lower():
        respuesta = "Realiza la Técnica del Bien (TDB): sonríe, respira profundo y piensa en algo positivo."
    else:
        # Respaldo simple usando JSON
        import json
        try:
            with open(os.path.join(os.path.dirname(__file__), "../data/behavior_guide.json")) as f:
                data = json.load(f)
            respuesta = data["respuestas"][0]
        except:
            respuesta = "No se pudo generar respuesta. Intenta más tarde."
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
