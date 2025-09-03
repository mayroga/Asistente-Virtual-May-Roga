from flask import Flask, jsonify, request

app = Flask(__name__)

# Una ruta simple para verificar que la API funciona.
@app.route('/')
def home():
    """
    Ruta de inicio de la API.

    Returns:
        JSON con un mensaje de bienvenida.
    """
    return jsonify({
        "message": "¡Hola! La API está funcionando correctamente."
    })

# Una ruta de ejemplo que recibe datos del cuerpo de la petición.
@app.route('/data', methods=['POST'])
def process_data():
    """
    Ruta para procesar datos enviados en el cuerpo de la petición.

    Returns:
        JSON con un mensaje de confirmación y los datos recibidos.
    """
    try:
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": "No se encontraron datos JSON en el cuerpo de la petición."}), 400
        
        # Simplemente devolvemos los datos para confirmar que los recibimos.
        return jsonify({
            "message": "Datos recibidos correctamente.",
            "received_data": data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Esta parte del código es solo para cuando ejecutas el archivo localmente,
# Gunicorn la ignora por completo.
if __name__ == '__main__':
    app.run(debug=True)
