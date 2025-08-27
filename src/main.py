# src/main.py
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import openai
import stripe
import json

app = FastAPI()

# Configuración OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configuración Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Archivos estáticos y templates
app.mount("/static", StaticFiles(directory="static"), name="static")

# Función de respaldo usando JSON
def respaldo(tipo):
    try:
        if tipo == "medico":
            archivo = "data/behavior_guide.json"
        elif tipo == "enfermedades":
            archivo = "data/enfermedades.json"
        elif tipo == "urgencias":
            archivo = "data/urgencias.json"
        else:
            archivo = "data/behavior_guide.json"
        with open(archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)
        return datos.get("respuesta", "Respuesta de respaldo genérica")
    except:
        return "Respuesta de respaldo genérica"

# Página principal
@app.get("/", response_class=HTMLResponse)
async def index():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# Endpoint chat
@app.post("/chat")
async def chat(message: str = Form(...)):
    texto = message.lower()
    try:
        if "horóscopo" in texto:
            respuesta = "Tu horóscopo para hoy: ¡Hoy es un día lleno de energía positiva! 🌞"
        elif "risoterapia" in texto:
            respuesta = "Técnica del Bien (TDB): sonríe, respira profundo y piensa en algo positivo."
        elif "medico" in texto or "salud" in texto:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message}]
            )
            respuesta = completion.choices[0].message.content
        elif "emergencia" in texto:
            respuesta = respaldo("urgencias")
        else:
            respuesta = respaldo("medico")
    except Exception:
        if "horóscopo" in texto:
            respuesta = respaldo("medico")
        elif "risoterapia" in texto:
            respuesta = respaldo("medico")
        elif "emergencia" in texto:
            respuesta = respaldo("urgencias")
        else:
            respuesta = respaldo("enfermedades")
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
                    'unit_amount': 500,  # $5.00
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

# Ping rápido
@app.get("/ping")
async def ping():
    return {"message": "Servidor activo 🚀"}
