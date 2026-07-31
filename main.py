from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import random
import re
from datetime import datetime
import urllib.parse

app = FastAPI()

# Asegura que el directorio 'static' exista antes de montar
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Vector de necesidades por defecto, ampliado para las preocupaciones de la audiencia objetivo
DEFAULT_NECESSITY_VECTOR = {
    "movimiento": 50, "naturaleza": 50, "silencio": 50, "agua": 50, "sol": 50,
    "sombra": 50, "aire_fresco": 50, "creatividad": 50, "comunidad": 50, "aprendizaje": 50,
    "juego": 50, "contemplacion": 50, "descanso": 50, "organizacion": 50,
    "alimentacion": 50, "musica": 50, "risa": 50, "esperanza": 50,
    "carga_trabajo": 50, "responsabilidad": 50, "soledad": 50, "aislamiento": 50,
    "prision_mental": 0, "agotamiento_mental": 0, "ansiedad": 0
}

# Límites del historial para evitar repeticiones recientes y fomentar la diversidad
MAX_HISTORY_SALIR = 5
MAX_HISTORY_CASA = 8
EXPLORATION_RATE = 0.20
HISTORY_PENALTY_BASE = 40

def limitar_historial(historial, limite):
    """Limita el historial a un número máximo de entradas."""
    if historial is None:
        return []
    return historial[-limite:]

def penalizacion_historial(mision_id, historial):
    """Calcula una penalización para misiones que han aparecido recientemente."""
    if not historial:
        return 0
    historial_invertido = list(reversed(historial)) # Las más recientes tienen mayor impacto
    for posicion, antiguo_id in enumerate(historial_invertido):
        if antiguo_id == mision_id:
            if posicion == 0: return HISTORY_PENALTY_BASE * 2.0 # Si es la última, penaliza más
            if posicion == 1: return HISTORY_PENALTY_BASE * 1.5
            if posicion == 2: return HISTORY_PENALTY_BASE * 1.0
            if posicion <= (len(historial_invertido) - 1): return HISTORY_PENALTY_BASE * 0.5
    return 0

def bonus_exploracion(mision_id, historial):
    """Otorga una bonificación si la misión nunca ha sido vista o no está en el historial reciente."""
    if not historial or mision_id not in historial:
        return 30 # Bonificación alta si nunca se ha visto
    if mision_id not in limitar_historial(historial, int(MAX_HISTORY_SALIR / 2)):
        return 10 # Bonificación menor si no está en el historial muy reciente
    return 0

def actualizar_historial(historial, nuevo_id, limite):
    """Añade un ID al historial, eliminando duplicados y manteniendo el límite."""
    historial = historial or []
    if nuevo_id in historial:
        historial.remove(nuevo_id)
    historial.append(nuevo_id)
    return historial[-limite:]

def diversidad_vector(vector1, vector2):
    """Calcula la distancia de diversidad entre dos vectores de necesidades."""
    distancia = 0
    needs_to_consider = [k for k in DEFAULT_NECESSITY_VECTOR.keys() if k not in ["prision_mental", "agotamiento_mental", "ansiedad"]]
    for k in needs_to_consider:
        val1 = vector1.get(k, DEFAULT_NECESSITY_VECTOR.get(k, 50))
        val2 = vector2.get(k, DEFAULT_NECESSITY_VECTOR.get(k, 50))
        distancia += abs(val1 - val2)
    return distancia

# Mensajes concisos para la experiencia
WHEN_ES = "Ahora. Es tu momento."
WHEN_EN = "Now. It's your moment."
FOR_WHAT_ES = "Reconectar. Romper el bucle."
FOR_WHAT_EN = "Reconnect. Break the loop."
GPS_BASE_URL = "https://www.google.com/maps/search/?api=1&query="

