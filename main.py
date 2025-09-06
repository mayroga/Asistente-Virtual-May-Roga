import os, json, tempfile, atexit
from time import sleep
from flask import Flask, jsonify, request, Response, send_file
from flask_cors import CORS
import stripe
import openai

app = Flask(__name__)
CORS(app)

# --- Config ---
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
YOUR_DOMAIN = os.environ.get("URL_SITE")
ACCESS_CODE = os.environ.get("MAYROGA_ACCESS_CODE")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_KEY

audio_cache = {}

@atexit.register
def cleanup_files():
    for f in audio_cache.values():
        try: os.remove(f)
        except: pass

# --- Inicio ---
@app.route("/")
def home(): return "Asistente Virtual May Roga activo"

# --- Desbloqueo ---
@app.route("/assistant-unlock", methods=["POST"])
def unlock_services():
    data = request.json
    if data.get("secret") == ACCESS_CODE: return jsonify({"success": True})
    return jsonify({"success": False}), 403

# --- Stripe ---
@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    data = request.json
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency':'usd',
                'product_data': {'name': data['product']},
                'unit_amount': int(data['amount']*100)
            },
            'quantity': 1
        }],
        mode='payment',
        success_url=YOUR_DOMAIN + '/success.html',
        cancel_url=YOUR_DOMAIN + '/cancel.html'
    )
    return jsonify({"url": session.url})

# --- Generar audio opcional ---
def generate_audio(text):
    try:
        r = openai.audio.speech.create(model="tts-1", voice="alloy", input=text)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        r.stream_to_file(tmp.name)
        tmp.close()
        audio_cache[os.path.basename(tmp.name)] = tmp.name
        return os.path.basename(tmp.name)
    except: return None

@app.route("/generate-voice")
def generate_voice():
    text = request.args.get("text")
    if not text: return "Texto no recibido",400
    filename = generate_audio(text)
    if filename: return jsonify({"file": filename, "url": f"/get-audio?file={filename}"})
    return "Error generando audio",500

@app.route("/get-audio")
def get_audio():
    f = request.args.get("file")
    if f in audio_cache: return send_file(audio_cache[f], mimetype="audio/mpeg")
    return "Archivo no encontrado",404

# --- SSE ---
@app.route("/assistant-stream")
def assistant_stream():
    service = request.args.get("service")
    secret = request.args.get("secret")
    if service=="Todos los servicios desbloqueados" and secret!=ACCESS_CODE: return "Forbidden",403

    def event_stream():
        msgs = ["Iniciando servicio: "+service, "Procesando...", "Servicio en curso", "Finalizando sesión"]
        for m in msgs:
            sleep(1)
            yield f"data:{m}|\n\n"
    return Response(event_stream(), mimetype="text/event-stream")

# --- Ejecutar ---
if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
