from flask import Flask, render_template, request, jsonify 
from flask_cors import CORS
import stripe, os, openai, json

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
openai.api_key = os.environ.get("OPENAI_API_KEY")

# --- Código secreto desde Render ---
MAYROGA_ACCESS_CODE = os.environ.get("MAYROGA_ACCESS_CODE")

# --- Home ---
@app.route("/")
def home():
    return render_template("index.html")

# --- Unlock services ---
@app.route("/assistant-unlock", methods=["POST"])
def unlock():
    data = request.json
    if data.get("secret") == MAYROGA_ACCESS_CODE:
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

# --- Stream AI Assistant ---
@app.route("/assistant-stream-message", methods=["POST"])
def assistant_stream_message():
    data = request.json
    service = data.get("service")
    messages = data.get("messages", [])
    prompt = f"Asistente May Roga para {service}. Atiende con risoterapia, bienestar, TVid, consejos de vida, medicina verde.\nUsuario: {messages[-1]}\nAsistente:"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-5-mini",
            messages=[{"role":"user","content":prompt}],
            max_tokens=300
        )
        answer = response.choices[0].message.content
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer": f"Error AI: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