# ============================================================
# CATÁLOGO DE MISIONES CENTRAL - PERSONALIZADO PARA AUDIENCIA
# Cada misión incluye vectores de necesidades para un scoring preciso.
# No se usan términos médicos ni nada que comprometa legalmente.
# ============================================================
BASE_MISIONES = {
    "CASA_ES": [
        {"id": 1, "titulo": "Reinicio Mental Profundo", "descripcion": "Cierra los ojos. Escucha tu respiración por un minuto. Deja que el silencio limpie tu mente de ruido. Siente el ancla de tu cuerpo.", "vector_necesidades": {"contemplacion": 95, "descanso": 90, "silencio": 100, "organizacion": 70, "esperanza": 80, "prision_mental": -20, "agotamiento_mental": -15, "ansiedad": -10}},
        {"id": 2, "titulo": "Desconexión Total del Rol", "descripcion": "Siente el peso de tu silla. El piso sostiene tu existencia. Permite que toda responsabilidad se desvanezca por un instante. Estás seguro, estás aquí.", "vector_necesidades": {"descanso": 100, "contemplacion": 90, "silencio": 80, "responsabilidad": -20, "aislamiento": 60, "prision_mental": -15, "agotamiento_mental": -10, "ansiedad": -5}},
        {"id": 3, "titulo": "Pausa Visual Terapéutica", "descripcion": "Voltea el teléfono. Mira una esquina del techo 45 segundos. Rompe el bucle de estímulos. Permite que tu visión descanse y tu mente se despeje.", "vector_necesidades": {"silencio": 90, "descanso": 85, "contemplacion": 90, "carga_trabajo": -15, "agotamiento_mental": -10, "ansiedad": -5}},
        {"id": 4, "titulo": "Liberación de Hombros", "descripcion": "Siente tus hombros completamente libres. Imagina que una mochila de peso invisible cae al suelo. Suelta la carga física y mental que llevas. Eres ligero.", "vector_necesidades": {"descanso": 95, "movimiento": 60, "risa": 40, "esperanza": 85, "carga_trabajo": -20, "responsabilidad": -15, "agotamiento_mental": -10, "ansiedad": -8}},
        {"id": 5, "titulo": "Bebida Consciente", "descripcion": "Un trago pequeño de agua fría. Siente el líquido recorrer tu cuerpo. Cada gota es vida entrando, limpiando la fatiga. Es un reinicio sencillo y vital.", "vector_necesidades": {"agua": 100, "descanso": 70, "silencio": 50, "salud": 80, "agotamiento_mental": -10, "ansiedad": -5}},
        {"id": 6, "titulo": "Renovación con Aire Fresco", "descripcion": "Abre la ventana. Deja que el aire te golpee la cara. Siente el exterior. Inhala profundamente, permite que el aire limpio renueve tu energía y disipe el encierro.", "vector_necesidades": {"aire_fresco": 100, "naturaleza": 80, "contemplacion": 70, "descanso": 60, "movimiento": 30, "prision_mental": -15, "agotamiento_mental": -10}},
        {"id": 7, "titulo": "Movimiento Corporal Consciente", "descripcion": "Gira muñecas y tobillos suavemente. Tu cuerpo es tuyo y responde a tu mando. Eres el dueño de este motor, activa la circulación, libera la rigidez.", "vector_necesidades": {"movimiento": 95, "descanso": 60, "salud": 80, "agotamiento_mental": -8, "ansiedad": -4}},
        {"id": 8, "titulo": "Anclaje en la Gratitud", "descripcion": "Cierra los ojos. Menciona una sola cosa buena que tienes hoy. Dilo en voz baja o mentalmente. Permite que la esperanza inunde tu presente.", "vector_necesidades": {"contemplacion": 100, "silencio": 90, "esperanza": 95, "aprendizaje": 70, "prision_mental": -10, "ansiedad": -7}},
        {"id": 9, "titulo": "Conexión a Tierra Segura", "descripcion": "Quítate los zapatos. Apoya las plantas de tus pies en el suelo. Siente la frialdad o la textura. La tierra te sostiene, te brinda estabilidad. Estás anclado.", "vector_necesidades": {"naturaleza": 90, "movimiento": 70, "contemplacion": 80, "silencio": 60, "descanso": 70, "aislamiento": 50, "prision_mental": -15}},
        {"id": 10, "titulo": "Estiramiento de Vitalidad", "descripcion": "Estira un brazo hacia arriba como si quisieras tocar el techo. Mantén la tensión por unos segundos y luego suelta de golpe. Siente la liberación de energía en tu cuerpo.", "vector_necesidades": {"movimiento": 95, "descanso": 60, "salud": 80, "agotamiento_mental": -8}},
        {"id": 11, "titulo": "Postura de Dignidad", "descripcion": "Endereza la espalda. Imagina un hilo invisible tirando suavemente de tu cabeza hacia arriba. Respira. Tu postura es un reflejo de tu fuerza interior.", "vector_necesidades": {"salud": 90, "movimiento": 70, "descanso": 80, "silencio": 60, "contemplacion": 70, "responsabilidad": 60}},
        {"id": 12, "titulo": "Contacto Frío Regenerador", "descripcion": "Toca una superficie fría (una ventana, una pared). Siente la temperatura real. Te aterriza en el presente, disipando la neblina mental.", "vector_necesidades": {"naturaleza": 80, "silencio": 70, "contemplacion": 90, "descanso": 60, "prision_mental": -10}},
        {"id": 13, "titulo": "Sacudida de Agobio", "descripcion": "Párate y sacude tus manos y piernas vigorosamente por 10 segundos, como si te quitaras agua. Deja que el agobio y el cansancio se desprendan de ti.", "vector_necesidades": {"movimiento": 100, "risa": 80, "descanso": 70, "juego": 60, "esperanza": 70, "agotamiento_mental": -20, "ansiedad": -15}},
        {"id": 14, "titulo": "Enfoque Visual Lejano", "descripcion": "Mira el objeto más lejano que puedas ver por tu ventana. Permite que tus ojos descansen del enfoque cercano de las pantallas. Expande tu visión, expande tu mente.", "vector_necesidades": {"contemplacion": 95, "silencio": 85, "naturaleza": 70, "descanso": 80, "creatividad": 40, "carga_trabajo": -10}},
        {"id": 15, "titulo": "Recordar la Calma", "descripcion": "Cierra los ojos y recuerda un momento real de profunda calma en tu vida. Revive esa sensación. La paz reside en ti.", "vector_necesidades": {"esperanza": 90, "contemplacion": 95, "risa": 70, "silencio": 80, "descanso": 85, "ansiedad": -10, "prision_mental": -15}},
        {"id": 16, "titulo": "El Poder de la Sonrisa", "descripcion": "Sonríe por 15 segundos, incluso si no sientes ganas. La acción física puede influir en tu estado interno. Genera una pequeña chispa de positividad.", "vector_necesidades": {"risa": 100, "esperanza": 90, "juego": 70, "creatividad": 50, "salud": 80, "prision_mental": -10}},
        {"id": 17, "titulo": "Oscuridad Restauradora", "descripcion": "Tápate los ojos con las palmas de tus manos, entrelazadas suavemente. Disfruta un minuto de oscuridad total. Permite que tus ojos y tu mente descansen profundamente.", "vector_necesidades": {"descanso": 100, "silencio": 90, "contemplacion": 80, "salud": 70, "agotamiento_mental": -15, "ansiedad": -10}},
        {"id": 18, "titulo": "Latido de tu Centro", "descripcion": "Coloca tu mano derecha sobre tu pecho, en el área de tu corazón. Siente el latido. Es tu motor vital. Estás presente, estás vivo.", "vector_necesidades": {"contemplacion": 100, "silencio": 90, "descanso": 80, "salud": 70, "ansiedad": -10}},
        {"id": 19, "titulo": "Movimiento Liberador del Cuello", "descripcion": "Realiza círculos lentos con tu cabeza. Siente cómo se libera la tensión acumulada por las pantallas o la preocupación. Suelta la rigidez.", "vector_necesidades": {"movimiento": 80, "descanso": 90, "salud": 90, "silencio": 70, "carga_trabajo": -10, "agotamiento_mental": -5}},
        {"id": 20, "titulo": "Reconexión por el Olfato", "descripcion": "Busca una flor, café o especia en casa. Huelea conscientemente. Concéntrate en el aroma. Permite que este pequeño acto te traiga al presente.", "vector_necesidades": {"naturaleza": 80, "alimentacion": 70, "contemplacion": 90, "silencio": 80, "descanso": 70, "prision_mental": -5}},
        {"id": 21, "titulo": "Cambio de Perspectiva Espacial", "descripcion": "Siéntate en otra silla o en un lugar diferente de la casa por 5 minutos. Un pequeño cambio en tu entorno puede generar una nueva perspectiva mental.", "vector_necesidades": {"movimiento": 60, "creatividad": 50, "descanso": 70, "organizacion": 40, "contemplacion": 60, "monotonia": -10}}, # Added 'monotonia'
        {"id": 22, "titulo": "Respiro de Soledad Dirigida", "descripcion": "Exhala cualquier preocupación aburrida o sentimiento de soledad. Imagina que sale de tu cuerpo con el aire. Estás borrando el ruido externo. Eres fuerte.", "vector_necesidades": {"esperanza": 90, "silencio": 80, "descanso": 85, "risa": 50, "creatividad": 60, "soledad": -20, "aislamiento": -15, "ansiedad": -10}},
        {"id": 23, "titulo": "Presencia Plena", "descripcion": "Estás aquí. Estás completamente a salvo. Tienes el control de este instante. Permítete sentir la paz absoluta en este segundo.", "vector_necesidades": {"esperanza": 100, "contemplacion": 95, "silencio": 90, "descanso": 85, "organizacion": 70, "prision_mental": -25, "agotamiento_mental": -20, "ansiedad": -15}},
        {"id": 24, "titulo": "Canta tu Libertad", "descripcion": "Tararea tu canción favorita suavemente. No pienses en las palabras, solo en la melodía. Siente el sonido en tu interior, liberando la monotonía.", "vector_necesidades": {"musica": 100, "risa": 70, "creatividad": 80, "descanso": 60, "juego": 50, "prision_mental": -10}},
        {"id": 25, "titulo": "Deseos para Hoy", "descripcion": "En un papel, anota tres deseos simples que te gustaría cumplir hoy. Enfócate en la posibilidad, no en la obligación. Permite que la esperanza guíe tu día.", "vector_necesidades": {"creatividad": 90, "aprendizaje": 70, "organizacion": 80, "esperanza": 95, "contemplacion": 70, "carga_trabajo": 60}},
        {"id": 26, "titulo": "Paseo Consciente por el Hogar", "descripcion": "Camina lentamente por un pasillo de tu casa, sintiendo cada paso en el suelo. Presta atención a la textura, el sonido. Estás presente en tu espacio.", "vector_necesidades": {"movimiento": 70, "contemplacion": 80, "silencio": 70, "descanso": 60, "organizacion": 50, "prision_mental": -5}},
        {"id": 27, "titulo": "Observa la Vida Verde", "descripcion": "Si tienes una planta en casa, obsérvala con atención durante un minuto. Nota sus colores, sus formas. Conecta con la vida silenciosa que te rodea.", "vector_necesidades": {"naturaleza": 90, "contemplacion": 95, "silencio": 80, "descanso": 70, "aprendizaje": 60, "aislamiento": 50}},
        {"id": 28, "titulo": "Dibuja un Círculo Perfecto", "descripcion": "Toma un lápiz y papel. Dibuja círculos, uno tras otro, sin pensar en nada más que en la forma perfecta. Permite que este acto simple te centre.", "vector_necesidades": {"creatividad": 100, "juego": 80, "contemplacion": 70, "silencio": 60, "descanso": 50, "carga_trabajo": -5}},
        {"id": 29, "titulo": "Escucha la Melodía Natural", "descripcion": "Si llueve o hay viento, abre la ventana y escucha el sonido de la naturaleza. Deja que el ritmo natural acune tu mente y disipe el estrés.", "vector_necesidades": {"naturaleza": 100, "silencio": 95, "agua": 90, "contemplacion": 90, "descanso": 85, "ansiedad": -15}},
        {"id": 30, "titulo": "Baila tu Desahogo", "descripcion": "Mueve tu cuerpo libremente por un minuto, como si nadie te viera. Suelta la tensión acumulada. Permite que la música interna guíe tu movimiento.", "vector_necesidades": {"movimiento": 100, "juego": 90, "risa": 80, "creatividad": 70, "musica": 50, "agotamiento_mental": -15, "prision_mental": -10}},
        {"id": 31, "titulo": "Infusión de Calma", "descripcion": "Prepara una infusión caliente (sin cafeína) y bébela lentamente. Siente el calor en tus manos, el aroma. Concéntrate solo en este momento de quietud.", "vector_necesidades": {"alimentacion": 90, "descanso": 100, "silencio": 80, "salud": 70, "contemplacion": 70, "ansiedad": -10}},
        {"id": 32, "titulo": "La Magia de tus Manos", "descripcion": "Observa las líneas y detalles de tus propias manos. Son herramientas poderosas que te acompañan cada día. Conéctate con ellas, con tu propia fuerza.", "vector_necesidades": {"contemplacion": 95, "aprendizaje": 70, "silencio": 80, "esperanza": 60, "creatividad": 50, "aislamiento": 40}},
        {"id": 33, "titulo": "Paisaje Interno", "descripcion": "Cierra los ojos e imagina tu paisaje natural favorito por 30 segundos. Visualiza los colores, los sonidos, los olores. Escapa a ese lugar dentro de ti.", "vector_necesidades": {"naturaleza": 100, "contemplacion": 95, "silencio": 90, "descanso": 85, "creatividad": 80, "prision_mental": -20}},
        {"id": 34, "titulo": "Estiramiento de Alma", "descripcion": "Siéntate en el suelo con las piernas estiradas y trata de tocar tus pies suavemente. Siente el estiramiento en tu espalda. Libera la tensión guardada.", "vector_necesidades": {"movimiento": 90, "salud": 85, "descanso": 70, "organizacion": 40, "silencio": 50, "agotamiento_mental": -5}},
        {"id": 35, "titulo": "Respiración Profunda Nasal", "descripcion": "Haz 5 respiraciones profundas, solo por la nariz. Siente el aire entrar y salir, llenando tus pulmones. Este es un ancla a tu presente.", "vector_necesidades": {"silencio": 100, "descanso": 95, "salud": 90, "aire_fresco": 80, "contemplacion": 90, "ansiedad": -15}},
        {"id": 36, "titulo": "Juego de Luz y Sombras", "descripcion": "Con tus manos, crea una forma en la pared con la luz de una lámpara. Observa cómo cambia. Reconecta con el juego y la imaginación simple.", "vector_necesidades": {"juego": 100, "creatividad": 90, "risa": 70, "contemplacion": 60, "descanso": 50, "prision_mental": -10}},
        {"id": 37, "titulo": "Abrazo al Interior", "descripcion": "Abraza tus brazos fuertemente, como si te estuvieras dando un abrazo a ti mismo. Siente la calidez, la seguridad. Eres tu propio refugio.", "vector_necesidades": {"comunidad": 90, "esperanza": 80, "descanso": 70, "risa": 60, "silencio": 50, "soledad": -20, "aislamiento": -15}},
        {"id": 38, "titulo": "Exploración de Colores", "descripcion": "Busca rápidamente 5 objetos de color azul en tu entorno. Enfoca tu vista en los detalles. Despierta tu mente a la observación activa.", "vector_necesidades": {"organizacion": 80, "aprendizaje": 70, "juego": 60, "creatividad": 50, "contemplacion": 70, "monotonia": -5}},
        {"id": 39, "titulo": "Masaje Facial Calmante", "descripcion": "Con las yemas de tus dedos, masajea suavemente tu frente y mejillas. Siente la presión, el alivio. Libera la tensión facial acumulada.", "vector_necesidades": {"descanso": 100, "salud": 90, "silencio": 85, "movimiento": 50, "contemplacion": 70, "ansiedad": -10}},
        {"id": 40, "titulo": "El Sonido del Hogar", "descripcion": "Siéntate cómodo, cierra los ojos y solo escucha los sonidos de tu casa. Cada crujido, cada susurro. Estás en tu espacio seguro.", "vector_necesidades": {"silencio": 100, "contemplacion": 95, "descanso": 90, "aprendizaje": 70, "naturaleza": 60, "prision_mental": -10}},
        {"id": 41, "titulo": "Tensa y Suelta los Pies", "descripcion": "Aprieta los dedos de tus pies fuertemente durante 5 segundos y luego relájalos completamente. Siente la tensión, luego la liberación. Una pausa consciente.", "vector_necesidades": {"movimiento": 90, "descanso": 80, "salud": 70, "organizacion": 40, "silencio": 50, "agotamiento_mental": -5}},
        {"id": 42, "titulo": "Cambio Mínimo, Gran Impacto", "descripcion": "Organiza cinco objetos que estén fuera de lugar en tu habitación. No es una tarea, es un micro-logro. Siente el control restaurado.", "vector_necesidades": {"organizacion": 100, "descanso": 70, "contemplacion": 60, "movimiento": 30, "silencio": 50, "carga_trabajo": 70, "prision_mental": -5}},
        {"id": 43, "titulo": "Descanso Visual Profundo", "descripcion": "Durante dos minutos, mira un punto lejano a través de la ventana. Permite que tus ojos descansen de la cercanía de las pantallas. Tu visión se expande.", "vector_necesidades": {"contemplacion": 95, "silencio": 85, "descanso": 90, "naturaleza": 70, "salud": 80, "agotamiento_mental": -10}},
        {"id": 44, "titulo": "Respiración con Propósito", "descripcion": "Realiza cinco respiraciones profundas siguiendo un ritmo lento y consciente. Concéntrate solo en el aire que entra y sale. Este es tu ancla al presente.", "vector_necesidades": {"silencio": 100, "descanso": 95, "salud": 90, "contemplacion": 90, "aire_fresco": 80, "ansiedad": -15, "agotamiento_mental": -10}},
        {"id": 45, "titulo": "Conexión a la Naturaleza Interior", "descripcion": "Abre una ventana durante dos minutos y observa el cielo sin mirar el teléfono. Siente la inmensidad, la quietud. Conecta con lo que es real fuera de ti.", "vector_necesidades": {"aire_fresco": 100, "naturaleza": 90, "contemplacion": 95, "descanso": 80, "silencio": 70, "prision_mental": -15}},
    ],
    "CASA_EN": [
        {"id": 1, "titulo": "Deep Mental Reset", "descripcion": "Close your eyes. Listen to your breath for one minute. Let the silence clear your mind of noise. Feel your body anchoring you.", "vector_necesidades": {"contemplacion": 95, "descanso": 90, "silencio": 100, "organizacion": 70, "esperanza": 80, "prision_mental": -20, "agotamiento_mental": -15, "ansiedad": -10}},
        {"id": 2, "titulo": "Total Role Disconnection", "descripcion": "Feel the weight of your chair. The floor supports your existence. Allow all responsibility to vanish for an instant. You are safe, you are here.", "vector_necesidades": {"descanso": 100, "contemplacion": 90, "silencio": 80, "responsabilidad": -20, "aislamiento": 60, "prision_mental": -15, "agotamiento_mental": -10, "ansiedad": -5}},
        {"id": 3, "titulo": "Therapeutic Visual Pause", "descripcion": "Flip your phone over. Look at a corner of the ceiling for 45 seconds. Break the loop of stimuli. Allow your vision to rest and your mind to clear.", "vector_necesidades": {"silencio": 90, "descanso": 85, "contemplacion": 90, "carga_trabajo": -15, "agotamiento_mental": -10, "ansiedad": -5}},
        {"id": 4, "titulo": "Shoulder Release", "descripcion": "Feel your shoulders completely free. Imagine an invisible backpack of weight falling to the floor. Release the physical and mental burden you carry. You are light.", "vector_necesidades": {"descanso": 95, "movimiento": 60, "risa": 40, "esperanza": 85, "carga_trabajo": -20, "responsabilidad": -15, "agotamiento_mental": -10, "ansiedad": -8}},
        {"id": 5, "titulo": "Mindful Drink", "descripcion": "A small sip of cold water. Feel the liquid move through your body. Each drop is life entering, cleansing fatigue. It's a simple, vital reset.", "vector_necesidades": {"agua": 100, "descanso": 70, "silencio": 50, "salud": 80, "agotamiento_mental": -10, "ansiedad": -5}},
        {"id": 6, "titulo": "Fresh Air Renewal", "descripcion": "Open the window. Let the air hit your face. Feel the outside. Inhale deeply, allow the clean air to renew your energy and dispel confinement.", "vector_necesidades": {"aire_fresco": 100, "naturaleza": 80, "contemplacion": 70, "descanso": 60, "movimiento": 30, "prision_mental": -15, "agotamiento_mental": -10}},
        {"id": 7, "titulo": "Conscious Body Movement", "descripcion": "Gently rotate your wrists and ankles. Your body is yours and responds to your command. You are the master of this engine, activate circulation, release stiffness.", "vector_necesidades": {"movimiento": 95, "descanso": 60, "salud": 80, "agotamiento_mental": -8, "ansiedad": -4}},
        {"id": 8, "titulo": "Anchor in Gratitude", "descripcion": "Close your eyes. Name one good thing you have today. Say it softly or mentally. Allow hope to fill your present.", "vector_necesidades": {"contemplacion": 100, "silencio": 90, "esperanza": 95, "aprendizaje": 70, "prision_mental": -10, "ansiedad": -7}},
        {"id": 9, "titulo": "Secure Grounding", "descripcion": "Take off your shoes. Rest the soles of your feet on the floor. Feel the coolness or texture. The earth supports you, provides stability. You are anchored.", "vector_necesidades": {"naturaleza": 90, "movimiento": 70, "contemplacion": 80, "silencio": 60, "descanso": 70, "aislamiento": 50, "prision_mental": -15}},
        {"id": 10, "titulo": "Vitality Stretch", "descripcion": "Stretch one arm up as if to touch the ceiling. Hold the tension for a few seconds, then release suddenly. Feel the energy release in your body.", "vector_necesidades": {"movimiento": 95, "descanso": 60, "salud": 80, "agotamiento_mental": -8}},
        {"id": 11, "titulo": "Posture of Dignity", "descripcion": "Straighten your back. Imagine an invisible thread gently pulling your head upwards. Breathe. Your posture is a reflection of your inner strength.", "vector_necesidades": {"salud": 90, "movimiento": 70, "descanso": 80, "silencio": 60, "contemplacion": 70, "responsabilidad": 60}},
        {"id": 12, "titulo": "Regenerative Cold Contact", "descripcion": "Touch a cold surface (a window, a wall). Feel the real temperature. It grounds you in the present, dispelling mental fog.", "vector_necesidades": {"naturaleza": 80, "silencio": 70, "contemplacion": 90, "descanso": 60, "prision_mental": -10}},
        {"id": 13, "titulo": "Shake Off Overwhelm", "descripcion": "Stand up and shake your hands and legs vigorously for 10 seconds, as if shaking off water. Let the overwhelm and fatigue detach from you.", "vector_necesidades": {"movimiento": 100, "risa": 80, "descanso": 70, "juego": 60, "esperanza": 70, "agotamiento_mental": -20, "ansiedad": -15}},
        {"id": 14, "titulo": "Distant Visual Focus", "descripcion": "Look at the farthest object you can see through your window. Allow your eyes to rest from the close focus of screens. Expand your vision, expand your mind.", "vector_necesidades": {"contemplacion": 95, "silencio": 85, "naturaleza": 70, "descanso": 80, "creatividad": 40, "carga_trabajo": -10}},
        {"id": 15, "titulo": "Recall Calm", "descripcion": "Close your eyes and recall a real moment of deep calm in your life. Relive that feeling. Peace resides within you.", "vector_necesidades": {"esperanza": 90, "contemplacion": 95, "risa": 70, "silencio": 80, "descanso": 85, "ansiedad": -10, "prision_mental": -15}},
        {"id": 16, "titulo": "The Power of a Smile", "descripcion": "Smile for 15 seconds, even if you don't feel like it. Physical action can influence your internal state. Generate a small spark of positivity.", "vector_necesidades": {"risa": 100, "esperanza": 90, "juego": 70, "creatividad": 50, "salud": 80, "prision_mental": -10}},
        {"id": 17, "titulo": "Restorative Darkness", "descripcion": "Cover your eyes with your palms, gently intertwined. Enjoy one minute of complete darkness. Allow your eyes and mind to rest deeply.", "vector_necesidades": {"descanso": 100, "silencio": 90, "contemplacion": 80, "salud": 70, "agotamiento_mental": -15, "ansiedad": -10}},
        {"id": 18, "titulo": "Beat of Your Core", "descripcion": "Place your right hand over your chest, on your heart area. Feel the heartbeat. It is your vital engine. You are present, you are alive.", "vector_necesidades": {"contemplacion": 100, "silencio": 90, "descanso": 80, "salud": 70, "ansiedad": -10}},
        {"id": 19, "titulo": "Liberating Neck Movement", "descripcion": "Perform slow circles with your head. Feel the tension accumulated from screens or worry release. Let go of stiffness.", "vector_necesidades": {"movimiento": 80, "descanso": 90, "salud": 90, "silencio": 70, "carga_trabajo": -10, "agotamiento_mental": -5}},
        {"id": 20, "titulo": "Reconnection by Scent", "descripcion": "Find a flower, coffee, or spice at home. Smell it consciously. Concentrate on the aroma. Allow this small act to bring you to the present.", "vector_necesidades": {"naturaleza": 80, "alimentacion": 70, "contemplacion": 90, "silencio": 80, "descanso": 70, "prision_mental": -5}},
        {"id": 21, "titulo": "Spatial Perspective Shift", "descripcion": "Sit in another chair or a different spot in the house for 5 minutes. A small change in your environment can generate a new mental perspective.", "vector_necesidades": {"movimiento": 60, "creatividad": 50, "descanso": 70, "organizacion": 40, "contemplacion": 60, "monotonia": -10}},
        {"id": 22, "titulo": "Directed Solitude Release", "descripcion": "Exhale any dull worry or feeling of loneliness. Imagine it leaving your body with the air. You are clearing the external noise. You are strong.", "vector_necesidades": {"esperanza": 90, "silencio": 80, "descanso": 85, "risa": 50, "creatividad": 60, "soledad": -20, "aislamiento": -15, "ansiedad": -10}},
        {"id": 23, "titulo": "Full Presence", "descripcion": "You are here. You are completely safe. You have control of this instant. Allow yourself to feel absolute peace in this second.", "vector_necesidades": {"esperanza": 100, "contemplacion": 95, "silencio": 90, "descanso": 85, "organizacion": 70, "prision_mental": -25, "agotamiento_mental": -20, "ansiedad": -15}},
        {"id": 24, "titulo": "Sing Your Freedom", "descripcion": "Hum your favorite song softly. Don't think about the words, just the melody. Feel the sound within you, releasing monotony.", "vector_necesidades": {"musica": 100, "risa": 70, "creatividad": 80, "descanso": 60, "juego": 50, "prision_mental": -10}},
        {"id": 25, "titulo": "Wishes for Today", "descripcion": "On a piece of paper, write down three simple wishes you'd like to fulfill today. Focus on possibility, not obligation. Let hope guide your day.", "vector_necesidades": {"creatividad": 90, "aprendizaje": 70, "organizacion": 80, "esperanza": 95, "contemplacion": 70, "carga_trabajo": 60}},
        {"id": 26, "titulo": "Mindful Walk at Home", "descripcion": "Walk slowly down a hallway in your house, feeling each step on the floor. Pay attention to the texture, the sound. You are present in your space.", "vector_necesidades": {"movimiento": 70, "contemplacion": 80, "silencio": 70, "descanso": 60, "organizacion": 50, "prision_mental": -5}},
        {"id": 27, "titulo": "Observe Green Life", "descripcion": "If you have a plant at home, observe it attentively for one minute. Notice its colors, its shapes. Connect with the silent life around you.", "vector_necesidades": {"naturaleza": 90, "contemplacion": 95, "silencio": 80, "descanso": 70, "aprendizaje": 60, "aislamiento": 50}},
        {"id": 28, "titulo": "Draw a Perfect Circle", "descripcion": "Take a pencil and paper. Draw circles, one after another, without thinking about anything but the perfect shape. Allow this simple act to center you.", "vector_necesidades": {"creatividad": 100, "juego": 80, "contemplacion": 70, "silencio": 60, "descanso": 50, "carga_trabajo": -5}},
        {"id": 29, "titulo": "Listen to Nature's Melody", "descripcion": "If it's raining or windy, open the window and listen to the sound of nature. Let the natural rhythm cradle your mind and dispel stress.", "vector_necesidades": {"naturaleza": 100, "silencio": 95, "agua": 90, "contemplacion": 90, "descanso": 85, "ansiedad": -15}},
        {"id": 30, "titulo": "Dance Your Release", "descripcion": "Move your body freely for one minute, as if no one is watching. Release accumulated tension. Allow internal music to guide your movement.", "vector_necesidades": {"movimiento": 100, "juego": 90, "risa": 80, "creatividad": 70, "musica": 50, "agotamiento_mental": -15, "prision_mental": -10}},
        {"id": 31, "titulo": "Calm Infusion", "descripcion": "Prepare a warm (caffeine-free) infusion and drink it slowly. Feel the warmth in your hands, the aroma. Concentrate only on this moment of stillness.", "vector_necesidades": {"alimentacion": 90, "descanso": 100, "silencio": 80, "salud": 70, "contemplacion": 70, "ansiedad": -10}},
        {"id": 32, "titulo": "The Magic of Your Hands", "descripcion": "Observe the lines and details of your own hands. They are powerful tools that accompany you every day. Connect with them, with your own strength.", "vector_necesidades": {"contemplacion": 95, "aprendizaje": 70, "silencio": 80, "esperanza": 60, "creatividad": 50, "aislamiento": 40}},
        {"id": 33, "titulo": "Inner Landscape", "descripcion": "Close your eyes and imagine your favorite natural landscape for 30 seconds. Visualize the colors, sounds, smells. Escape to that place within you.", "vector_necesidades": {"naturaleza": 100, "contemplacion": 95, "silencio": 90, "descanso": 85, "creatividad": 80, "prision_mental": -20}},
        {"id": 34, "titulo": "Soul Stretch", "descripcion": "Sit on the floor with your legs stretched out and try to touch your feet gently. Feel the stretch in your back. Release stored tension.", "vector_necesidades": {"movimiento": 90, "salud": 85, "descanso": 70, "organizacion": 40, "silencio": 50, "agotamiento_mental": -5}},
        {"id": 35, "titulo": "Deep Nasal Breathing", "descripcion": "Take 5 deep breaths, only through your nose. Feel the air entering and leaving, filling your lungs. This is an anchor to your present.", "vector_necesidades": {"silencio": 100, "descanso": 95, "salud": 90, "aire_fresco": 80, "contemplacion": 90, "ansiedad": -15}},
        {"id": 36, "titulo": "Light and Shadow Play", "descripcion": "With your hands, create a shape on the wall with the light from a lamp. Watch it change. Reconnect with simple play and imagination.", "vector_necesidades": {"juego": 100, "creatividad": 90, "risa": 70, "contemplacion": 60, "descanso": 50, "prision_mental": -10}},
        {"id": 37, "titulo": "Inner Embrace", "descripcion": "Hug your arms tightly, as if you are giving yourself a hug. Feel the warmth, the security. You are your own refuge.", "vector_necesidades": {"comunidad": 90, "esperanza": 80, "descanso": 70, "risa": 60, "silencio": 50, "soledad": -20, "aislamiento": -15}},
        {"id": 38, "titulo": "Color Exploration", "descripcion": "Quickly find 5 blue objects in your surroundings. Focus your sight on the details. Awaken your mind to active observation.", "vector_necesidades": {"organizacion": 80, "aprendizaje": 70, "juego": 60, "creatividad": 50, "contemplacion": 70, "monotonia": -5}},
        {"id": 39, "titulo": "Calming Facial Massage", "descripcion": "With your fingertips, gently massage your forehead and cheeks. Feel the pressure, the relief. Release accumulated facial tension.", "vector_necesidades": {"descanso": 100, "salud": 90, "silencio": 85, "movimiento": 50, "contemplacion": 70, "ansiedad": -10}},
        {"id": 40, "titulo": "The Sound of Home", "descripcion": "Sit comfortably, close your eyes, and just listen to the sounds of your home. Every creak, every whisper. You are in your safe space.", "vector_necesidades": {"silencio": 100, "contemplacion": 95, "descanso": 90, "aprendizaje": 70, "naturaleza": 60, "prision_mental": -10}},
        {"id": 41, "titulo": "Tense and Release Feet", "descripcion": "Squeeze your toes tightly for 5 seconds and then completely relax them. Feel the tension, then the release. A conscious pause.", "vector_necesidades": {"movimiento": 90, "descanso": 80, "salud": 70, "organizacion": 40, "silencio": 50, "agotamiento_mental": -5}},
        {"id": 42, "titulo": "Minimal Change, Big Impact", "descripcion": "Organize five misplaced objects in your room. It's not a chore, it's a micro-achievement. Feel control restored.", "vector_necesidades": {"organizacion": 100, "descanso": 70, "contemplacion": 60, "movimiento": 30, "silencio": 50, "carga_trabajo": 70, "prision_mental": -5}},
        {"id": 43, "titulo": "Deep Visual Rest", "descripcion": "For two minutes, look at a distant point through the window. Allow your eyes to rest from the closeness of screens. Your vision expands.", "vector_necesidades": {"contemplacion": 95, "silencio": 85, "descanso": 90, "naturaleza": 70, "salud": 80, "agotamiento_mental": -10}},
        {"id": 44, "titulo": "Purposeful Breathing", "descripcion": "Take five deep breaths following a slow, conscious rhythm. Focus only on the air entering and leaving. This is your anchor to the present.", "vector_necesidades": {"silencio": 100, "descanso": 95, "salud": 90, "contemplacion": 90, "aire_fresco": 80, "ansiedad": -15, "agotamiento_mental": -10}},
        {"id": 45, "titulo": "Connection to Inner Nature", "descripcion": "Open a window for two minutes and observe the sky without looking at your phone. Feel the vastness, the stillness. Connect with what is real outside of you.", "vector_necesidades": {"aire_fresco": 100, "naturaleza": 90, "contemplacion": 95, "descanso": 80, "silencio": 70, "prision_mental": -15}},
    ],
    "SALIR": {
        "agotado": [
            {"id": 101, "titulo": "Refugio Bajo las Hojas", "titulo_en": "Shelter Under the Leaves", "porque": "Mente agotada por pantallas y responsabilidades. Necesitas una desconexión orgánica y un respiro fresco para renovar tu ser.", "porque_en": "Mind exhausted by screens and responsibilities. You need an organic disconnection and a fresh breath to renew your being.", "que_hacer": "Busca un gran árbol en un parque cercano. Toca su corteza, siente la textura. Permanece un momento bajo su sombra fresca. Deja que la naturaleza te recargue.", "que_hacer_en": "Find a large tree in a nearby park. Touch its bark, feel the texture. Stay for a moment under its cool shade. Let nature recharge you.", "donde": "Un parque verde y apacible.", "donde_en": "A green and peaceful park.", "gps": "quiet park with shade trees", "vector_necesidades": {"movimiento": 60, "naturaleza": 100, "silencio": 80, "sombra": 100, "aire_fresco": 100, "contemplacion": 95, "descanso": 90, "esperanza": 85, "agotamiento_mental": -20, "prision_mental": -15}},
            {"id": 102, "titulo": "Remanso de Silencio", "titulo_en": "Haven of Silence", "porque": "Exiges un respiro mental profundo. Evita el ruido y busca la calma introspectiva. Tu mente necesita paz para reorganizarse.", "porque_en": "Demanding a deep mental break. Avoid noise and seek introspective calm. Your mind needs peace to reorganize.", "que_hacer": "Visita una cafetería tranquila o una biblioteca. Pide tu bebida o simplemente siéntate. Observa tu entorno sin distracciones digitales. Permite que el silencio te envuelva.", "que_hacer_en": "Visit a quiet cafe or library. Order your drink or simply sit. Observe your surroundings without digital distractions. Let silence envelop you.", "donde": "Establecimiento local tranquilo.", "donde_en": "Peaceful local establishment.", "gps": "quiet cafe or library", "vector_necesidades": {"movimiento": 20, "silencio": 95, "contemplacion": 95, "descanso": 85, "organizacion": 70, "alimentacion": 60, "esperanza": 70, "agotamiento_mental": -15, "ansiedad": -10}},
            {"id": 103, "titulo": "Santuario Botánico Personal", "titulo_en": "Personal Botanical Sanctuary", "porque": "Cerebro sobrecargado. Reconéctate con lo esencial de la naturaleza. Necesitas aire puro y belleza para sanar el agotamiento.", "porque_en": "Overloaded brain. Reconnect with nature's essence. You need pure air and beauty to heal exhaustion.", "que_hacer": "Pasea sin prisa por los senderos de un jardín botánico o un parque con mucha vegetación. Contempla las plantas, sus texturas, sus colores. Respira hondo y siente la renovación.", "que_hacer_en": "Stroll leisurely through the paths of a botanical garden or a park with abundant vegetation. Contemplate the plants, their textures, their colors. Breathe deeply and feel the renewal.", "donde": "Jardín botánico público o parque con flora abundante.", "donde_en": "Public botanical garden or park with abundant flora.", "gps": "botanical garden or nature park", "vector_necesidades": {"movimiento": 70, "naturaleza": 100, "silencio": 75, "agua": 50, "sol": 70, "sombra": 90, "aire_fresco": 100, "creatividad": 80, "contemplacion": 90, "descanso": 80, "esperanza": 90, "agotamiento_mental": -20, "prision_mental": -15}},
            {"id": 104, "titulo": "Visión de la Inmensidad", "titulo_en": "Vision of Immensity", "porque": "Requieres perspectiva. Eleva tu mirada y rompe la rutina visual que te aprisiona. Conecta con algo más grande que tus preocupaciones.", "porque_en": "Requiring perspective. Elevate your gaze and break the visual routine that traps you. Connect with something larger than your worries.", "que_hacer": "Encuentra un mirador o un punto alto. Observa el horizonte. Siente la inmensidad del paisaje. Deja que tus problemas se minimicen ante la magnitud del mundo.", "que_hacer_en": "Find an overlook or a high point. Observe the horizon. Feel the immensity of the landscape. Let your problems shrink before the world's magnitude.", "donde": "Mirador público o zona elevada con vista panorámica.", "donde_en": "Public overlook or elevated area with panoramic view.", "gps": "scenic overlook or high point view", "vector_necesidades": {"movimiento": 40, "naturaleza": 90, "silencio": 85, "agua": 60, "sol": 80, "aire_fresco": 95, "contemplacion": 100, "descanso": 70, "esperanza": 95, "prision_mental": -25, "ansiedad": -15}},
            {"id": 105, "titulo": "Respiración Profunda Guiada", "titulo_en": "Guided Deep Breathing", "porque": "Mente sobrecargada, cuerpo tenso. Busca calma interna y regula tu sistema. La respiración es tu ancla vital.", "porque_en": "Overloaded mind, tense body. Seek inner calm and regulate your system. Breath is your vital anchor.", "que_hacer": "Busca un lugar tranquilo. Cierra los ojos. Concéntrate en la respiración: inhala profundamente, retén y exhala lentamente. Repite varias veces, soltando cada tensión con el aire.", "que_hacer_en": "Find a quiet place. Close your eyes. Concentrate on breathing: inhale deeply, hold, and exhale slowly. Repeat several times, releasing each tension with the air.", "donde": "Espacio tranquilo, sala de espera, vehículo estacionado.", "donde_en": "Quiet space, waiting room, parked vehicle.", "gps": "quiet park bench", "vector_necesidades": {"movimiento": 10, "silencio": 100, "aire_fresco": 60, "creatividad": 50, "contemplacion": 100, "descanso": 100, "organizacion": 80, "esperanza": 90, "agotamiento_mental": -25, "ansiedad": -20, "prision_mental": -20}},
            {"id": 106, "titulo": "Paseo Contemplativo en Almacén", "titulo_en": "Contemplative Warehouse Walk", "porque": "Agotamiento por sedentarismo y monotonía visual. Mover las piernas en un entorno amplio y diferente limpia tu mente y activa tu cuerpo sin esfuerzo.", "porque_en": "Exhaustion from sedentary lifestyle and visual monotony. Moving your legs in a spacious, different environment clears your mind and activates your body effortlessly.", "que_hacer": "Dirígete a un almacén mayorista o tienda de gran superficie. Camina a paso firme por los pasillos perimetrales sin prisa de comprar. Observa el lugar, usa este sitio climatizado para activar tus extremidades.", "que_hacer_en": "Head to a wholesale warehouse or large department store. Walk steadily through the perimeter aisles without any shopping rush. Observe the place, use this climate-controlled site to activate your limbs.", "donde": "Pasillos amplios de una tienda de autoservicio o almacén.", "donde_en": "Spacious aisles of a self-service store or warehouse.", "gps": "wholesale club or large market", "vector_necesidades": {"movimiento": 85, "organizacion": 70, "contemplacion": 60, "comunidad": 50, "juego": 30, "descanso": 20, "silencio": 10, "agotamiento_mental": -10, "prision_mental": -5}},
            {"id": 107, "titulo": "Oasis Burocrático de Quietud", "titulo_en": "Bureaucratic Oasis of Quietness", "porque": "Fatiga extrema producida por esperas tensas, trámites o estímulos digitales repetitivos. Necesitas un espacio de calma absoluta.", "porque_en": "Extreme fatigue produced by tense waiting, procedures, or repetitive digital stimuli. You need a space of absolute calm.", "que_hacer": "Ubica la biblioteca pública más cercana. Ingresa en absoluto silencio. Toma asiento en la sala común o zona de lectura. Disfruta de la quietud del entorno. Permite que tus ojos y tu mente descansen por completo.", "que_hacer_en": "Locate the nearest public library. Enter in absolute silence. Take a seat in the common room or reading zone. Enjoy the stillness of the environment. Allow your eyes and mind to rest completely.", "donde": "Sala de lectura, biblioteca municipal o zona de estudio.", "donde_en": "Reading room, municipal library, or study zone.", "gps": "public library", "vector_necesidades": {"aprendizaje": 100, "silencio": 100, "contemplacion": 90, "descanso": 85, "organizacion": 70, "salud": 80, "agotamiento_mental": -20, "ansiedad": -15, "carga_trabajo": -10}},
        ],
        "estresado": [
            {"id": 108, "titulo": "Desahogo de Energía Física", "titulo_en": "Physical Energy Release", "porque": "Cuerpo tenso, mente agitada. Libera tensiones al moverte con propósito. Siente tu fuerza interior y transforma el estrés.", "porque_en": "Tense body, agitated mind. Release tension by moving with purpose. Feel your inner strength and transform stress.", "que_hacer": "Encuentra una rampa, escaleras públicas o una colina. Sube a paso firme, concéntrate en cada paso. Usa tu energía para liberar el estrés acumulado. Suda y suelta.", "que_hacer_en": "Find a ramp, public stairs, or a hill. Climb steadily, focusing on each step. Use your energy to release accumulated stress. Sweat and let go.", "donde": "Escalera pública o zona con pendiente.", "donde_en": "Public stairs or sloped area.", "gps": "public stairs or hill", "vector_necesidades": {"movimiento": 100, "naturaleza": 30, "silencio": 50, "sol": 70, "aire_fresco": 85, "contemplacion": 60, "descanso": 10, "organizacion": 30, "esperanza": 75, "estres": -25, "agotamiento_mental": -15}},
            {"id": 109, "titulo": "Armonía al Aire Libre", "titulo_en": "Outdoor Harmony", "porque": "Mente acelerada por el estrés. Conecta cuerpo y naturaleza para encontrar tu centro. La respiración consciente es tu herramienta.", "porque_en": "Mind racing due to stress. Connect body and nature to find your center. Conscious breathing is your tool.", "que_hacer": "Busca un parque tranquilo. Siéntate o extiende una manta. Sigue una rutina de estiramientos simples o enfócate en tu respiración. Permite que el entorno natural te calme.", "que_hacer_en": "Find a quiet park. Sit or spread a blanket. Follow a simple stretching routine or focus on your breath. Let the natural environment calm you.", "donde": "Parque tranquilo o área verde abierta.", "donde_en": "Quiet park or open green area.", "gps": "quiet park for stretching", "vector_necesidades": {"movimiento": 90, "naturaleza": 90, "silencio": 70, "sol": 70, "sombra": 60, "aire_fresco": 95, "creatividad": 60, "contemplacion": 80, "descanso": 70, "esperanza": 80, "estres": -20, "ansiedad": -15}},
            {"id": 110, "titulo": "Transformación de Tensión", "titulo_en": "Tension Transformation", "porque": "Necesitas liberar energía acumulada. Convierte la tensión en fuerza constructiva. Activa tu cuerpo y tu mente para un cambio positivo.", "porque_en": "Need to release accumulated energy. Convert tension into constructive strength. Activate your body and mind for positive change.", "que_hacer": "Visita un centro deportivo público o un gimnasio. Enfócate en una rutina de ejercicios que disfrutes. Suda y siente cómo la tensión se disuelve en cada movimiento. Tu cuerpo es una herramienta poderosa.", "que_hacer_en": "Visit a public sports center or gym. Focus on an exercise routine you enjoy. Sweat and feel tension dissolve with each movement. Your body is a powerful tool.", "donde": "Gimnasio o centro deportivo comunitario.", "donde_en": "Community gym or sports center.", "gps": "community gym or recreation center", "vector_necesidades": {"movimiento": 100, "silencio": 20, "agua": 10, "aire_fresco": 60, "comunidad": 70, "organizacion": 80, "musica": 80, "risa": 40, "esperanza": 60, "estres": -30, "agotamiento_mental": -20, "carga_trabajo": -15}},
            {"id": 111, "titulo": "Impacto Liberador Corporal", "titulo_en": "Body Liberating Impact", "porque": "Rigidez muscular y emociones contenidas. Necesitas un quiebre físico para liberar el agobio y la presión que sientes.", "porque_en": "Muscular rigidity and contained emotions. You need a physical breakthrough to release the overwhelm and pressure you feel.", "que_hacer": "Dirígete a un parque de trampolines o un centro de escalada (si es accesible). Salta o usa tus manos para subir. Deja que el esfuerzo extreme drene el agobio diario. Siente la libertad del movimiento.", "que_hacer_en": "Head to a trampoline park or climbing center (if accessible). Jump or use your hands to climb. Let extreme effort drain daily overwhelm. Feel the freedom of movement.", "donde": "Parque de trampolines o centro de escalada.", "donde_en": "Trampoline park or climbing center.", "gps": "trampoline park or climbing gym", "vector_necesidades": {"movimiento": 100, "juego": 100, "risa": 90, "salud": 95, "silencio": 10, "comunidad": 60, "esperanza": 90, "estres": -35, "ansiedad": -25, "prision_mental": -20}},
            {"id": 112, "titulo": "Remanso de Hidro-Calma", "titulo_en": "Hydro-Calm Haven", "porque": "Sistema nervioso en alerta roja permanente. El contacto con agua templada en movimiento es el alivio corporal y mental definitivo. Permite que te envuelva.", "porque_en": "Nervous system on permanent red alert. Contact with moving warm water is the ultimate body and mental relief. Let it envelop you.", "que_hacer": "Visita un centro recreativo con piscina municipal o un YMCA. Sumérgete en el agua templada o en un jacuzzi. Cierra los ojos. Permite que las burbujas den un masaje a tu cuerpo. Concéntrate en flotar y en la quietud.", "que_hacer_en": "Visit a recreation center with a municipal pool or YMCA. Submerge in warm water or a jacuzzi. Close your eyes. Let the bubbles massage your body. Focus on floating and stillness.", "donde": "YMCA, alberca climatizada o spa comunitario local.", "donde_en": "YMCA, heated pool, or local community spa.", "gps": "ymca pool or public spa", "vector_necesidades": {"agua": 100, "descanso": 100, "salud": 95, "silencio": 60, "contemplacion": 90, "sombra": 80, "esperanza": 85, "estres": -30, "ansiedad": -20, "agotamiento_mental": -15}},
            {"id": 113, "titulo": "Desconexión de Frecuencias", "titulo_en": "Frequency Disconnection", "porque": "Mente acelerada con ideas fijas y un zumbido interno debido al estrés constante. Necesitas un quiebre sonoro y mental.", "porque_en": "Racing mind with fixed ideas and internal buzzing due to constant stress. You need a sonic and mental break.", "que_hacer": "Busca un estudio de yoga, meditación o un espacio de sound healing (si es accesible). Asiste a una sesión o siéntate en su vestíbulo en silencio. Cierra los ojos. Escucha la quietud del lugar. Inhala en cuatro tiempos y exhala en ocho. Reconecta con tu propio ritmo.", "que_hacer_en": "Search for a yoga or meditation studio or a sound healing space (if accessible). Attend a session or sit in its lobby in silence. Close your eyes. Listen to the stillness of the place. Inhale for four counts and exhale for eight. Reconnect with your own rhythm.", "donde": "Estudio de yoga, centro de meditación o sound healing.", "donde_en": "Yoga studio, meditation center, or sound healing spot.", "gps": "sound healing or yoga studio", "vector_necesidades": {"silencio": 100, "descanso": 95, "musica": 90, "contemplacion": 95, "salud": 90, "esperanza": 90, "organizacion": 70, "estres": -35, "ansiedad": -25, "prision_mental": -20}},
            {"id": 114, "titulo": "Escape Orgánico al Bosque", "titulo_en": "Organic Forest Escape", "porque": "Estrés de la ciudad o la oficina. Requieres los elementos del bosque y el aire puro para calmar tu cuerpo y tu mente. Desconecta del concreto.", "porque_en": "City or office stress. You need forest elements and pure air to calm your body and mind. Disconnect from concrete.", "que_hacer": "Dirígete al parque estatal o reserva protegida más cercana. Entra a un sendero. Camina descalzo sobre la tierra o toca la corteza de un gran árbol por un minuto. Siente la brisa fresca en tu cara, lejos del asfalto.", "que_hacer_en": "Head to the nearest State Park or protected reserve. Enter a trail. Walk barefoot on the earth or touch the bark of a large tree for a minute. Feel the fresh breeze on your face, away from asphalt.", "donde": "Sendero boscoso, reserva natural o parque estatal.", "donde_en": "Wooded trail, nature reserve, or state park.", "gps": "state park trail or nature reserve", "vector_necesidades": {"naturaleza": 100, "aire_fresco": 100, "silencio": 85, "movimiento": 60, "contemplacion": 90, "descanso": 60, "esperanza": 95, "sol": 70, "estres": -30, "ansiedad": -20, "prision_mental": -15}},
], "aburrido": [ {"id": 115, "titulo": "Galería de Colores Urbanos", "titulo_en": "Urban Color Gallery", "porque": "Días repetitivos y sin inspiración. Busca novedad y despierta tu visión a la belleza oculta. Tu mente anhela estímulos frescos.", "porque_en": "Repetitive and uninspired days. Seek novelty and awaken your vision to hidden beauty. Your mind craves fresh stimuli.", "que_hacer": "Camina lentamente por calles con murales o arte urbano. Observa los colores, las formas, los mensajes. Deja que tu creatividad se despierte y el aburrimiento se disipe.", "que_hacer_en": "Walk slowly through streets with murals or urban art. Observe the colors, shapes, messages. Let your creativity awaken and boredom dissipate.", "donde": "Calle con murales o distrito de arte.", "donde_en": "Street with murals or art district.", "gps": "street art or murals", "vector_necesidades": {"movimiento": 80, "naturaleza": 20, "silencio": 40, "sol": 80, "sombra": 50, "aire_fresco": 90, "creatividad": 100, "comunidad": 60, "aprendizaje": 70, "juego": 55, "contemplacion": 85, "descanso": 30, "esperanza": 95, "monotonia": -25, "prision_mental": -10}}, {"id": 116, "titulo": "Descompresión Arquitectónica", "titulo_en": "Architectural Decompression", "porque": "Monotonía del espacio habitual. Necesitas un entorno de hermoso diseño para cambiar tus estímulos visuales y relajar tu mente.", "porque_en": "Usual space monotony. You need a beautifully designed environment to change your visual stimuli and relax your mind.", "que_hacer": "Ubica un hotel o resort cercano. Ingresa y siéntate en una de sus butacas públicas. Observa la architecture, los detalles. Mantén la espalda recta. Descansa un minuto de las pantallas y del ruido mental.", "que_hacer_en": "Locate the nearest hotel or resort. Enter and sit in one of its public armchairs. Observe the architecture, the details. Keep your spine straight. Take a one-minute break from screens and mental noise.", "donde": "Lobby o zona de descanso pública de un hotel.", "donde_en": "Lobby or public lounge area of a hotel.", "gps": "hotel lobby", "vector_necesidades": {"descanso": 100, "silencio": 85, "contemplacion": 95, "organizacion": 80, "esperanza": 80, "comunidad": 50, "movimiento": 20, "monotonia": -20, "agotamiento_mental": -10}}, {"id": 117, "titulo": "Expansión de Horizontes", "titulo_en": "Horizon Expansion", "porque": "Falta de perspectiva y estancamiento. Ver el movimiento de la vida y los viajes te devuelve el enfoque y la esperanza.", "porque_en": "Lack of perspective and stagnation. Watching the movement of life and travel returns your focus and hope.", "que_hacer": "Si estás cerca de una central de transporte, dirígete al vestíbulo principal. Busca el ventanal más amplio con vista al exterior. Realiza tres respiraciones lentas asimilando la inmensidad del espacio y las posibilidades.", "que_hacer_en": "If near a transit center, head to the main lobby. Find the widest window with a view of the outside. Take three slow breaths, taking in the immensity of space and possibilities.", "donde": "Vestíbulo público de aeropuerto o central de transportes.", "donde_en": "Public airport lobby or transit center.", "gps": "transit center or airport terminal", "vector_necesidades": {"contemplacion": 100, "aire_fresco": 90, "esperanza": 95, "descanso": 70, "silencio": 50, "movimiento": 30, "aprendizaje": 60, "monotonia": -20, "prision_mental": -15}}, {"id": 118, "titulo": "Impacto Sensorial de Juego", "titulo_en": "Playful Sensory Impact", "porque": "Bucle mental de apatía o rutina plana. Necesitas un impacto visual y sonoro de juego para romper la inercia. Reconecta con tu niño interior.", "porque_en": "Mental loop of apathy or flat routine. You need a visual and auditory impact of play to break inertia. Reconnect with your inner child.", "que_hacer": "Dirígete al parque de atracciones o centro de entretenimiento más cercano. Observa las luces, escucha las risas del entorno. Permítete conectar con una dinámica de ocio simple para romper la inercia del día. No necesitas participar, solo observar.", "que_hacer_en": "Head to the nearest amusement park or entertainment center. Observe the lights, listen to the laughter around you. Allow yourself to connect with a simple leisure dynamic to break the daytime inertia. You don't need to participate, just observe.", "donde": "Parque recreativo, zona infantil o centro de juegos local.", "donde_en": "Recreation park, kid zone, or local arcade center.", "gps": "amusement park or arcade", "vector_necesidades": {"juego": 100, "risa": 100, "comunidad": 80, "movimiento": 70, "esperanza": 90, "silencio": 20, "descanso": 50, "creatividad": 60, "monotonia": -30, "agotamiento_mental": -10, "ansiedad": -5}}, {"id": 119, "titulo": "Exploración de Arquitecturas", "titulo_en": "Architectural Exploration", "porque": "Falta de inspiración y estancamiento estético. Visualizar arquitecturas alternativas expande tu mente y libera tu imaginación.", "porque_en": "Lack of inspiration and aesthetic stagnation. Visualizing alternative architectures expands your mind and frees your imagination.", "que_hacer": "Desde tu espacio, abre una aplicación de búsqueda de imágenes. Busca 'cabañas remotas' o 'arquitectura minimalista' en tu estado. Analiza el lugar, las texturas y los planos visuales como un ejercicio de imaginación sin obligación de reservar. ", "que_hacer_en": "From your space, open an image search app. Search for 'remote cabins' or 'minimalist architecture' in your state. Analyze the place, textures, and visual layouts as an exercise of imagination without the obligation to book.", "donde": "Interfaz móvil desde tu zona de descanso habitual.", "donde_en": "Mobile interface from your usual resting space.", "gps": "local architect office", "vector_necesidades": {"creatividad": 100, "contemplacion": 95, "juego": 70, "organizacion": 80, "esperanza": 85, "descanso": 60, "aprendizaje": 60, "monotonia": -20, "prision_mental": -10}}, {"id": 120, "titulo": "Reconexión con el Ritmo Urbano", "titulo_en": "Reconnect with Urban Rhythm", "porque": "Monotonía aplastante y falta de estímulos rítmicos o sociales. Necesitas un quiebre sensorial radical mediante ritmos y movimiento para sentirte vivo.", "porque_en": "Crushing monotony and lack of rhythmic or social stimuli. You need a radical sensory break through rhythm and movement to feel alive.", "que_hacer": "Visita una zona de discotecas o un club céntrico nocturno. Sal un momento a la acera peatonal abierta. Escucha la vibración profunda del bajo golpeando las paredes. Siente el pulso acelerado de la vida nocturna, un recordatorio de la diversidad y el movimiento.", "que_hacer_en": "Visit a club district or a downtown nightclub. Step outside to the open pedestrian sidewalk for a moment. Listen to the deep bass vibration hitting the building walls. Feel the accelerated pulse of nightlife, a reminder of diversity and movement.", "donde": "Perímetro exterior de un club nocturno urbano.", "donde_en": "Outer perimeter of an urban nightclub.", "gps": "nightlife district or dance clubs", "vector_necesidades": {"juego": 100, "musica": 100, "comunidad": 90, "risa": 80, "movimiento": 70, "creatividad": 60, "silencio": 10, "descanso": 30, "monotonia": -30, "aislamiento": -20}}, {"id": 121, "titulo": "Terapia de Pasillo Contemplativa", "titulo_en": "Contemplative Aisle Therapy", "porque": "Estancamiento mental en casa y falta de variedad en tu entorno visual inmediato. Necesitas moverte en un espacio amplio y con nueva información visual.", "porque_en": "Mental stagnation at home and lack of variety in your immediate visual environment. You need to move in a spacious environment with new visual information.", "que_hacer": "Dirígete a una gran superficie comercial. Recorre el lugar de forma contemplativa, sin la obligación de comprar. Observa la organización, los productos, la gente. Camina a paso firme para activar el flujo de tus piernas y de tus pensamientos.", "que_hacer_en": "Head to a large department store. Walk through the place contemplatively, without the obligation to shop. Observe the organization, products, people. Walk steadily to activate the flow in your legs and thoughts.", "donde": "Gran superficie comercial o tienda de departamentos.", "donde_en": "Large department store or retail store.", "gps": "department store or large retail", "vector_necesidades": {"movimiento": 80, "organizacion": 70, "contemplacion": 70, "comunidad": 60, "juego": 50, "descanso": 20, "silencio": 15, "monotonia": -20, "prision_mental": -10}}, ], "cansado": [
        "cansado": [
            {"id": 122, "titulo": "Paseo de Reflexión en Biblioteca", "titulo_en": "Reflective Library Walk", "porque": "Cansancio mental. Necesitas calma, aprendizaje sin distracciones y un entorno que recargue tu energía de forma silenciosa. Busca refugio en el conocimiento.", "porque_en": "Mental fatigue. You need calm, undistracted learning, and an environment that silently recharges your energy. Seek refuge in knowledge.", "que_hacer": "Visita tu biblioteca local. Busca un libro que te llame la atención o simplemente disfruta del silencio y la atmósfera. Permite que tu mente descanse y se renueve.", "que_hacer_en": "Visit your local library. Find a book that catches your eye or simply enjoy the silence and atmosphere. Allow your mind to rest and renew.", "donde": "Biblioteca pública o universitaria.", "donde_en": "Public or university library.", "gps": "public library", "vector_necesidades": {"movimiento": 30, "naturaleza": 10, "silencio": 100, "sombra": 80, "aire_fresco": 50, "creatividad": 70, "comunidad": 50, "aprendizaje": 95, "contemplacion": 90, "descanso": 85, "organizacion": 70, "esperanza": 70, "agotamiento_mental": -20, "prision_mental": -15, "carga_trabajo": -10}},
            {"id": 123, "titulo": "Respiro Junto al Agua", "titulo_en": "Water's Edge Respite", "porque": "Cansancio acumulado. Necesitas despejar la mente. El aire fresco y la vista al agua tienen un efecto calmante profundo. Regresa a lo elemental.", "porque_en": "Accumulated fatigue. Need to clear the mind. Fresh air and water views have a deep calming effect. Return to the elemental.", "que_hacer": "Camina por el paseo marítimo, un puerto o un muelle. Observa los barcos, escucha el suave sonido del oleaje. Siente la brisa fresca. Permite que la vastedad del agua calme tus pensamientos.", "que_hacer_en": "Walk along the boardwalk, a harbor, or a pier. Watch the boats, listen to the gentle sound of the waves. Feel the fresh breeze. Let the vastness of the water calm your thoughts.", "donde": "Puerto, muelle o paseo marítimo.", "donde_en": "Harbor, pier, or boardwalk.", "gps": "harbor walk or pier", "vector_necesidades": {"movimiento": 70, "naturaleza": 80, "silencio": 60, "agua": 100, "sol": 70, "sombra": 50, "aire_fresco": 95, "contemplacion": 90, "descanso": 80, "esperanza": 90, "agotamiento_mental": -20, "ansiedad": -15, "prision_mental": -10}},
            {"id": 124, "titulo": "Pausa Estratégica en Ruta", "titulo_en": "Strategic Route Pause", "porque": "Fatiga muscular y embotamiento cognitivo por trayectos continuos. Tu cuerpo y mente necesitan un quiebre deliberado y consciente. Toma el control de tu pausa.", "porque_en": "Muscular fatigue and cognitive dullness from continuous travel. Your body and mind need a deliberate and conscious break. Take control of your pause.", "que_hacer": "Busca la próxima área de servicio segura o zona de descanso. Estaciona completamente, apaga el motor y sal del vehículo. Realiza un suave estiramiento corporal, respira el aire fresco y camina despacio un minuto para reactivar tu circulación y tu mente.", "que_hacer_en": "Find the next safe service area or rest zone. Park completely, turn off the engine, and step out of the vehicle. Do a gentle body stretch, breathe the fresh air, and walk slowly for one minute to reactivate your circulation and mind.", "donde": "Área de servicio de autopista o zona de descanso pública.", "donde_en": "Highway service area or public rest zone.", "gps": "highway rest stop or plaza", "vector_necesidades": {"descanso": 95, "movimiento": 60, "aire_fresco": 90, "salud": 85, "silencio": 50, "contemplacion": 70, "organizacion": 40, "agotamiento_mental": -25, "carga_trabajo": -15}},
            {"id": 125, "titulo": "Recuperación Histórica y Pasiva", "titulo_en": "Historical Passive Recovery", "porque": "Agotamiento mental por la predictibilidad. Necesitas un suave cambio de ritmo y la riqueza visual de un entorno con historia para reactivar tu mente.", "porque_en": "Mental exhaustion due to predictability. You need a gentle change of pace and the visual richness of a historical environment to reactivate your mind.", "que_hacer": "Ubica una zona histórica o plaza antigua a pie. Camina a un paso deliberadamente lento, sin prisa. Contempla las estructuras arquitectónicas, siente la historia del lugar. Usa este entorno para despejar tu mente y reconectar.", "que_hacer_en": "Locate a historical zone or old plaza on foot. Walk at a deliberately slow, unhurried pace. Contemplate the architectural structures, feel the history of the place. Use this environment to clear your mind and reconnect.", "donde": "Centro histórico, plaza pública o calles peatonales.", "donde_en": "Historical center, public plaza, or pedestrian streets.", "gps": "historical landmark or walking tour", "vector_necesidades": {"aprendizaje": 90, "contemplacion": 95, "descanso": 80, "movimiento": 50, "silencio": 70, "creatividad": 60, "esperanza": 80, "agotamiento_mental": -20, "monotonia": -15}},
            {"id": 126, "titulo": "Aislamiento Sensorial Controlado", "titulo_en": "Controlled Sensory Isolation", "porque": "Saturación del sistema nervioso por exceso de interacción o demandas. Necesitas un espacio de penumbra y quietud para restaurar tu equilibrio.", "porque_en": "Nervous system saturation from excessive interaction or demands. You need a space of dim light and stillness to restore your balance.", "que_hacer": "Dirígete al complejo de salas más cercano (cine, teatro). Elige una función matinal o en horario de baja afluencia. Siéntate en la penumbra, suelta el teléfono y permite que la oscuridad y el distanciamiento controlado calmen el ruido de tu mente y el cansancio de tus ojos.", "que_hacer_en": "Head to the nearest theater complex (cinema, theater). Choose a morning or low-traffic screening. Sit in the dim light, drop your phone, and allow the darkness and controlled distancing to quiet the noise in your mind and the fatigue in your eyes.", "donde": "Sala de cine o vestíbulo de proyecciones.", "donde_en": "Commercial movie theater or screening lobby.", "gps": "local cinema or amc", "vector_necesidades": {"descanso": 100, "silencio": 85, "contemplacion": 90, "sombra": 100, "juego": 40, "creatividad": 50, "movimiento": 5, "agotamiento_mental": -25, "prision_mental": -20, "aislamiento": -15}},
            {"id": 127, "titulo": "Homeostasis Verde Total", "titulo_en": "Total Green Homeostasis", "porque": "Agotamiento crónico por el ambiente artificial y la falta de conexión orgánica. Tu cuerpo y mente anhelan la naturaleza.", "porque_en": "Chronic fatigue due to artificial environment and lack of organic connection. Your body and mind yearn for nature.", "que_hacer": "Ubica el jardín botánico o parque floral más cercano. Busca un banco protegido por la vegetación. Permanece allí inmóvil por dos minutos enteros. Respira el aire limpio del ambiente. Deja que los tonos verdes relajen tu mirada y calmen tu ser.", "que_hacer_en": "Locate the nearest botanical garden or floral park. Find a bench sheltered by vegetation. Remain there motionless for two whole minutes. Breathe the clean ambient air. Let the green tones relax your gaze and calm your being.", "donde": "Jardín botánico público, vivero o parque natural regional.", "donde_en": "Public botanical garden, nursery, or regional nature park.", "gps": "botanical garden or nursery", "vector_necesidades": {"naturaleza": 100, "aire_fresco": 100, "descanso": 90, "silencio": 80, "contemplacion": 95, "sombra": 90, "salud": 85, "movimiento": 25, "agotamiento_mental": -30, "ansiedad": -20, "prision_mental": -15}},
            {"id": 128, "titulo": "Módulo de Quietud Acuática", "titulo_en": "Aquatic Stillness Module", "porque": "Cansancio mental plano y monotonía. Necesitas observar el movimiento sutil de la naturaleza sin prisas para restaurar tu equilibrio interno.", "porque_en": "Flat mental fatigue and monotony. You need to observe the subtle movement of nature without haste to restore your internal balance.", "que_hacer": "Encuentra un parque con lago o estanque. Siéntate en el asiento más cercano a la orilla. Observa las ondas del agua y las aves por un minuto. Lleva tu respiración a un ritmo lento y consciente. Conecta con la quietud del agua.", "que_hacer_en": "Find a local park with a lake or pond. Sit on the seat closest to the edge. Observe the water ripples and the birds for a minute. Lead your breathing to a slow, conscious pace. Connect with the stillness of the water.", "donde": "Banco de parque junto a un estanque o lago público.", "donde_en": "Park bench next to a public pond or lake.", "gps": "public lake park or fountain", "vector_necesidades": {"agua": 100, "contemplacion": 100, "descanso": 95, "silencio": 75, "naturaleza": 85, "aire_fresco": 90, "movimiento": 15, "agotamiento_mental": -25, "prision_mental": -15}},
        ],
        "ansioso": [
            {"id": 129, "titulo": "Contemplación del Flujo Natural", "titulo_en": "Contemplation of Natural Flow", "porque": "Mente agitada por la ansiedad. El agua en movimiento tiene un efecto calmante. Relaja tensiones y te ancla en el presente.", "porque_en": "Mind agitated by anxiety. Moving water has a calming effect. It relaxes tensions and anchors you in the present.", "que_hacer": "Busca una fuente, un lago o un río cercano. Observa el flujo de la corriente o las ondas del agua. Déjate llevar por su ritmo. Permite que el movimiento natural disipe tu ansiedad.", "que_hacer_en": "Find a nearby fountain, lake, or river. Observe the stream flow or water ripples. Let yourself be carried by its rhythm. Allow natural movement to dissipate your anxiety.", "donde": "Fuente de agua o lago público.", "donde_en": "Public fountain or lake.", "gps": "public fountain or lake", "vector_necesidades": {"movimiento": 40, "naturaleza": 80, "silencio": 70, "agua": 100, "sol": 60, "sombra": 50, "aire_fresco": 90, "contemplacion": 90, "descanso": 80, "esperanza": 80, "ansiedad": -25, "prision_mental": -15}},
            {"id": 130, "titulo": "Flotando en la Inmensidad", "titulo_en": "Floating in Vastness", "porque": "Estrés y ansiedad acumulados. Necesitas desconexión total. Flota tus preocupaciones y relaja tu cuerpo en un ambiente de calma líquida.", "porque_en": "Accumulated stress and anxiety. Need total disconnection. Float your worries away and relax your body in a liquid calm environment.", "que_hacer": "Realiza un viaje corto en una barca (si es accesible) o simplemente siéntate junto a un cuerpo de agua. Siente la brisa. Observa la inmensidad del paisaje líquido. Permite que tu mente se expanda y tus tensiones se disuelvan.", "que_hacer_en": "Take a short boat trip (if accessible) or simply sit by a body of water. Feel the breeze. Observe the vast liquid landscape. Allow your mind to expand and your tensions to dissolve.", "donde": "Lago o río con alquiler de botes o área costera.", "donde_en": "Lake or river with boat rentals or coastal area.", "gps": "boat rentals lake or river", "vector_necesidades": {"movimiento": 60, "naturaleza": 100, "silencio": 80, "agua": 100, "sol": 80, "sombra": 60, "aire_fresco": 100, "creatividad": 50, "comunidad": 50, "contemplacion": 95, "descanso": 90, "esperanza": 90, "ansiedad": -30, "prision_mental": -20}},
            {"id": 131, "titulo": "Campo de Juego Inocente", "titulo_en": "Innocent Playfield", "porque": "Ansiedad cíclica y rumiación mental. Necesitas un impacto de juego y risas para apagar el pánico y reconectar con la ligereza.", "porque_en": "Cyclic anxiety and mental rumination. You need a shock of play and laughter to quiet panic and reconnect with lightness.", "que_hacer": "Dirígete al parque de mascotas, zona infantil o centro recreativo más cercano. Observa las interacciones de los animales o los niños. Escucha los sonidos del perímetro. Conéctate con la diversión inocente por un minuto para anular el bucle de pensamientos.", "que_hacer_en": "Head to the nearest dog park, kids zone, or recreational center. Observe animal or children's interactions. Listen to the sounds of the perimeter. Connect with innocent fun for a minute to cancel the thought loop.", "donde": "Parque de perros local, zona infantil o centro de juegos.", "donde_en": "Local dog park, kids zone, or arcade center.", "gps": "dog park or amusement arcade", "vector_necesidades": {"juego": 100, "risa": 100, "comunidad": 90, "movimiento": 70, "esperanza": 95, "silencio": 20, "descanso": 50, "creatividad": 40, "ansiedad": -35, "prision_mental": -25}},
            {"id": 132, "titulo": "Refugio de Quietud Consciente", "titulo_en": "Refuge of Conscious Stillness", "porque": "Inquietud social aguda y ruido mental por sobrecarga de responsabilidades. Necesitas un espacio de calma controlada para restaurar tu centro.", "porque_en": "Acute social uneasiness and mental noise from responsibility overload. You need a space of controlled calm to restore your center.", "que_hacer": "Visita el jardín o la sala de un hotel/resort. Siéntate en una de las butacas públicas. Cierra los ojos por sesenta segundos. Respira a un ritmo lento. Habita tu propio cuerpo en total quietud. Siente la seguridad de tu presencia.", "que_hacer_en": "Visit the garden or lounge of a hotel/resort. Sit in one of the public armchairs. Close your eyes for sixty seconds. Breathe at a slow pace. Inhabit your own body in total stillness. Feel the security of your presence.", "donde": "Jardín interior, lobby o zona de descanso de un hotel.", "donde_en": "Interior garden, lobby, or lounge area of a hotel.", "gps": "boutique hotel lobby", "vector_necesidades": {"descanso": 100, "silencio": 95, "contemplacion": 95, "organizacion": 80, "salud": 90, "esperanza": 90, "sombra": 80, "ansiedad": -30, "soledad": -20, "aislamiento": -15, "prision_mental": -20}},
            {"id": 133, "titulo": "Estrategia de Alivio en Tránsito", "titulo_en": "Transit Relief Strategy", "porque": "Sensación de asfixia o claustrofobia mental por la rutina. Necesitas la inmensidad de los espacios de tránsito para sentir que el mundo es grande y tus problemas transitorios.", "porque_en": "Feeling of suffocation or mental claustrophobia from routine. You need the vastness of transit spaces to feel that the world is big and your problems are transient.", "que_hacer": "Si estás cerca de una central de transportes (aeropuerto, estación), camina hacia el vestíbulo principal. Despega la mirada de la pantalla. Observa a los viajeros partir. Asimila que el mundo es inmenso y tu problema actual es transitorio. Respira la amplitud.", "que_hacer_en": "If near a transit center (airport, station), walk to the main lobby. Take your eyes off the screen. Watch travelers depart. Assimilate that the world is immense and your current issue is transient. Breathe the vastness.", "donde": "Vestíbulo público de aeropuerto o central de transportes.", "donde_en": "Public airport lobby or transit center.", "gps": "transit center or airport terminal", "vector_necesidades": {"contemplacion": 100, "aire_fresco": 90, "esperanza": 95, "descanso": 70, "silencio": 60, "movimiento": 40, "aprendizaje": 50, "ansiedad": -25, "prision_mental": -20, "carga_trabajo": -15}},
            {"id": 134, "titulo": "Silencio Comunitario Reparador", "titulo_en": "Restorative Community Silence", "porque": "Aislamiento mental nocivo y parálisis por ansiedad social. Necesitas estar rodeado de flujos humanos tranquilos para sentirte conectado, pero seguro.", "porque_en": "Harmful mental isolation and social anxiety paralysis. You need to be surrounded by calm human flows to feel connected, but safe.", "que_hacer": "Dirígete a una cafetería tranquila o un parque concurrido, pero con bancos disponibles. Pide una bebida tibia o agua. Siéntate en un rincón. Evita revisar el teléfono. Simplemente observa los movimientos pausados de las personas y el aroma del lugar para desacelerar tu pulso. Estás presente, acompañado, pero en tu espacio.", "que_hacer_en": "Head to a quiet coffee shop or a busy park with available benches. Order a warm drink or water. Sit in a corner. Avoid checking your phone. Simply observe the slow movements of people and the aroma of the place to slow your pulse. You are present, accompanied, but in your space.", "donde": "Cafetería o establecimiento de bebidas local.", "donde_en": "Local coffee shop or beverage venue.", "gps": "quiet cafe or bakery", "vector_necesidades": {"comunidad": 90, "descanso": 85, "silencio": 75, "alimentacion": 60, "contemplacion": 80, "esperanza": 85, "musica": 30, "ansiedad": -30, "soledad": -20, "aislamiento": -15}},
            {"id": 135, "titulo": "Jardín de Rocas Zen Interior", "titulo_en": "Indoor Zen Rock Garden", "porque": "Mente agitada. Buscas orden, armonía y un punto de enfoque para centrar tus pensamientos y disipar la ansiedad. La simplicidad es tu guía.", "porque_en": "Agitated mind. You seek order, harmony, and a focal point to center your thoughts and dissipate anxiety. Simplicity is your guide.", "que_hacer": "Encuentra un jardín de rocas zen (a menudo en centros de bienestar, hoteles o incluso en línea con imágenes). Observa las formas, la disposición. Medita en su calma y en la sensación de orden que transmite. Permite que esa quietud te envuelva.", "que_hacer_en": "Find a zen rock garden (often in wellness centers, hotels, or even online with images). Observe the shapes, the arrangement. Meditate on its calm and the feeling of order it conveys. Let that stillness envelop you.", "donde": "Jardín de rocas o japonés (físico o visualizado).", "donde_en": "Rock or Japanese garden (physical or visualized).", "gps": "zen garden or meditation center", "vector_necesidades": {"movimiento": 10, "naturaleza": 90, "silencio": 100, "agua": 50, "sol": 50, "sombra": 80, "aire_fresco": 90, "creatividad": 70, "contemplacion": 100, "descanso": 95, "organizacion": 100, "esperanza": 90, "ansiedad": -35, "prision_mental": -25}},
        ],
        "cansado": [], # Cansado se fusiona con agotado y estresado en algunas misiones para evitar redundancia
        "aburrido": [], # Aburrido se fusiona con otras categorías
    }
}

# Fusionar misiones para "cansado" y "aburrido" si no tienen catálogo propio, hacia "agotado" o "estresado"
if not BASE_MISIONES["SALIR"]["cansado"]:
    BASE_MISIONES["SALIR"]["cansado"] = BASE_MISIONES["SALIR"]["agotado"] + BASE_MISIONES["SALIR"]["estresado"]
if not BASE_MISIONES["SALIR"]["aburrido"]:
    BASE_MISIONES["SALIR"]["aburrido"] = BASE_MISIONES["SALIR"]["aburrido"] + BASE_MISIONES["SALIR"]["agotado"] + BASE_MISIONES["SALIR"]["estresado"]

def score_coincidencia(perfil_local, vector_necesidades, historial=None, mission_id=None):
    """Calcula un score de coincidencia entre el perfil del usuario y una misión."""
    historial = historial or []
    score = 0
    # Coincidencia principal: Cuanto más cerca esté la necesidad del usuario del objetivo de la misión, mayor el score.
    for necesidad, objetivo in vector_necesidades.items():
        if necesidad in ["prision_mental", "agotamiento_mental", "ansiedad"]: # Estos son indicadores, no necesidades a igualar
            continue
        usuario = perfil_local.get(necesidad, DEFAULT_NECESSITY_VECTOR.get(necesidad, 50))
        diferencia = abs(usuario - objetivo)
        score += (100 - diferencia) * 0.5 # Ponderación base

    # Priorizar necesidades insatisfechas (altas en perfil) que la misión cubre bien.
    for necesidad, valor_usuario in perfil_local.items():
        if necesidad in ["prision_mental", "agotamiento_mental", "ansiedad"]:
            continue
        if valor_usuario > 70 and vector_necesidades.get(necesidad, 0) > 70:
            score += (valor_usuario * 0.3)
        elif valor_usuario > 50 and vector_necesidades.get(necesidad, 0) > 50:
            score += (valor_usuario * 0.1)

    # Priorizar solución de los indicadores negativos
    ansiedad = perfil_local.get("ansiedad", 0)
    agotamiento_mental = perfil_local.get("agotamiento_mental", 0)
    prision_mental = perfil_local.get("prision_mental", 0)

    # Si la misión reduce estos indicadores, bonifica.
    score += (abs(vector_necesidades.get("ansiedad", 0)) * (ansiedad / 100)) * 2 # Bonifica si la misión baja ansiedad y el usuario está ansioso
    score += (abs(vector_necesidades.get("agotamiento_mental", 0)) * (agotamiento_mental / 100)) * 2
    score += (abs(vector_necesidades.get("prision_mental", 0)) * (prision_mental / 100)) * 2

    if mission_id is not None:
        score -= penalizacion_historial(mission_id, historial)
        score += bonus_exploracion(mission_id, historial)
   
    return round(max(0, score), 2)

def seleccionar_por_ranking(candidatos):
    """Selecciona una misión basándose en un ranking ponderado, favoreciendo los scores más altos."""
    if not candidatos:
        return None
   
    candidatos = sorted(candidatos, key=lambda x: x["score"], reverse=True)
   
    if not candidatos:
        return None

    mejor_score = candidatos[0]["score"]
   
    # Si todos tienen un score bajo y similar, elige uno al azar para diversidad
    if mejor_score <= 150: # Umbral para considerar que los scores son "bajos" o muy parecidos
        scores_unicos = {c["score"] for c in candidatos}
        if len(scores_unicos) <= 2: # Si hay 1 o 2 scores únicos, significa que muchos son iguales
            return random.choice(candidatos)

    score_umbral = max(mejor_score * 0.8, mejor_score - 100) # El 80% del mejor o 100 puntos menos
   
    mejores_candidatos_para_eleccion = [
        c for c in candidatos if c["score"] >= score_umbral
    ]
   
    if not mejores_candidatos_para_eleccion:
        mejores_candidatos_para_eleccion = candidatos[:min(5, len(candidatos))] # Toma del top 5 si el umbral fue muy estricto
        if not mejores_candidatos_para_eleccion: return None

    pesos = [c["score"] for c in mejores_candidatos_para_eleccion]
    pesos = [max(1, p) for p in pesos] # Asegura pesos positivos para random.choices

    return random.choices(mejores_candidatos_para_eleccion, weights=pesos, k=1)[0]

def seleccionar_mision_inteligente(misiones, perfil_local, historial=None):
    """Selecciona una única misión inteligente de una lista."""
    historial = historial or []
    candidatos = []
    for mision in misiones:
        mission_vector = mision.get("vector_necesidades", DEFAULT_NECESSITY_VECTOR)
        score = score_coincidencia(perfil_local=perfil_local, vector_necesidades=mission_vector, historial=historial, mission_id=mision["id"])
        candidatos.append({"mision": mision, "score": score})
    seleccion = seleccionar_por_ranking(candidatos)
    if seleccion is None:
        return random.choice(misiones) if misiones else None
    return seleccion["mision"]

def seleccionar_n_misiones_inteligentes(n, misiones, perfil_local, historial_actual=None):
    """Selecciona N misiones inteligentes y diversas para el modo SALIR."""
    historial_actual = historial_actual or []
    candidatos_base = []
    for mision in misiones:
        mission_vector = mision.get("vector_necesidades", DEFAULT_NECESSITY_VECTOR)
        score = score_coincidencia(perfil_local=perfil_local, vector_necesidades=mission_vector, historial=historial_actual, mission_id=mision["id"])
        candidatos_base.append({"mision": mision, "score": score})

    candidatos_base.sort(key=lambda x: x["score"], reverse=True)
   
    seleccionadas = []
    ids_seleccionados = set()
   
    # Prioriza las de mayor score y las que no estén en el historial, y sean diversas
    for cand in candidates_base:
        if len(seleccionadas) >= n:
            break
        if cand["mision"]["id"] not in ids_seleccionados and cand["mision"]["id"] not in historial_actual:
            es_diversa = True
            for sel_mision in seleccionadas:
                distancia = diversidad_vector(
                    cand["mision"].get("vector_necesidades", DEFAULT_NECESSITY_VECTOR),
                    sel_mision.get("vector_necesidades", DEFAULT_NECESSITY_VECTOR)
                )
                if distancia < 120: # Umbral de diversidad para SALIR
                    es_diversa = False
                    break
            if es_diversa:
                seleccionadas.append(cand["mision"])
                ids_seleccionados.add(cand["mision"]["id"])
   
    # Si aún no hay suficientes, toma las siguientes mejores aunque no sean tan diversas, evitando repeticiones
    while len(seleccionadas) < n:
        added_this_round = False
        for cand in candidatos_base:
            if len(seleccionadas) >= n:
                break
            if cand["mision"]["id"] not in ids_seleccionados:
                seleccionadas.append(cand["mision"])
                ids_seleccionados.add(cand["mision"]["id"])
                added_this_round = True
        if not added_this_round and len(seleccionadas) < n: # Si ya no hay nuevas, recicla de las disponibles sin historial (si el historial se "vacía" implícitamente)
            temp_misiones = [m for m in misiones if m["id"] not in ids_seleccionados]
            if not temp_misiones:
                temp_misiones = misiones # Si no hay nada, reusa todo para no quedarse sin opciones
            random.shuffle(temp_misiones)
            for m in temp_misiones:
                if len(seleccionadas) >= n:
                    break
                if m["id"] not in ids_seleccionados:
                    seleccionadas.append(m)
                    ids_seleccionados.add(m["id"])
            if not temp_misiones and len(seleccionadas) < n: # Break if no more missions possible
                break

    return seleccionadas[:n]

def seleccionar_misiones_casa_inteligente(misiones, perfil_local, historial_casa=None, cantidad=3):
    """Selecciona N misiones inteligentes y diversas para el modo CASA."""
    historial_casa = historial_casa or []
   
    disponibles = [m for m in misiones if m["id"] not in historial_casa]
   
    if len(disponibles) < cantidad * 1.5: # Si quedan pocas opciones no repetidas, reinicia el 'pool'
        disponibles = misiones

    candidatos = []
    for mision in disponibles:
        mission_vector = mision.get("vector_necesidades", DEFAULT_NECESSITY_VECTOR)
        score = score_coincidencia(perfil_local=perfil_local, vector_necesidades=mission_vector, historial=historial_casa, mission_id=mision.get("id"))
        candidatos.append({"mision": mision, "score": score})
   
    candidatos.sort(key=lambda x: x["score"], reverse=True)
   
    resultado = []
    ids_en_resultado = set()
   
    # Intenta seleccionar misiones diversas y de alto score
    for candidato in candidatos:
        mision = candidato["mision"]
        if mision["id"] in ids_en_resultado:
            continue
        es_diversa = True
        for anterior_mision in resultado:
            distancia = diversidad_vector(
                mision.get("vector_necesidades", DEFAULT_NECESSITY_VECTOR),
                anterior_mision.get("vector_necesidades", DEFAULT_NECESSITY_VECTOR)
            )
            if distancia < 80: # Umbral de diversidad para CASA
                es_diversa = False
                break
        if es_diversa:
            resultado.append(mision)
            ids_en_resultado.add(mision["id"])
        if len(resultado) >= cantidad:
            break
           
    # Si no se alcanzan las 'cantidad' requeridas con diversidad, añade las siguientes mejores
    while len(resultado) < cantidad and len(candidatos) > len(resultado):
        for candidato in candidatos:
            mision = candidato["mision"]
            if mision["id"] not in ids_en_resultado:
                resultado.append(mision)
                ids_en_resultado.add(mision["id"])
            if len(resultado) >= cantidad:
                break
    
    return resultado[:cantidad]


@app.get("/")
async def index():
    """Sirve la página HTML principal de la aplicación."""
    return FileResponse('static/curse.html')

@app.post("/api/mando-integral")
async def mando_integral(request: Request):
    """
    Endpoint principal para el Mando Integral de Bienestar.
    Recibe la entrada del usuario y el perfil de preferencias local para retornar una recomendación personalizada.
    """
    payload = await request.json()
    opcion_usuario = str(payload.get("modo", "")).strip().upper()
    zip_code = str(payload.get("zip", "")).strip()
    mente = str(payload.get("mente", "aburrido")).lower()
    perfil_tipo = str(payload.get("perfil", "veterano_guerra")).lower() # Nuevo valor por defecto
    desahogo = str(payload.get("desahogo", "")).lower()
    lang = str(payload.get("lang", "es")).lower()
   
    if zip_code and not re.fullmatch(r"^\d{5}$", zip_code):
        return JSONResponse({"error": "Código Postal inválido. Debe ser 5 dígitos numéricos."}, status_code=400)
       
    perfil_local = payload.get("perfil_local", {})
    if not isinstance(perfil_local, dict):
        perfil_local = {}
       
    # Asegura que todas las claves del perfil_local existan y tengan valores por defecto si faltan
    perfil_local = {
        **DEFAULT_NECESSITY_VECTOR,
        **{k: v for k, v in perfil_local.items() if k in DEFAULT_NECESSITY_VECTOR}
    }
    
    # Lógica para la "detección" de condiciones específicas en el desahogo
    # No se combate marcas, sino la raíz de los síntomas que el usuario describe en relación a su vida.
    specific_recovery_mission = False
    specific_trigger = ""

    if "solo" in desahogo or "soledad" in desahogo or "abandonado" in desahogo:
        specific_recovery_mission = True
        specific_trigger = "soledad"
    elif "carga de trabajo" in desahogo or "estres" in desahogo or "agobio" in desahogo:
        specific_recovery_mission = True
        specific_trigger = "carga_trabajo"
    elif "monotonia" in desahogo or "aburrido" in desahogo or "rutina" in desahogo:
        specific_recovery_mission = True
        specific_trigger = "monotonia"
    elif "ansiedad" in desahogo or "preocupado" in desahogo:
        specific_recovery_mission = True
        specific_trigger = "ansiedad"
    elif "cansado" in desahogo or "agotado" in desahogo:
        specific_recovery_mission = True
        specific_trigger = "agotamiento"
    elif "prision mental" in desahogo or "encierro" in desahogo:
        specific_recovery_mission = True
        specific_trigger = "prision_mental"
    elif "responsabilidad" in desahogo:
        specific_recovery_mission = True
        specific_trigger = "responsabilidad"

    # Si se detecta un trigger específico, se genera una "misión de recuperación" forzada en modo SALIR
    if specific_recovery_mission:
        instruccion_es = ""
        instruccion_en = ""
        titulo_es = ""
        titulo_en = ""
        gps_query = ""
        vector_especial = {}

        if specific_trigger == "soledad":
            titulo_es = "Módulo de Conexión Silenciosa"
            titulo_en = "Silent Connection Module"
            instruccion_es = "Estás sintiendo el peso del aislamiento. Dirígete a un parque concurrido o una cafetería. No interactúes, solo observa. Siente la presencia humana sin presión. Reconecta con el fluir de la vida sin sentirte solo. Este es un ancla a la comunidad."
            instruccion_en = "You're feeling the weight of isolation. Go to a busy park or coffee shop. Don't interact, just observe. Feel human presence without pressure. Reconnect with the flow of life without feeling alone. This is an anchor to community."
            gps_query = "quiet coffee shop or busy park"
            vector_especial = {"comunidad": 100, "silencio": 80, "contemplacion": 90, "soledad": -30, "aislamiento": -25}
        elif specific_trigger == "carga_trabajo":
            titulo_es = "Módulo de Descompresión Urgente"
            titulo_en = "Urgent Decompression Module"
            instruccion_es = "La carga te asfixia. Busca un espacio abierto, un mirador o un patio. Cierra los ojos. Inhala profundamente por 5 segundos, retén 5, exhala 5. Repite 3 veces. Visualiza cómo la carga se desprende de tus hombros. La vasta amplitud te espera."
            instruccion_en = "The burden suffocates you. Find an open space, an overlook, or a courtyard. Close your eyes. Inhale deeply for 5 seconds, hold 5, exhale 5. Repeat 3 times. Visualize the load falling from your shoulders. Vast spaciousness awaits you."
            gps_query = "scenic overlook or open park"
            vector_especial = {"descanso": 100, "aire_fresco": 95, "contemplacion": 90, "carga_trabajo": -30, "responsabilidad": -20, "agotamiento_mental": -25}
        elif specific_trigger == "monotonia":
            titulo_es = "Módulo de Estimulación Novedosa"
            titulo_en = "Novel Stimulation Module"
            instruccion_es = "La rutina te aplasta. Busca una calle con arte urbano, un mercado de agricultores o una tienda de antigüedades. Observa cada detalle. Permite que tus sentidos se despierten con lo inesperado. El mundo está lleno de maravillas simples."
            instruccion_en = "Routine crushes you. Find a street with urban art, a farmer's market, or an antique shop. Observe every detail. Allow your senses to awaken with the unexpected. The world is full of simple wonders."
            gps_query = "street art or farmers market"
            vector_especial = {"creatividad": 100, "aprendizaje": 90, "movimiento": 70, "monotonia": -30, "prision_mental": -15}
        elif specific_trigger == "ansiedad":
            titulo_es = "Módulo de Enfoque Profundo"
            titulo_en = "Deep Focus Module"
            instruccion_es = "Tu mente corre sin freno. Dirígete a un jardín de rocas zen (real o en línea si no es posible ir físicamente) o un lago. Observa la quietud. Concentra tu vista en un punto fijo del paisaje. Siente cómo tu respiración se ralentiza. El presente es tu ancla."
            instruccion_en = "Your mind is racing. Go to a Zen rock garden (real or online if not physically possible) or a lake. Observe the stillness. Concentrate your gaze on a fixed point in the landscape. Feel your breathing slow down. The present is your anchor."
            gps_query = "zen garden or public lake"
            vector_especial = {"silencio": 100, "contemplacion": 100, "agua": 90, "naturaleza": 85, "ansiedad": -35, "prision_mental": -25}
        elif specific_trigger == "agotamiento":
            titulo_es = "Módulo de Restauración Vital"
            titulo_en = "Vital Restoration Module"
            instruccion_es = "El agotamiento te consume. Busca un lugar tranquilo y fresco, como la sombra de un gran árbol en un parque o un banco en un jardín botánico. Siéntate, cierra los ojos y escucha los sonidos suaves del entorno. Permite que tu cuerpo se rinda al descanso profundo. La renovación comienza ahora."
            instruccion_en = "Exhaustion consumes you. Find a quiet and cool place, like the shade of a large tree in a park or a bench in a botanical garden. Sit, close your eyes, and listen to the soft sounds of the surroundings. Allow your body to surrender to deep rest. Renewal begins now."
            gps_query = "quiet park with shade or botanical garden"
            vector_especial = {"descanso": 100, "naturaleza": 95, "silencio": 90, "sombra": 90, "aire_fresco": 85, "agotamiento_mental": -30, "prision_mental": -20}
        elif specific_trigger == "prision_mental":
            titulo_es = "Módulo de Expansión de Conciencia"
            titulo_en = "Consciousness Expansion Module"
            instruccion_es = "Te sientes atrapado en tu propia mente. Dirígete a un mirador panorámico o a la costa. Observa la inmensidad del horizonte. Permite que tu mente se expanda más allá de tus límites autoimpuestos. Siente la libertad y la vasta perspectiva."
            instruccion_en = "You feel trapped in your own mind. Head to a panoramic overlook or the coast. Observe the vastness of the horizon. Allow your mind to expand beyond your self-imposed limits. Feel the freedom and vast perspective."
            gps_query = "scenic overlook or coastal view"
            vector_especial = {"contemplacion": 100, "naturaleza": 95, "aire_fresco": 90, "esperanza": 95, "prision_mental": -40, "ansiedad": -20}
        elif specific_trigger == "responsabilidad":
            titulo_es = "Módulo de Aligeramiento de Carga"
            titulo_en = "Load Lightening Module"
            instruccion_es = "La presión de la responsabilidad pesa sobre ti. Ve a un gimnasio comunitario o una cancha deportiva. Enfócate en una actividad física vigorosa por unos minutos. Siente cómo cada movimiento libera la tensión. Tu cuerpo descarga lo que tu mente retiene."
            instruccion_en = "The pressure of responsibility weighs on you. Go to a community gym or sports court. Focus on vigorous physical activity for a few minutes. Feel each movement release tension. Your body unloads what your mind holds."
            gps_query = "community gym or public sports court"
            vector_especial = {"movimiento": 100, "salud": 90, "juego": 70, "responsabilidad": -30, "estres": -25, "agotamiento_mental": -15}

        query_mapa_url = urllib.parse.quote_plus(f"{gps_query} in {zip_code}")
        target_link = f"{GPS_BASE_URL}{query_mapa_url}"

        final_misiones_para_frontend = [{
            "destino_id": 999,
            "destino_titulo": titulo_es,
            "destino_titulo_en": titulo_en,
            "que_hacer": "Intervención de Apoyo Directo",
            "que_hacer_en": "Direct Support Intervention",
            "destino_entorno": "PERÍMETRO DE ACCIÓN DE CAMPO",
            "destino_instruccion": instruccion_es,
            "destino_instruccion_en": instruccion_en,
            "destino_coordenadas_gps": target_link,
            "vector_entorno_seleccionado": {**DEFAULT_NECESSITY_VECTOR, **vector_especial},
        }]

        return JSONResponse({
            "DIRECCIONAMIENTO_MASTER": "ACCION_CAMPO",
            "misiones": final_misiones_para_frontend,
            "historial_salir_actualizado": payload.get("historial_salir", []),
            "forced_recovery": True
        })

    # CONTINUACIÓN DEL FLUJO BASE DE LA PLATAFORMA OPEN THAN GO
    # 1. INTERVENCIÓN DOMÉSTICA (MODO CASA)
    if opcion_usuario == "CASA":
        idioma = "EN" if lang.lower() == "en" else "ES"
        misiones_completas = BASE_MISIONES[f"CASA_{idioma}"]
        historial_casa = payload.get("historial_casa", [])
        misiones_casa = seleccionar_misiones_casa_inteligente(misiones_completas, perfil_local, historial_casa, cantidad=3)
        for m in misiones_casa:
            historial_casa = actualizar_historial(historial_casa, m["id"], MAX_HISTORY_CASA)
        return JSONResponse({
            "DIRECCIONAMIENTO_MASTER": "INTERVENCION_DOMESTICA",
            "misiones": misiones_casa,
            "historial_casa_actualizado": historial_casa
        })
       
    # 2. ACCIÓN DE CAMPO (MODO SALIR - SELECCIÓN PREDICTIVA)
    opciones_salir_candidatas = BASE_MISIONES["SALIR"].get(mente, BASE_MISIONES["SALIR"]["aburrido"])
    historial_salir = payload.get("historial_salir", [])
   
    misiones_seleccionadas_raw = seleccionar_n_misiones_inteligentes(
        n=3,
        misiones=opciones_salir_candidatas,
        perfil_local=perfil_local,
        historial_actual=historial_salir
    )
   
    final_misiones_para_frontend = []
   
    for info_seleccionada in misiones_seleccionadas_raw:
        # Los "presupuestos" se transforman en "enfoques de gasto"
        enfoque_gasto = ""
        if payload.get("budget", "0") == "0":
            enfoque_gasto = "ENFOQUE: Cero Costo. Bienestar accesible." if lang == "es" else "FOCUS: Zero Cost. Accessible Well-being."
        elif payload.get("budget", "0") == "1":
            enfoque_gasto = "ENFOQUE: Gasto Mínimo. Inversión en ti." if lang == "es" else "FOCUS: Minimal Expense. Invest in self."
        elif payload.get("budget", "0") == "2":
            enfoque_gasto = "ENFOQUE: Abierto. Tu bienestar no tiene precio." if lang == "es" else "FOCUS: Open. Your well-being is priceless."

        quienes_van = ""
        if perfil_tipo == "veterano_guerra":
            quienes_van = "AUDIENCIA: Veterano de Guerra. Fortaleza interior." if lang == "es" else "AUDIENCE: War Veteran. Inner strength."
        elif perfil_tipo == "adulto_mayor":
            quienes_van = "AUDIENCIA: Adulto Mayor. Paz y conexión." if lang == "es" else "AUDIENCE: Senior Adult. Peace and connection."
        elif perfil_tipo == "trabajador_gobierno":
            quienes_van = "AUDIENCIA: Trabajador del Gobierno. Equilibrio y respiro." if lang == "es" else "AUDIENCE: Government Worker. Balance and respite."

        titulo_ganador = info_seleccionada.get("titulo_en", info_seleccionada["titulo"]) if lang == "en" else info_seleccionada["titulo"]
        que_hacer_lang = info_seleccionada.get('que_hacer_en', info_seleccionada['que_hacer']) if lang == "en" else info_seleccionada['que_hacer']
        porque_lang = info_seleccionada.get('porque_en', info_seleccionada['porque']) if lang == "en" else info_seleccionada['porque']
        donde_base = info_seleccionada.get("donde_en", info_seleccionada["donde"]) if lang == "en" else info_seleccionada["donde"]
        anclaje_geografico = zip_code
        map_base_url = GPS_BASE_URL

        guia_masticada = (
            f"DESTINO: {titulo_ganador or ''}.\n"
            f"POR QUÉ: {porque_lang or ''}\n"
            f"QUÉ HACER: {que_hacer_lang or ''}\n"
            f"CUÁNDO: {(WHEN_EN if lang == 'en' else WHEN_ES) or ''}\n"
            f"PARA QUÉ: {(FOR_WHAT_EN if lang == 'en' else FOR_WHAT_ES) or ''}\n"
            f"{quienes_van}\n{enfoque_gasto}"
        )

        search_query_parts = []
        if perfil_tipo == "adulto_mayor":
            search_query_parts.append("senior friendly")
        search_query_parts.append(info_seleccionada["gps"])
        search_query_parts.append(f"in {anclaje_geografico}")

        full_map_query_string = " ".join(search_query_parts)
        target_link = f"{map_base_url}{urllib.parse.quote_plus(full_map_query_string)}"

        final_vector_necesidades = {**DEFAULT_NECESSITY_VECTOR, **info_seleccionada.get("vector_necesidades", {})}

        final_misiones_para_frontend.append({
            "destino_id": info_seleccionada.get("id"),
            "destino_titulo": titulo_ganador,
            "destino_titulo_en": info_seleccionada.get("titulo_en", info_seleccionada["titulo"]),
            "que_hacer": info_seleccionada["que_hacer"], # Siempre mantener el original y el de idioma para el front
            "que_hacer_en": info_seleccionada.get("que_hacer_en", info_seleccionada["que_hacer"]),
            "destino_entorno": donde_base,
            "destino_instruccion": guia_masticada.strip(),
            "destino_instruccion_en": guia_masticada.strip(), # Ambos usan el mismo guia_masticada ya formateado
            "destino_coordenadas_gps": target_link,
            "vector_entorno_seleccionado": final_vector_necesidades,
        })

    return JSONResponse({
        "DIRECCIONAMIENTO_MASTER": "ACCION_CAMPO",
        "misiones": final_misiones_para_frontend,
        "historial_salir_actualizado": historial_salir
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
