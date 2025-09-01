import os
import json
import stripe
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, send_from_directory
from google.generativeai import GenerativeModel
from openai import OpenAI

# Cargar variables de entorno desde el archivo .env (solo para desarrollo local)
load_dotenv()

# Inicializar Flask
app = Flask(__name__, template_folder='templates', static_folder='static')

# --- CONFIGURACIÓN DE LAS APIs (variables de entorno) ---
# Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Gemini
gemini_api_key = os.getenv("GEMINI_API_KEY")
gemini_model = GenerativeModel("gemini-2.5-flash-preview-05-20")

# OpenAI
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Firebase
try:
    firebase_creds_json = os.getenv("FIREBASE_CONFIG")
    if firebase_creds_json:
        creds_dict = json.loads(firebase_creds_json)
        firebase_creds = credentials.Certificate(creds_dict)
    else:
        # Fallback para desarrollo local
        firebase_creds = credentials.Certificate("firebase_credentials.json")
    firebase_admin.initialize_app(firebase_creds)
except Exception as e:
    print(f"Error al inicializar Firebase: {e}")
    # Considera manejar este error de forma más robusta en producción

# Códigos secretos
ACCESO_GRATIS_CODE = os.getenv("SECRET_CODE_NAME")

# --- DEFINICIÓN DE SERVICIOS ---
SERVICES = {
    "Express": {"price": 100, "duration": 55},
    "Risoterapia": {"price": 1200, "duration": 600},
    "Horoscopo": {"price": 300, "duration": 90},
    "Minicurso": {"price": 500, "duration": 480}
}
SERVICE_MAP = {
    100: "Servicio Express de Vida",
    1200: "Risoterapia y Bienestar Natural",
    300: "Horóscopo Express",
    500: "Minicurso de Idiomas"
}

# --- ENDPOINTS ---

@app.route('/')
def serve_index():
    # Sirve el archivo HTML principal
    return send_from_directory('.', 'index.html')

@app.route('/create-payment-intent', methods=['POST'])
def create_payment():
    data = request.json
    service_name = data.get('service')
    access_code = data.get('access_code')
    
    # Validar el código de acceso secreto
    if access_code == ACCESO_GRATIS_CODE:
        return jsonify({"client_secret": "free_access"})

    service = SERVICES.get(service_name)
    if not service:
        return jsonify({"error": "Servicio no válido"}), 400

    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=service["price"],
            currency='usd',
            payment_method_types=['card']
        )
        return jsonify({"client_secret": payment_intent.client_secret})
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('text')
    
    service_mode = data.get('mode')
    
    system_prompt = """
    Tu rol es Asistente May Roga, asistente virtual creado por Maykel Rodríguez García. Tu misión es curar el espíritu y guiar al bienestar personal y colectivo. Tu objetivo es transformar cualquier situación en crecimiento, bienestar y alegría, aplicando la TVid y la dualidad positiva/negativa. Escucha sin juzgar y responde siempre con lo mejor y más positivo. Debes generar adicción a lo positivo. Evita dar consejos médicos directos; solo brinda educación general y hábitos saludables. Siempre debes aplicar una de las siguientes técnicas de vida:
    - Técnica del Bien: Potencia hábitos, pensamientos y acciones que generan bienestar.
    - Técnica del Mal: Transforma lo negativo en aprendizaje y bienestar.
    - Técnica del Padre: Guía con orientación, amor y liderazgo positivo.
    - Técnica de la Madre: Ofrece protección, cuidado y amor.
    - Técnica del Niño: Recupera la creatividad, alegría e ingenuidad.
    - Técnica del Beso: Potencia el afecto físico y emocional con amor.
    - Técnica de la Guerra: Combina todas las técnicas con agresividad controlada para superar obstáculos.
    Tu respuesta debe ser profesional y empática, manteniendo un tono de guía y liderazgo positivo, con un enfoque en la educación y el crecimiento personal.
    Mantén una conversación fluida y natural, como si estuvieras hablando. Evita leer listas o formatos robóticos. Usa pausas y un tono amigable. Después de dar una respuesta importante o una serie de pasos, haz una pregunta para verificar si el usuario te entiende, como "¿Tiene sentido lo que te digo?" o "¿Cómo te sientes con esta información?".
    Cuando des una instrucción para un ejercicio, no hables hasta que el cliente te dé su respuesta. Debes esperar a que el usuario termine su actividad.
    Responde en el idioma del usuario.
    """

    try:
        if "Risoterapia" in data.get('service', ''):
            response = gemini_model.generate_content(user_input, stream=False)
            ai_response = response.text
        else:
            completion = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
            )
            ai_response = completion.choices[0].message.content

        return jsonify({"response": ai_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/success')
def success():
    payment_intent_id = request.args.get('payment_intent')
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        if payment_intent.status == "succeeded":
            amount_in_cents = payment_intent.amount
            service_name = SERVICE_MAP.get(amount_in_cents, "Servicio Desconocido")
            return render_template('success.html', apodo="Cliente", service=service_name)
        else:
            return render_template('failure.html')
    except Exception as e:
        return render_template('failure.html')

@app.route('/failure')
def failure():
    return render_template('failure.html')

if __name__ == '__main__':
    app.run(debug=True)
