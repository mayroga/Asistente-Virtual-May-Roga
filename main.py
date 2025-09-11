from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import stripe
import os
import openai

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# --- Claves desde variables de entorno ---
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
PUBLIC_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")  # Tu clave pública Stripe
MAYROGA_SECRET = os.environ.get("MAYROGA_ACCESS_CODE")  # Código secreto
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
URL_SITE = os.environ.get("URL_SITE")  # https://asistente-virtual-may-roga.onrender.com

openai.api_key = OPENAI_API_KEY

# --- Funciones OpenAI ---
def detectar_tvid(mensaje):
    mensaje = mensaje.lower()
    if "estres" in mensaje:
        return ["TDB", "TDM"]
    elif "ira" in mensaje:
        return ["TDM"]
    else:
        return ["TDB"]

def adaptar_ejercicios(tecnicas, servicio):
    adapted = []
    for t in tecnicas:
        ejercicios = ["Ejercicio 1", "Ejercicio 2"]
        adapted.append({
            "sigla": t,
            "nombre": t,
            "descripcion": f"Descripcion de {t}",
            "ejercicios": ejercicios
        })
    return adapted

def generar_sesion_coach(tecnicas, servicio):
    tiempo_total = 600  # 10 minutos por defecto
    bloques = [
        {"nombre": "Bienvenida", "duracion": int(tiempo_total*0.1), "actividad": "Saluda y pregunta"},
        {"nombre": "Exploracion", "duracion": int(tiempo_total*0.2), "actividad": "Escucha necesidades"},
        {"nombre": "Practica", "duracion": int(tiempo_total*0.6), "actividad": f"Guia ejercicios de {', '.join([t['sigla'] for t in tecnicas])}"},
        {"nombre": "Cierre", "duracion": int(tiempo_total*0.1), "actividad": "Resumen y refuerzo positivo"}
    ]
    return bloques

def generar_respuesta_openai(service, messages):
    try:
        ultimo_mensaje = messages[-1] if messages else ""
        tvid_seleccionada = detectar_tvid(ultimo_mensaje)
        tvid_adaptada = adaptar_ejercicios(tvid_seleccionada, service)
        bloques_sesion = generar_sesion_coach(tvid_adaptada, service)

        tvid_info = "\n".join([
            f"{t['sigla']} - {t['nombre']}: {t['descripcion']}\nEjercicios: {', '.join(t['ejercicios'])}"
            for t in tvid_adaptada
        ])
        bloques_info = "\n".join([
            f"{b['nombre']} ({b['duracion']} seg): {b['actividad']}" for b in bloques_sesion
        ])

        formatted_messages = [
            {"role": "system", "content":
             f"""Eres Asistente May Roga, creado por Maykel Rodriguez Garcia, experto en risoterapia y bienestar natural.
Conoces todas las Tecnicas de Vida (Tvid): TDB, TDM, TDN, TDK, TDP, TDMM, TDG.
GUIA al cliente como un verdadero coach: pregunta, escucha y adapta ejercicios paso a paso segun sus respuestas.
Nunca uses contacto fisico.
Manten tono profesional, calido y cercano, adapta ejemplos a la edad y situacion del cliente.
Informacion de Tvid adaptada segun mensaje del usuario y tipo de servicio ({service}):
{tvid_info}
Bloques de la sesion segun tiempo total:
{bloques_info}"""
            }
        ]
        for m in messages:
            formatted_messages.append({"role": "user", "content": m})

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=formatted_messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error AI: {str(e)}"

# --- Rutas Flask ---
@app.route("/")
def home():
    return render_template("index.html", stripe_public_key=PUBLIC_KEY)

@app.route("/assistant-unlock", methods=["POST"])
def unlock():
    data = request.json
    return jsonify({"success": data.get("secret") == MAYROGA_SECRET})

# --- Todos los servicios ya incluidos ---
SERVICES_REPLACEMENTS = {
    "RISOTERAPIA Y BIENESTAR NATURAL": "Risoterapia y Bienestar Natural",
    "SERVICIO EXPRESS": "Express Service",
    "HOROSCOPO Y CONSEJOS DE VIDA": "Horoscope & Life Advice",
    "TÉ MÁGICO EN 2 MINUTOS": "Magic Tea in 2 Minutes",
    "INFUSIÓN ANTI-ESTRÉS": "Anti-Stress Infusion",
    "BATIDO ENERGÉTICO NATURAL": "Natural Energy Smoothie",
    "MINI GUÍA DE PLANTAS CURATIVAS": "Mini Healing Plants Guide",
    "RESPIRACIÓN VERDE EXPRESS": "Green Breathing Express",
    "RISA RELÁMPAGO": "Lightning Laughter",
    "MOTÍVATE EN UN MINUTO": "Motivate in a Minute",
    "RESPIRA Y SONRÍE": "Breathe and Smile",
    "CONFIANZA EXPRESS": "Express Confidence",
    "OPTIMISMO AL INSTANTE": "Instant Optimism",
    "HORÓSCOPO FLASH": "Flash Horoscope",
    "CONSEJO DEL DÍA": "Daily Advice",
    "AMOR INSTANTÁNEO": "Instant Love",
    "ABUNDANCIA EN 2 MINUTOS": "Abundance in 2 Minutes",
    "MENSAJE DE TU ESTRELLA": "Message from Your Star",
    "MINI DIAGNÓSTICO DE HÁBITOS": "Mini Habit Diagnosis",
    "EJERCICIO TVID EXPRESS": "TVid Express Exercise",
    "PREVENCIÓN EN UN MINUTO": "Prevention in a Minute",
    "RETO 3 DÍAS EXPRESS": "3-Day Express Challenge",
    "TRACKER DE BIENESTAR DIARIO": "Daily Wellbeing Tracker",
    "RECETA VERDE EXPRESS": "Green Recipe Express",
    "TÉ RELAJANTE RÁPIDO": "Quick Relaxing Tea",
    "BATIDO CREATIVO": "Creative Smoothie",
    "INFUSIÓN PARA CLARIDAD MENTAL": "Mental Clarity Infusion",
    "MINI DETOX EXPRESS": "Mini Detox Express"
}

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    data = request.json
    product_name = data['product'].upper()
    if product_name in SERVICES_REPLACEMENTS:
        product_name = SERVICES_REPLACEMENTS[product_name]

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': product_name},
                    'unit_amount': int(float(data['amount']) * 100)
                },
                'quantity': 1
            }],
            mode='payment',
            success_url=f"{URL_SITE}/success?service={product_name}",
            cancel_url=f"{URL_SITE}/cancel"
        )
        return jsonify({"url": session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/assistant-stream-message", methods=["POST"])
def assistant_stream_message():
    data = request.json
    service = data.get("service")
    messages = data.get("messages", [])

    if not messages:
        return jsonify({"answer": ""})

    # SOLO responde si se paga o se pone código secreto
    paid = data.get("paid", False)
    secret_verified = data.get("secret_verified", False)

    if paid or secret_verified:
        answer = generar_respuesta_openai(service, messages)
        return jsonify({"answer": answer})
    else:
        return jsonify({"answer": ""})  # Queda en blanco si no se paga ni hay código secreto

@app.route("/success")
def success():
    service = request.args.get("service", "")
    return f"✅ Pago exitoso. Servicio activado: {service}"

@app.route("/cancel")
def cancel():
    return "❌ Pago cancelado."

# --- Ejecutar servidor ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
