from flask import Flask, request, jsonify, Response
import time
import json

app = Flask(__name__)

# -------------------
# CONFIGURACIÓN
# -------------------
# Tu código secreto, solo en backend
SECRET_CODE = "MI_CODIGO_SECRETO_REAL"

# Lista de servicios (para ejemplo)
SERVICES = {
    "Risoterapia y Bienestar Natural": {"duration": 600, "price": 12},
    "Horóscopo y Consejos de Vida": {"duration": 120, "price": 6},
    "Respuesta Rápida": {"duration": 55, "price": 2},
    "Servicio Personalizado": {"duration": 1200, "price": 50},
    "Servicio Corporativo": {"duration": 1800, "price": 750},
    "Servicio Grupal": {"duration": 900, "price": 450}
}

# -------------------
# ENDPOINT: desbloqueo con código secreto
# -------------------
@app.route("/assistant-unlock", methods=["POST"])
def unlock_services():
    data = request.get_json()
    if data and data.get("secret") == SECRET_CODE:
        return jsonify({"success": True})
    return jsonify({"success": False}), 403

# -------------------
# ENDPOINT: SSE del asistente
# -------------------
@app.route("/assistant-stream")
def assistant_stream():
    service = request.args.get("service")
    secret = request.args.get("secret", None)

    # Validación de código secreto si se solicita 'all'
    if service == "all":
        if secret != SECRET_CODE:
            return "Código incorrecto", 403

    def event_stream():
        # Ejemplo: enviar mensajes cada 2 segundos
        for i in range(1, 6):
            msg = f"🎵 Mensaje {i} del servicio {service}"
            yield f"data: {msg}\n\n"
            time.sleep(2)
        yield "data: Sesión finalizada ✅\n\n"

    return Response(event_stream(), mimetype="text/event-stream")

# -------------------
# ENDPOINT: simulación checkout (Stripe)
# -------------------
@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    data = request.get_json()
    product = data.get("product")
    amount = data.get("amount")
    # Aquí iría tu lógica real con Stripe
    # Para prueba, devolvemos un id simulado
    return jsonify({"id": "cs_test_simulado"})

# -------------------
# INICIO APP
# -------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
