from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import stripe

app = FastAPI()

# Configura tu clave secreta de Stripe
stripe.api_key = "TU_STRIPE_SECRET_KEY"

# Plantillas
templates = Jinja2Templates(directory="templates")

# Página principal
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Crear sesión de pago
@app.post("/create-checkout-session")
async def create_checkout_session(apodo: str = Form(...), servicio: str = Form(...)):
    try:
        # Precios de ejemplo
        precios = {
            "asistente_virtual": 500,  # $5.00
            "risoterapia": 1200,       # $12.00
            "horoscopo": 300           # $3.00
        }
        if servicio not in precios:
            return JSONResponse({"error": "Servicio inválido"}, status_code=400)

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": servicio},
                    "unit_amount": precios[servicio],
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{request.url.scheme}://{request.url.hostname}/?apodo={apodo}&servicio={servicio}",
            cancel_url=f"{request.url.scheme}://{request.url.hostname}/",
        )
        return JSONResponse({"url": session.url})
    except Exception as e:
        return JSONResponse({"error": str(e)})

# Servicio después del pago
@app.post("/get-service")
async def get_service(apodo: str = Form(...), servicio: str = Form(...)):
    mensajes = {
        "asistente_virtual": "Accediste al Asistente Virtual Médico. Disfruta tu sesión.",
        "risoterapia": "Bienvenido a tu sesión de Risoterapia y Bienestar Natural.",
        "horoscopo": "Aquí está tu horóscopo personalizado."
    }
    resultado = mensajes.get(servicio, "Servicio desconocido")
    return JSONResponse({"resultado": resultado})

# Chat con asistente
@app.post("/chat")
async def chat(apodo: str = Form(...), message: str = Form(...)):
    # Respuesta simple de ejemplo, puedes integrar GPT u otro motor aquí
    respuesta = f"{apodo}, tu mensaje fue recibido: {message}"
    return JSONResponse({"respuesta": respuesta})
