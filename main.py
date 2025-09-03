import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from firebase_admin import credentials, firestore, initialize_app
import google.generativeai as genai
import stripe

# Initialize Flask App
app = Flask(__name__)
CORS(app)

# Firebase initialization
# You must set your Firebase credentials as a JSON string in a Render environment variable
# called FIREBASE_CREDENTIALS.
try:
    cred_json = os.getenv("FIREBASE_CREDENTIALS")
    if not cred_json:
        raise ValueError("FIREBASE_CREDENTIALS environment variable is not set.")
    cred = credentials.Certificate(firestore.from_dict(json.loads(cred_json)))
    initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"Error al inicializar Firebase: {e}")
    # Consider removing app.run() and letting Gunicorn handle the errors in production
    # to avoid a blank page.

# Gemini API configuration
# Ensure GEMINI_API_KEY is set in your Render environment variables.
try:
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"Error al configurar la API de Gemini: {e}")

# Stripe configuration
# Ensure STRIPE_SECRET_KEY is set in your Render environment variables.
try:
    stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
    if not stripe_secret_key:
        raise ValueError("STRIPE_SECRET_KEY environment variable is not set.")
    stripe.api_key = stripe_secret_key
except Exception as e:
    print(f"Error al configurar Stripe: {e}")

@app.route("/")
def index():
    return "¡El backend está funcionando correctamente!"

@app.route("/generate", methods=["POST"])
def generate_text():
    try:
        data = request.json
        prompt = data.get("prompt")
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
            
        response = model.generate_content(prompt)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
