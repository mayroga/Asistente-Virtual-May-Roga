from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import stripe, os, json
import openai
import requests

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
openai.api_key = os.environ.get("OPENAI_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Código secreto queda como está en Render
SECRET_CODE = os.environ.get("MAYROGA_ACCESS_CODE")

# --- Home ---
@app.route("/")
def home():
    return render_template("index.html")

# --- Unlock services ---
@app.route("/assistant-unlock", methods=["POST"])
def unlock():
    data = request.json
    if data.get("secret") == SECRET_CODE:
        return jsonify({"success": True})
    return jsonify({"success": False})

# --- Crear checkout Stripe ---
@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    data = request.json
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': data['product']},
                    'unit_amount': int(float(data['amount'])*100)
                },
                'quantity': 1
            }],
            mode='payment',
            success_url="https://yourdomain.com/success",
            cancel_url="https://yourdomain.com/cancel"
        )
        return jsonify({"url": session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# --- Stream AI Assistant con fallback OpenAI → Gemini ---
@app.route("/assistant-stream-message", methods=["POST"])
def assistant_stream_message():
    data = request.json
    service = data.get("service")
    messages = data.get("messages", [])
    prompt = f"Asistente May Roga para {service}. Atiende con risoterapia, bienestar, TVid, consejos de vida, medicina verde.\nUsuario: {messages[-1]}\nAsistente:"

    # Intentar OpenAI primero
    try:
        response = openai.chat.completions.create(
            model="gpt-5-mini",
            messages=[{"role":"user","content":prompt}],
            max_completion_tokens=300
        )
        answer = response.choices[0].message.content
        return jsonify({"answer": answer})
    except Exception as e_openai:
        # Si falla, fallback a Gemini
        try:
            gemini_url = "https://api.generativeai.google/v1beta2/models/text-bison-001:generate"
            headers = {"Authorization": f"Bearer {GEMINI_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "prompt": {"text": prompt},
                "temperature": 0.7,
                "maxOutputTokens": 300
            }
            res = requests.post(gemini_url, headers=headers, json=payload)
            res_json = res.json()
            answer = res_json.get("candidates", [{}])[0].get("content", "Lo siento, no pude generar respuesta.")
            return jsonify({"answer": answer})
        except Exception as e_gemini:
            return jsonify({"answer": f"Error AI: OpenAI [{str(e_openai)}], Gemini [{str(e_gemini)}]"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
