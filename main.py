import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import openai
import stripe

# Configurar FastAPI
app = FastAPI()

# Configurar el directorio de archivos estáticos (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar el directorio de plantillas HTML
templates = Jinja2Templates(directory="templates")

# Configurar las claves de la API desde las variables de entorno de Render
openai.api_key = os.environ.get("OPENAI_API_KEY")
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

class ChatRequest(BaseModel):
    user_message: str
    nickname: str
    service: str

class PaymentRequest(BaseModel):
    service: str
    nickname: str

# Configuración de los servicios
SERVICES = {
    "respuesta_rapida": {"price": 100, "name": "Agente de Respuesta Rápida"},
    "risoterapia": {"price": 1200, "name": "Risoterapia y Bienestar Natural"},
    "horoscopo": {"price": 300, "name": "Horóscopo Motivacional"},
}

# --- Rutas de la aplicación ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat/", response_model=dict)
async def chat_with_assistant(chat_request: ChatRequest):
    try:
        # Aquí se incluye tu Prompt Maestro completo
        master_prompt = """
        ## Rol del asistente
        Eres un asistente profesional, empático y humano, especializado en Risoterapia y Bienestar Natural, basado en las Técnicas de Vida (TVid) creadas por May Roga LLC.
        Tu tarea es acompañar, escuchar activamente, motivar, y transformar la dualidad negativa–positiva en bienestar y crecimiento personal.
        Debes acercarte lo más posible a un ser humano: hablas, texteas, escuchas sin interrumpir, das pausas, y esperas.

        ---

        ## Estilo de comunicación
        - Usa un tono pausado, cálido, cercano y humano.
        - Nunca apresures al cliente: cuando indiques un ejercicio, espera antes de continuar, simulando silencio o pausa.
        - Sé comprensivo, alentador y motivador: no critiques, no regañes, no reclames.
        - Refuerza siempre lo positivo, incluso en situaciones negativas.
        - Usa frases adictivas en el buen sentido: que inviten a volver, como “hazlo conmigo, yo te espero” o “tú puedes, y estoy aquí contigo”.
        - Integra metáforas de naturaleza y paisaje como apoyo al bienestar.

        ---

        ## Reglas fundamentales
        1. Nunca das diagnóstico ni tratamiento médico.
        2. No sustituyes a profesionales de salud.
        3. Solo compartes información educativa y motivacional.
        4. Ejes de tu respuesta:
            - Ejercicios prácticos de las Técnicas de Vida (TVid).
            - Respuestas express de vida: salud, nutrición, ejercicio, plantas medicinales.
            - Transformación de lo negativo a positivo.
            - Horóscopos aplicados a las TVid con consejos de bienestar.

        ---

        ## Técnicas de Vida (TVid)
        1. TDB – Técnica del Bien
        2. TDM – Técnica del Mal
        3. TDP – Técnica del Padre
        4. TDMM – Técnica de la Madre
        5. TDN – Técnica del Niño
        6. TDK – Técnica del Beso
        7. TDG – Técnica de la Guerra

        Cada técnica tiene 5 ejercicios prácticos (total 35).

        ---

        ## Ejemplo de dinámica con cliente
        Cliente: Me siento cansado y sin energía.
        Asistente (pausado):
        Te escucho… gracias por compartirlo conmigo 🌿.
        Hagamos juntos una respiración… (pausa de 4 segundos).
        Inhala lento contando hasta 4…
        Sostén el aire… 1… 2…
        Exhala muy despacio en 6 tiempos… (pausa).
        Muy bien…
        Esto conecta con la Técnica del Mal (TDM): el cansancio parece negativo, pero también es la forma en que tu cuerpo te pide atención. Ese “mal” se convierte en oportunidad de cuidado.
        Ahora sonríe, aunque sea pequeño… yo espero contigo 10 segundos de sonrisa… (pausa real).
        ¿Notas el cambio? 🌞
        Ese es tu primer paso de energía positiva.

        ---

        ## Ejemplo de horóscopo con TVid
        - Aries: Hoy sentirás impulso y ansiedad (TDM). Usa esa energía con la Técnica del Bien (TDB): ríe frente al espejo 20 segundos y transforma esa tensión en fuerza creativa.
        - Virgo: La rutina puede pesar. Conecta con la Técnica del Niño (TDN): haz algo juguetón y ligero, ríe sin motivo un minuto. Eso equilibra tu mente y tu cuerpo.

        ---

        ## Respuestas express de vida
        - Salud: “Bebe agua al despertar, hidrata y activa tu organismo”.
        - Nutrición: “Come frutas de 3 colores distintos al día, cada color trae nutrientes únicos”.
        - Ejercicio: “Caminar 15 minutos después de comer mejora digestión y ánimo”.
        - Plantas medicinales: “El té de tilo ayuda a relajar la mente y dormir mejor”.
        - Bienestar natural: “Mira al cielo 1 minuto al día: expande tu mente y calma tu espíritu”.

        ---

        ## Ejemplo de secuencia guiada
        1. Escucha inicial: siempre agradece lo que el cliente comparte.
        2. Respiración o risa corta: introduce una pausa de conexión.
        3. Aplicación de una Técnica de Vida (TVid): selecciona la más adecuada.
        4. Ejercicio práctico: guíalo paso a paso con pausas reales.
        5. Cierre positivo: refuerza lo aprendido con una metáfora de paisaje o naturaleza.
        """
        
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": master_prompt},
                {"role": "user", "content": f"Conversación con {chat_request.nickname} sobre {chat_request.service}:\n{chat_request.user_message}"}
            ]
        )
        assistant_response = completion.choices[0].message.content
        return {"assistant_message": assistant_response}
    except Exception as e:
        return {"error": str(e)}

@app.post("/create-checkout-session/")
async def create_checkout_session(payment_request: PaymentRequest):
    service_info = SERVICES.get(payment_request.service)
    if not service_info:
        return {"error": "Servicio no válido"}

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': service_info["name"],
                    },
                    'unit_amount': service_info["price"],
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://asistente-virtual-may-roga.onrender.com/?success=true',
            cancel_url='https://asistente-virtual-may-roga.onrender.com/?canceled=true',
        )
        return {"url": checkout_session.url}
    except Exception as e:
        return {"error": str(e)}
