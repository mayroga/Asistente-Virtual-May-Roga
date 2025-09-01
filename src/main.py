import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import stripe

# Inicializa la aplicación de FastAPI
app = FastAPI()

# Configura CORS para permitir solicitudes desde tu frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configura Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Configura OpenAI
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configura Firebase
try:
    firebase_config = os.getenv("FIREBASE_CONFIG")
    if not firebase_config:
        raise ValueError("FIREBASE_CONFIG environment variable is not set.")
    
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    # Puedes manejar el error aquí o simplemente dejar que la aplicación falle al iniciar
    raise

class Message(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/create-checkout-session")
async def create_checkout_session(data: Message):
    try:
        # Aquí puedes usar el mensaje para generar una descripción del producto
        # usando el modelo de lenguaje de OpenAI.
        prompt = f"Crear un nombre de producto corto para esta descripción de cliente: {data.message}. No incluyas información de precio o moneda."
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=20
        )
        product_name = response.choices[0].message.content.strip()

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product_name,
                    },
                    'unit_amount': 2000, # $20.00
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url="https://medico-virtual-may-roga.onrender.com/success",
            cancel_url="https://medico-virtual-may-roga.onrender.com/cancel",
        )
        return {"sessionId": session.id}
    except Exception as e:
        print(f"Error creating checkout session: {e}")
        return {"error": str(e)}, 500
