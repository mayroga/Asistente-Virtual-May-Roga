import os, stripe
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

# Claves de Stripe desde variables de entorno
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
stripe.api_key = STRIPE_SECRET_KEY

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# Rutas de templates y static
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Ruta raíz
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Crear sesión de pago
@app.post("/pay/create-session")
def create_session():
    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "Médico Virtual May Roga - Sesión"},
                    "unit_amount": 1500
                },
                "quantity": 1
            }],
            success_url=os.getenv("SUCCESS_URL", "https://example.com/success"),
            cancel_url=os.getenv("CANCEL_URL", "https://example.com/cancel"),
        )
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(400, str(e))

# Webhook Stripe
@app.post("/webhook-stripe")
async def webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        raise HTTPException(400, f"Webhook error: {e}")

    if event["type"] in ("checkout.session.completed", "payment_intent.succeeded"):
        print("✅ Pago confirmado, habilitar acceso de servicio.")

    return JSONResponse({"received": True})
