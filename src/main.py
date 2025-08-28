from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import stripe
import os
import openai

# Variables de entorno
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Servicios disponibles
services = {
    "medico": {"name": "Asistente Virtual Médico", "price": 500},  # en centavos USD
    "risoterapia": {"name": "Sesión de Risoterapia", "price": 700},
    "horoscopo": {"name": "Horóscopo Personalizado", "price": 300}
}

# Página principal
@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "services": services})

# Crear sesión de pago Stripe
@app.post("/create-checkout-session")
async def create_checkout_session(service_id: str = Form(...), apodo: str = Form(...)):
    if service_id not in services:
        return JSONResponse({"error": "Servicio inválido"}, status_code=400)
    service = services[service_id]
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": f"{service['name']} - {apodo}"},
                "unit_amount": service['price'],
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=f"/chat?apodo={apodo}&service_id={service_id}",
        cancel_url="/"
    )
    return {"id": session.id}

# Chat con el asistente
@app.get("/chat")
async def chat_page(request: Request, apodo: str, service_id: str):
    if service_id not in services:
        return JSONResponse({"error": "Servicio inválido"}, status_code=400)
    return templates.TemplateResponse("chat.html", {"request": request, "apodo": apodo, "service": services[service_id]})

# Respuesta inteligente OpenAI
@app.post("/get-response")
async def get_response(apodo: str = Form(...), service_id: str = Form(...), user_input: str = Form(...)):
    if service_id not in services:
        return JSONResponse({"error": "Servicio inválido"}, status_code=400)
    
    prompt = f"Servicio: {services[service_id]['name']}\nApodo: {apodo}\nUsuario: {user_input}\nRespuesta:"
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        answer = f"Error al generar respuesta: {str(e)}"
    
    return {"answer": answer}
