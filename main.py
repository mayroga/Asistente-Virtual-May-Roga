from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import stripe
import os
import openai

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# --- Claves desde variables de entorno ---
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
PUBLIC_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
MAYROGA_SECRET = os.environ.get("MAYROGA_ACCESS_CODE")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
URL_SITE = os.environ.get("URL_SITE")  # Para success/cancel URLs

# --- Configuración OpenAI ---
openai.api_key = OPENAI_API_KEY

# --- Control de acceso para producción ---
# True = acceso controlado; False = acceso libre (pruebas)
ENABLE_ACCESS_CONTROL = False

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
        answer = response.choices[0].message.content
        return answer
    except Exception as e:
        print("Error OpenAI:", str(e))
        return f"Error AI: {str(e)}"

# --- Rutas Flask ---
@app.route("/")
def home():
    return render_template("index.html", stripe_public_key=PUBLIC_KEY)

@app.route("/assistant-unlock", methods=["POST"])
def unlock():
    data = request.json
    secret_verified = data.get("secret") == MAYROGA_SECRET
    return jsonify({"success": secret_verified})

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    data = request.json
    product_name = data['product'].upper()
    replacements = {
        "TÉ MAGICO EN 2 MINUTOS": "TE MAGICO EN DOS MINUTOS",
        "INFUSIÓN ANTI-ESTRÉS": "INFUSION ANTI-ESTRES",
        "BATIDO ENERGÉTICO NATURAL": "BATIDO ENERGETICO NATURAL",
        "MINI GUÍA DE PLANTAS CURATIVAS": "MINI GUIA DE PLANTAS CURATIVAS",
        "RESPIRACIÓN VERDE EXPRESS": "RESPIRACION VERDE EXPRESS",
        "RISA RELÁMPAGO": "RISA RELAMPAGO",
        "MOTÍVATE EN UN MINUTO": "MOTIVATE EN UN MINUTO",
        "RESPIRA Y SONRÍE": "RESPIRA Y SONRIE",
        "HORÓSCOPO FLASH": "HOROSCOPO FLASH",
        "CONSEJO DEL DÍA": "CONSEJO DEL DIA",
        "AMOR INSTANTÁNEO": "AMOR INSTANTANEO",
        "MINI DIAGNÓSTICO DE HÁBITOS": "MINI DIAGNOSTICO DE HABITOS",
        "PREVENCIÓN EN UN MINUTO": "PREVENCION EN UN MINUTO",
        "RETO 3 DÍAS EXPRESS": "RETO 3 DIAS EXPRESS",
        "INFUSIÓN PARA CLARIDAD MENTAL": "INFUSION PARA CLARIDAD MENTAL"
    }
    if product_name in replacements:
        product_name = replacements[product_name]

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
    paid = data.get("paid", False)
    secret_verified = data.get("secret_verified", False)

    if not messages:
        return jsonify({"answer": "No se envio ningun mensaje."})

    # --- Control de acceso solo si ENABLE_ACCESS_CONTROL = True ---
    if ENABLE_ACCESS_CONTROL:
        if not (paid or secret_verified):
            return jsonify({"answer": ""})

    # Ejecuta OpenAI normalmente
    answer = generar_respuesta_openai(service, messages)
    return jsonify({"answer": answer})

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
