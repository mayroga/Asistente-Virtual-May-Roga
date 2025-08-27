from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
import json
import os
import openai

app = FastAPI()

# Configurar OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Cargar JSON de respaldo
def cargar_json(nombre):
    ruta = os.path.join("data", nombre)
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"respuestas": ["Lo siento, no tengo respuesta disponible."]}

behavior_guide = cargar_json("behavior_guide.json")
enfermedades = cargar_json("enfermedades.json")
urgencias = cargar_json("urgencias.json")

# Página principal
@app.get("/", response_class=HTMLResponse)
async def index():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# Endpoint chat
@app.post("/chat")
async def chat(message: str = Form(...)):
    mensaje = message.lower()
    
    # Horóscopo
    if "horóscopo" in mensaje:
        respuesta = "Tu horóscopo para hoy: ¡Energía positiva y alegría! 🌞"
    
    # Risoterapia
    elif "risoterapia" in mensaje:
        respuesta = "Técnica del Bien (TDB): sonríe, respira profundo y piensa en algo positivo."
    
    # Enfermedad
    elif "enfermedad" in mensaje:
        respuesta = enfermedades.get("respuestas", ["No hay información disponible."])[0]
    
    # Urgencia
    elif "urgencia" in mensaje:
        respuesta = urgencias.get("respuestas", ["No hay información disponible."])[0]
    
    # General / respaldo
    else:
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message}]
            )
            respuesta = completion.choices[0].message.content
        except:
            respuesta = behavior_guide.get("respuestas", ["Lo siento, no puedo responder ahora."])[0]

    return JSONResponse({"respuesta": respuesta})

# Ping rápido
@app.get("/ping")
async def ping():
    return {"message": "Servidor activo 🚀"}
