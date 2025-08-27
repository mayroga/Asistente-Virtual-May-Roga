# src/main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Inicializamos la app
app = FastAPI()

# Configuración de templates y static (aunque static esté vacío)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Antes cargábamos behavior_guide.json, ahora inicializamos vacío
behavior_guide = []

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Página principal
    """
    return templates.TemplateResponse("index.html", {
        "request": request,
        "behavior_guide": behavior_guide  # vacío por ahora
    })
