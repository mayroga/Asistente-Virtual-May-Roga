from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import stripe
import os

# Configuración de Stripe (pon tu clave secreta aquí)
stripe.api_key = "TU_STRIPE_SECRET_KEY"

app = FastAPI()

# Montar static si existe (opcional)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Precios y servicios
SERVICIOS = {
    "asistente_virtual": {"nombre": "Asistente Virtual", "duracion": "8 min", "precio": 500},
    "risoterapia": {"nombre": "Risoterapia", "duracion": "10 min", "precio": 1200},
    "horoscopo": {"nombre": "Horóscopo", "duracion": "35 seg", "precio": 300},
}

@app.post("/create-checkout-session")
async def create_checkout_session(apodo: str = Form(...), servicio: str = Form(...)):
    if servicio not in SERVICIOS:
        return JSONResponse({"error": "Servicio no válido"}, status_code=400)

    item = SERVICIOS[servicio]
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"{item['nombre']} - {item['duracion']}"
                    },
                    "unit_amount": item['precio'],
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{os.getenv('SUCCESS_URL', 'http://localhost:10000')}?apodo={apodo}&servicio={servicio}",
            cancel_url=f"{os.getenv('CANCEL_URL', 'http://localhost:10000')}",
        )
        return JSONResponse({"url": checkout_session.url})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/get-service")
async def get_service(apodo: str = Form(...), servicio: str = Form(...)):
    if servicio not in SERVICIOS:
        return JSONResponse({"resultado": "Servicio no encontrado"})

    item = SERVICIOS[servicio]

    # Mensaje personalizado según servicio
    if servicio == "asistente_virtual":
        resultado = f"Hola {apodo}, tu Asistente Virtual te brindará orientación médica informativa de manera profesional."
    elif servicio == "risoterapia":
        resultado = f"Hola {apodo}, disfruta de tu sesión de Risoterapia basada en las Técnicas de Vida, ¡a reír y sentir bienestar!"
    elif servicio == "horoscopo":
        resultado = f"Hola {apodo}, aquí tienes tu lectura de Horóscopo y consejos astrológicos del día."

    return JSONResponse({"resultado": resultado})

# Ruta raíz opcional
@app.get("/")
async def root():
    return {"message": "Bienvenido al Medico Virtual May Roga - usa el front-end para acceder a los servicios"}
