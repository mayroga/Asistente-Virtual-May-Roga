from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import stripe
import os
from langdetect import detect

# Configuración de Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

app = FastAPI(title="Medico Virtual May Roga")

# Montaje de static solo si existe
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Precios de servicios
SERVICIOS = {
    "asistente_virtual": {"precio": 500, "duracion": 8*60},  # $5 por 8 minutos
    "risoterapia": {"precio": 1200, "duracion": 10*60},      # $12 por 10 minutos
    "horoscopo": {"precio": 300, "duracion": 35}            # $3 por 35 seg
}

# Página principal
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head>
            <title>Medico Virtual May Roga</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { font-size: 18px; font-family: Arial, sans-serif; }
                h1 { font-size: 28px; }
                .subtitulo { font-size: 12px; color: gray; }
            </style>
        </head>
        <body>
            <h1>Asistente Virtual</h1>
            <div class="subtitulo">Medico Virtual May Roga - Informativo</div>
            <p>Elige un servicio e ingresa tu apodo antes de pagar para comenzar.</p>
        </body>
    </html>
    """

# Endpoint para crear pago
@app.post("/create-checkout-session")
async def create_checkout(apodo: str = Form(...), servicio: str = Form(...)):
    if servicio not in SERVICIOS:
        return JSONResponse({"error": "Servicio no válido"}, status_code=400)
    
    price = SERVICIOS[servicio]["precio"]
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': servicio.replace("_", " ").title()},
                    'unit_amount': price,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"https://medico-virtual-may-roga.onrender.com/service?apodo={apodo}&servicio={servicio}",
            cancel_url="https://medico-virtual-may-roga.onrender.com/",
        )
        return JSONResponse({"url": session.url})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# Servicio una vez pagado
@app.get("/service", response_class=HTMLResponse)
async def service(apodo: str, servicio: str):
    mensaje = ""
    
    if servicio == "asistente_virtual":
        mensaje = f"""
        <p>Hola {apodo}, soy tu Asistente Virtual.</p>
        <p>Este servicio es <b>informativo</b>. Te daré un diagnóstico único y sugerencias de tratamiento educativo.</p>
        """
    elif servicio == "risoterapia":
        mensaje = f"""
        <p>Hola {apodo}, bienvenido a tu sesión de Risoterapia basada en Técnicas de Vida.</p>
        <p>Disfruta de 10 minutos de ejercicios y bienestar natural.</p>
        """
    elif servicio == "horoscopo":
        mensaje = f"""
        <p>Hola {apodo}, aquí está tu horóscopo y consejo zodiacal de hoy (35 segundos de lectura).</p>
        """

    return f"""
    <html>
        <head>
            <title>{servicio.replace('_', ' ').title()}</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-size: 18px; font-family: Arial, sans-serif; }}
            </style>
        </head>
        <body>
            {mensaje}
            <p style="font-size:12px; color:gray;">
                Recuerda: Este servicio médico es solo <b>informativo</b>. No guarda información sensible y no reemplaza a un profesional de la salud.
            </p>
        </body>
    </html>
    """

# Detección de idioma
@app.post("/detect-lang")
async def detect_lang(text: str = Form(...)):
    try:
        idioma = detect(text)
        return {"idioma": idioma}
    except:
        return {"idioma": "desconocido"}
