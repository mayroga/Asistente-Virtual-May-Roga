from fastapi import FastAPI, Request, Response, status
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os, uuid, asyncio
import openai

app = FastAPI()
openai.api_key = os.environ.get("OPENAI_API_KEY")

# CORS para Google Sites
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "https://sites.google.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAYROGA_ACCESS_CODE = os.environ.get("MAYROGA_ACCESS_CODE")
SERVICES = {
    "Risoterapia y Bienestar Natural": 600,
    "Horóscopo y Consejos de Vida": 120,
    "Respuesta Rápida": 55,
    "Servicio Personalizado": 1200,
    "Servicio Corporativo": 20*60,
    "Servicio Grupal": 900
}

@app.post("/create-checkout-session")
async def create_checkout_session(req: Request):
    data = await req.json()
    product = data.get("product")
    amount = int(data.get("amount")) * 100
    return JSONResponse({"id":"sesion_de_pago_demo"})

@app.get("/assistant-stream")
async def assistant_stream(service: str, secret: str = None):
    if secret and secret != MAYROGA_ACCESS_CODE:
        return Response("Forbidden", status_code=status.HTTP_403_FORBIDDEN)

    async def event_generator():
        messages = [
            f"Bienvenido al servicio {service}.",
            "Aplicando Técnicas de Vida (TVid) de May Roga LLC...",
            "Escuchando tu estado y adaptando la sesión...",
            "Sesión en progreso..."
        ]
        for msg in messages:
            # Generar TTS real con OpenAI/Gemini
            response = openai.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice="alloy",
                input=msg
            )
            audio_filename = f"/static/audios/{uuid.uuid4()}.mp3"
            with open(f".{audio_filename}", "wb") as f:
                f.write(response.audio_data)
            yield f"data: {msg}|{audio_filename}\n\n"
            await asyncio.sleep(2)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/get-duration")
async def get_duration(service: str):
    return {"duration": SERVICES.get(service, 300)}
