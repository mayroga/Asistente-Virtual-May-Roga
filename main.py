from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# Initialize the Flask application
app = Flask(__name__)
# Enable CORS for all domains, which is necessary for the frontend to communicate with the backend
CORS(app)

# Mock Stripe and a simple chat assistant for demonstration.
# IMPORTANT: This is for demonstration only. In a real application, you would
# integrate with the Stripe API and a real chatbot service.

# Mock data for service pricing
SERVICES = {
    "risoterapia": {"name": "Risoterapia y Bienestar", "price": 1200},
    "horoscopo": {"name": "Horóscopo / Zodiaco", "price": 500},
    "respuesta_rapida": {"name": "Servicio Rápido", "price": 200},
}

@app.route("/create-checkout-session/", methods=["POST"])
def create_checkout_session():
    """
    Handles the request to create a Stripe checkout session.
    Mocks a successful payment and returns a redirect URL.
    """
    try:
        data = request.json
        service = data.get("service")
        
        if service not in SERVICES:
            return jsonify({"error": "Service not found"}), 404

        # In a real application, you would create a Stripe Checkout Session here.
        # This is a mock URL to simulate a successful payment redirection.
        # It redirects to the frontend with a 'success=true' parameter.
        checkout_url = "https://asistente-virtual-may-roga.onrender.com/?success=true"
        return jsonify({"url": checkout_url})

    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route("/chat/", methods=["POST"])
def chat():
    """
    Handles chat messages and provides a mock response.
    """
    try:
        data = request.json
        user_message = data.get("user_message")
        nickname = data.get("nickname")
        service = data.get("service")

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # This is a hardcoded mock response.
        # In a real application, you would use a large language model (LLM) here
        # to generate a dynamic response based on the user's message and the service.
        response_message = f"Hola {nickname}! Recibí tu mensaje: '{user_message}'. Gracias por usar el servicio de {SERVICES[service]['name']}."

        return jsonify({"assistant_message": response_message})
    
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == "__main__":
    # Get the port from the environment variable provided by Render, defaulting to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
