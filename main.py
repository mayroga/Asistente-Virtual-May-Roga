from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import stripe
import os
import openai
import json
import datetime

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)
CORS(app, origins=["https://sites.google.com"])

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
PUBLIC_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
MAYROGA_SECRET = os.environ.get("MAYROGA_ACCESS_CODE")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
URL_SITE = os.environ.get("URL_SITE")
openai.api_key = OPENAI_API_KEY

# --- Cargar manual Tvid ---
with open('manual_tvid.json', 'r', encoding='utf-8') as f:
    manual_data = json.load(f)["manual"]

manual_tecnicas = manual_data["partes"]["manual_Tvid_solo"]["tecnicas"]
tabla_decision = manual_data["partes"]["manual_Tvid_solo"]["tabla_decision"]
reglas_generales = manual_data["partes"]["parte_IV"]["reglas"]

# --- Tiempos de cada servicio en segundos ---
SERVICIO_TIEMPOS = {
    "respuesta rápida": 48,
    "risoterapia y bienestar natural": 300,
    "horoscopo y consejos de vida": 90,
    "receta verde express": 120,
    "mensaje de tu estrella": 120,
    "respira y sonríe": 120
}

# --- Función para detectar Tvid según palabras clave ---
def detectar_tvid(mensaje):
    mensaje = mensaje.lower()
    if "estres" in mensaje or "agotado" in mensaje:
        return [t for t in manual_tecnicas if t["sigla"] in tabla_decision["estres"]]
    elif "ira" in mensaje or "culpa" in mensaje:
        return [t for t in manual_tecnicas if t["sigla"] in tabla_decision["ira"]]
    elif "bloque" in mensaje or "creativo" in mensaje:
        return [t for t in manual_tecnicas if t["sigla"] in tabla_decision["bloqueo_creativo"]]
    elif "autoestima" in mensaje or "solo" in mensaje:
        return [t for t in manual_tecnicas if t["sigla"] in tabla_decision["autoestima_baja"]]
    elif "procrastinacion" in mensaje or "desorganizado" in mensaje:
        return [t for t in manual_tecnicas if t["sigla"] in tabla_decision["procrastinacion"]]
    elif "crisis" in mensaje or "miedo" in mensaje:
        return [t for t in manual_tecnicas if t["sigla"] in tabla_decision["crisis"]]
    else:
        return [t for t in manual_tecnicas if t["sigla"] == "TDB"]

# --- Función para adaptar ejercicios según tipo de servicio ---
def adaptar_ejercicios(tecnicas, servicio):
    adapted = []
    for t in tecnicas:
        ejercicios = t["ejercicios"]
        s = servicio.lower()
        if s == "receta verde express":
            ejercicios = [f"{e} (guía personalizada)" for e in ejercicios]
        elif s == "mensaje de tu estrella":
            ejercicios = [f"{e} (enfoque corporativo)" for e in ejercicios]
        elif s == "respira y sonríe":
            ejercicios = [f"{e} (dinámica grupal)" for e in ejercicios]
        elif s == "risoterapia y bienestar natural":
            ejercicios = [f"{e} (bienestar y risa)" for e in ejercicios]
        adapted.append({
            "sigla": t["sigla"],
            "nombre": t["nombre"],
            "descripcion": t["descripcion"],
            "ejercicios": ejercicios
        })
    return adapted

# --- Función para guiar la sesión como un coach ---
def generar_sesion_coach(tecnicas, servicio):
    tiempo_total = SERVICIO_TIEMPOS.get(servicio.lower(), 600)
    bloques = []
    if tiempo_total <= 60:
        bloques.append({"nombre": "Interacción rápida", "duracion": tiempo_total, "actividad": "Pregunta y respuesta rápida"})
    else:
        bienvenida = int(tiempo_total * 0.1)
        exploracion = int(tiempo_total * 0.2)
        practica = int(tiempo_total * 0.6)
        cierre = int(tiempo_total * 0.1)
        bloques = [
            {"nombre": "Bienvenida cálida", "duracion": bienvenida, "actividad": "Saluda, pregunta cómo se siente"},
            {"nombre": "Exploración inicial", "duracion": exploracion, "actividad": "Escucha necesidades y emociones del cliente"},
            {"nombre": "Práctica guiada", "duracion": practica, "actividad": f"Guía ejercicios de: {', '.join([e['sigla'] for e in tecnicas])} adaptados a {servicio}"},
            {"nombre": "Cierre positivo", "duracion": cierre, "actividad": "Resumen y refuerzo positivo"}
        ]
    return bloques

@app.route('/')
def index():
    return render_template('index.html', stripe_public_key=PUBLIC_KEY)

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout():
    data = request.get_json()
    product = data.get('product')
    amount = data.get('amount')
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': product},
                    'unit_amount': int(amount * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'{URL_SITE}/success?service={product}',
            cancel_url=f'{URL_SITE}/cancel',
        )
        return jsonify({'url': session.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/assistant-unlock', methods=['POST'])
def unlock_services():
    data = request.get_json()
    secret = data.get('secret')
    return jsonify({'success': secret == MAYROGA_SECRET})

@app.route('/assistant-stream-message', methods=['POST'])
def assistant_stream_message():
    data = request.get_json()
    service = data.get('service', 'Servicio')
    messages = data.get('messages', [])
    try:
        ultimo_mensaje = messages[-1] if messages else ""
        tvid_seleccionada = detectar_tvid(ultimo_mensaje)
        tvid_adaptada = adaptar_ejercicios(tvid_seleccionada, service)
        bloques_sesion = generar_sesion_coach(tvid_adaptada, service)
        tvid_info = "\n".join([ f"{t['sigla']} - {t['nombre']}: {t['descripcion']}\nEjercicios: {', '.join(t['ejercicios'])}" for t in tvid_adaptada ])
        bloques_info = "\n".join([ f"{b['nombre']} ({b['duracion']} seg): {b['actividad']}" for b in bloques_sesion ])
        formatted_messages = [{"role": "system", "content": f"""Eres Asistente May Roga, creado por Maykel Rodríguez García, experto en risoterapia y bienestar natural. Conoces todas las Técnicas de Vida (Tvid): TDB, TDM, TDN, TDK, TDP, TDMM, TDG. GUÍA al cliente como un verdadero coach: pregunta, escucha y adapta ejercicios paso a paso según sus respuestas. Nunca uses contacto físico. Mantén tono profesional, cálido y cercano, adapta ejemplos a la edad y situación del cliente. Información de Tvid adaptada según mensaje del usuario y tipo de servicio ({service}): {tvid_info} Bloques de la sesión según tiempo total: {bloques_info}""" }]
        for m in messages:
            formatted_messages.append({"role": "user", "content": m})
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=formatted_messages
        )
        answer = response.choices[0].message.content
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'answer': f"Error al generar respuesta: {str(e)}"})

@app.route('/success')
def success():
    service = request.args.get('service', '')
    return f"Pago exitoso ✅. Servicio activado: {service}"

@app.route('/cancel')
def cancel():
    return "Pago cancelado ❌"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
