import os
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai # Importación actualizada

# --- Firebase Setup ---
# Obtiene la configuración de Firebase de la variable de entorno
firebase_config_json = os.environ.get('__firebase_config__')

if firebase_config_json:
    # Carga las credenciales de Firebase desde la configuración
    try:
        cred = credentials.Certificate(eval(firebase_config_json))
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Firebase inicializado correctamente.")
    except Exception as e:
        print(f"Error al inicializar Firebase: {e}")
else:
    print("Error: La variable de entorno '__firebase_config__' no está configurada.")

# --- Gemini API Setup ---
# Obtiene la clave de API de Gemini de la variable de entorno
gemini_api_key = os.environ.get('GEMINI_API_KEY')

if gemini_api_key:
    # Configura el cliente de la API de Gemini con la nueva función
    genai.configure(api_key=gemini_api_key)
    print("Cliente de la API de Gemini configurado correctamente.")
else:
    print("Error: La variable de entorno 'GEMINI_API_KEY' no está configurada.")

# --- Aquí puedes añadir el resto de tu lógica de la aplicación ---
# Ahora puedes usar 'db' para interactuar con Firestore y el módulo 'genai'
# para hacer llamadas a la API de Gemini.

# Ejemplo de cómo podrías usar el cliente de Gemini (solo para demostración)
# model = genai.GenerativeModel('gemini-pro')
# response = model.generate_content("Escribe una historia corta.")
# print(response.text)
