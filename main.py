import os
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import stripe
import firebase_admin
from firebase_admin import credentials, firestore
from google.generativeai.client import get_default_client

# --- Inicialización de Flask ---
app = Flask(__name__)
CORS(app)

# --- Inicialización de Stripe ---
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# --- Inicialización de Firebase ---
firebase_config_json = os.environ.get("__firebase_config__")
if firebase_config_json:
    cred = credentials.Certificate(json.loads(firebase_config_json))
    firebase_admin.initialize_app(cred)
db = firestore.client()

# --- Inicialización cliente AI ---
client_ai = get_default_client()

# --- Rutas ---
@app.route("/validate-access-code", methods=["POST"])
def validate_access_code():
    data = request.json
    code = data.get("code", "")
    # Validación simple (puedes mejorarla con Firestore)
    allowed_codes = ["ABC123", "MAYROGA2025"]
    if code in allowed_codes:
        return jsonify({"valid": True})
    return jsonify({"valid": False}), 403

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    data = request.json
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=data.get("line_items", []),
            success_url=data.get("success_url", ""),
            cancel_url=data.get("cancel_url", "")
        )
        return jsonify({"url": session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/assistant-message", methods=["POST"])
def assistant_message():
    data = request.json
    user_text = data.get("message", "")
    
    # --- Detección automática de idioma ---
    language = detect_language(user_text)

    # --- Generar respuesta usando TVid ---
    response_text = generate_tvid_response(user_text, language)

    # --- Simular tiempos de interacción ---
    time.sleep(1.2)  # pausa antes de responder
    return jsonify({"response": response_text, "language": language})

# --- Funciones auxiliares ---
def detect_language(text):
    # Detectar idioma simple basado en caracteres
    if any("\u0400" <= c <= "\u04FF" for c in text):  # cirílico
        return "ru"
    elif any("\u4E00" <= c <= "\u9FFF" for c in text):  # chino
        return "zh"
    elif any(c.isalpha() for c in text) and all(ord(c) < 128 for c in text):
        return "en"
    else:
        return "es"

def generate_tvid_response(user_text, language):
    """
    Aquí aplicamos las TVid de May Roga LLC.
    Se analiza el texto del usuario y se devuelve un mensaje positivo
    basado en la dualidad negativa/positiva y las técnicas: TDB, TDM, TDP, TDMM, TDN, TDK, TDG.
    """
    # Ejemplo básico de respuesta
    if "triste" in user_text.lower() or "mal" in user_text.lower():
        base_response = "Vamos a transformar eso en algo positivo, paso a paso 🌿."
    else:
        base_response = "¡Excelente! Mantén esa energía positiva 🌟."

    # Adaptar según idioma
    if language == "en":
        base_response = "Let's transform this into something positive, step by step 🌿." if "triste" in user_text.lower() else "Great! Keep that positive energy 🌟."
    elif language == "ru":
        base_response = "Давайте постепенно превратим это во что-то позитивное 🌿." if "triste" in user_text.lower() else "Отлично! Сохраняйте этот позитивный настрой 🌟."
    # más idiomas se pueden agregar

    return base_response

# --- Arranque de la app ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
