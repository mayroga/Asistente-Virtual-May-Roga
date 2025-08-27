from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>May Roga</title>
        </head>
        <body>
            <h1>Bienvenido a May Roga LLC</h1>
            <p>Servicio de risoterapia y bienestar natural activo.</p>
        </body>
    </html>
    """

# Aquí puedes agregar más endpoints según tu proyecto
