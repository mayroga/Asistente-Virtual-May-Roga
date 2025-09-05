import os
import stripe
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS

# Configuración base
app = Flask(__name__)
CORS(app)

# Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")  # en Render lo pones en Variables de Entorno
DOMAIN = os.environ.get("DOMAIN", "https://asistente-virtual-may-roga.onrender.com")

# Página principal
@app.route("/")
def index():
    return render_template("index.html")

# Página de chat
@app.route("/chat")
def chat():
    return render_template("may-roga-chat-assistant.html")

# Crear sesión de pago
@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    try:
        data = request.json
        price_id = data.get("priceId")

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[{
                "price": price_id,
                "quantity": 1
            }],
            success_url=f"{DOMAIN}/success",
            cancel_url=f"{DOMAIN}/cancel",
        )
        return jsonify({"url": checkout_session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Rutas de confirmación
@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/cancel")
def cancel():
    return render_template("cancel.html")

@app.route("/failure")
def failure():
    return render_template("failure.html")

# --- API de Chat (simplificada) ---
@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json
    message = data.get("message", "")
    if not message:
        return jsonify({"error": "Mensaje vacío"}), 400

    # Aquí podrías conectar con Google Generative AI, pero como demo:
    reply = f"Entendido: {message}. Estoy aquí para ayudarte con risoterapia y bienestar natural."
    return jsonify({"reply": reply})

# Arranque
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
