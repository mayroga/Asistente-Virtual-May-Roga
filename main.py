import random
import string
import json
from flask import Flask, request, jsonify

# --- Configuración de la aplicación Flask ---
app = Flask(__name__)

# --- Base de datos simulada (para demostración) ---
# En un sistema real, usarías una base de datos como Firestore o PostgreSQL
clientes_registrados = {}
sesiones_activas = {}

# --- Función para simular el pago con Stripe ---
def simular_pago_stripe(servicio, monto):
    """
    Simula una transacción de pago.
    En un entorno de producción, esto se conectaría con la API de Stripe.
    """
    print(f"Simulando pago de {monto} para el servicio: {servicio}")
    # Aquí iría la lógica real de la API de Stripe.
    # Por ahora, asumimos que siempre es exitoso.
    return True

# --- Función para generar códigos de sesión únicos ---
def generar_codigo_sesion(longitud=6):
    """
    Genera un código alfanumérico aleatorio para una sesión grupal.
    """
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(random.choice(caracteres) for _ in range(longitud))

# --- Rutas de la API (Endpoints) ---

@app.route('/registrar', methods=['POST'])
def registrar_cliente():
    """
    Ruta para manejar el registro de un nuevo cliente.
    """
    data = request.json
    apodo = data.get('apodo')
    correo = data.get('correo')
    telefono = data.get('telefono')

    if not apodo or not correo or not telefono:
        return jsonify({"mensaje": "Error: Se requieren todos los campos de registro."}), 400

    cliente_id = apodo # Usamos el apodo como ID simple
    clientes_registrados[cliente_id] = {
        'apodo': apodo,
        'correo': correo,
        'telefono': telefono
    }
    
    print(f"Nuevo cliente registrado: {json.dumps(clientes_registrados[cliente_id], indent=2)}")
    return jsonify({"mensaje": "Registro exitoso."}), 200

@app.route('/iniciar_sesion', methods=['POST'])
def iniciar_sesion():
    """
    Ruta para iniciar una sesión de servicio después del pago.
    """
    data = request.json
    servicio = data.get('servicio')
    modo = data.get('modo')
    monto = data.get('monto')

    if not servicio or not modo or not monto:
        return jsonify({"mensaje": "Error: Se requieren el servicio, modo y monto."}), 400

    # Simular el proceso de pago
    pago_exitoso = simular_pago_stripe(servicio, monto)

    if not pago_exitoso:
        return jsonify({"mensaje": "El pago no pudo ser procesado."}), 402 # 402 Payment Required

    codigo_sesion = None
    if modo == 'grupal':
        codigo_sesion = generar_codigo_sesion()
        print(f"Código de sesión grupal generado: {codigo_sesion}")
    
    sesiones_activas[codigo_sesion or "individual"] = {
        'servicio': servicio,
        'modo': modo,
        'inicio': 'timestamp' # Usarías el tiempo real
    }

    response_data = {
        "mensaje": "Sesión iniciada correctamente.",
        "codigo_sesion": codigo_sesion
    }
    
    return jsonify(response_data), 200

@app.route('/salud_check', methods=['GET'])
def salud_check():
    """
    Ruta simple para verificar que el servidor está en funcionamiento.
    """
    return jsonify({"status": "activo", "mensaje": "Asistente May Roga listo para curar tu espíritu."}), 200

# --- Inicio del servidor ---
if __name__ == '__main__':
    app.run(debug=True)
