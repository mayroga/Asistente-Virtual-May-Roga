from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import os
import openai
import time

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# --- Configuración variables de entorno ---
openai.api_key = os.environ.get("OPENAI_API_KEY")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
ACCESS_CODE = os.environ.get("MAYROGA_ACCESS_CODE")
URL_SITE = os.environ.get("URL_SITE", "https://asistente-virtual-may-roga.onrender.com")

# --- RUTA PRINCIPAL ---
@app.route('/')
def index():
    return render_template('index.html', stripe_public_key=STRIPE_PUBLISHABLE_KEY)

# --- Desbloquear servicios con código secreto ---
@app.route('/assistant-unlock', methods=['POST'])
def unlock_services():
    data = request.get_json()
    secret = data.get('secret')
    if secret == ACCESS_CODE:
        return jsonify({'success': True})
    return jsonify({'success': False})

# --- SSE para comunicación de mensajes con IA ---
@app.route('/assistant-stream')
def assistant_stream():
    service = request.args.get('service', 'Servicio')
    secret = request.args.get('secret', None)

    # Validación del código secreto para servicios desbloqueados
    if secret != ACCESS_CODE:
        return jsonify({'error': 'Código secreto incorrecto'}), 403

    def generate():
        # Mensajes iniciales de bienvenida
        initial_messages = [
            f"Bienvenido al servicio: {service}",
            "Aquí empieza tu sesión de comunicación...",
            "Disfruta de la experiencia 😊"
        ]
        for msg in initial_messages:
            yield f"data: {msg}\n\n"
            time.sleep(1)

        # Ciclo de interacción con OpenAI (simulación de chat continuo)
        user_messages = []
        while True:
            # Espera por un nuevo mensaje del cliente (usaremos una cola temporal en frontend)
            # Aquí simplificado: toma un último mensaje si se pasa como parámetro GET
            latest_msg = request.args.get('message')
            if latest_msg:
                user_messages.append({"role": "user", "content": latest_msg})
                # Crear prompt completo
                prompt = [
                    {"role": "system", "content": f"Eres el Asistente May Roga. Atiendes de forma empática y profesional, guiando al usuario en el servicio '{service}'."}
                ] + user_messages

                try:
                    completion = openai.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=prompt,
                        temperature=0.7
                    )
                    response_msg = completion.choices[0].message['content']
                    user_messages.append({"role": "assistant", "content": response_msg})
                    yield f"data: {response_msg}\n\n"
                except Exception as e:
                    yield f"data: Error al generar respuesta: {str(e)}\n\n"

            time.sleep(1)  # evita loop muy rápido

    return Response(generate(), mimetype='text/event-stream')

# --- Inicio de sesión de chat desde frontend ---
@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.get_json()
    service = data.get('service', 'Servicio')
    message = data.get('message', '')
    secret = data.get('secret', None)

    if secret != ACCESS_CODE:
        return jsonify({'error': 'Código secreto incorrecto'}), 403

    # Respuesta directa de OpenAI
    prompt = [
        {"role": "system", "content": f"Eres el Asistente May Roga. Atiendes de forma empática y profesional, guiando al usuario en el servicio '{service}'."},
        {"role": "user", "content": message}
    ]

    try:
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=prompt,
            temperature=0.7
        )
        response_msg = completion.choices[0].message['content']
        return jsonify({"response": response_msg})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
