import os
import firebase_admin
from firebase_admin import credentials, firestore
from google.generativeai.client import get_default_client

# --- Firebase Setup ---
# Obtiene la configuración de Firebase de la variable de entorno
firebase_config_json = os.environ.get('__firebase_config__')

if firebase_config_json:
    # Carga las credenciales de Firebase desde la configuración
    cred = credentials.Certificate(firebase_config_json)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase inicializado correctamente.")
else:
    print("Error: La variable de entorno '__firebase_config__' no está configurada.")

# --- Gemini API Setup ---
# Obtiene la clave de API de Gemini de la variable de entorno
gemini_api_key = os.environ.get('GEMINI_API_KEY')

if gemini_api_key:
    # Configura el cliente de la API de Gemini
    api_client = get_default_client(api_key=gemini_api_key)
    print("Cliente de la API de Gemini configurado correctamente.")
else:
    print("Error: La variable de entorno 'GEMINI_API_KEY' no está configurada.")

# --- Aquí puedes añadir el resto de tu lógica de la aplicación ---
# Ahora puedes usar 'db' para interactuar con Firestore y 'api_client' para
# hacer llamadas a la API de Gemini.

# Ejemplo de cómo podrías usar el cliente de Firestore (solo para demostración)
# doc_ref = db.collection('tu_coleccion').document('tu_documento')
# doc_ref.set({'clave': 'valor'})

# Ejemplo de cómo podrías usar el cliente de la API de Gemini (solo para demostración)
# response = api_client.generate_content('Escribe una historia corta.')
# print(response.text)
