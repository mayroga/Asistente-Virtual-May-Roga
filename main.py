import os
import random
import re
import urllib.parse
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

DEFAULT_NECESSITY_VECTOR = {
    "movimiento": 50,
    "naturaleza": 50,
    "silencio": 50,
    "agua": 50,
    "sol": 50,
    "sombra": 50,
    "aire_fresco": 50,
    "creatividad": 50,
    "comunidad": 50,
    "aprendizaje": 50,
    "juego": 50,
    "contemplacion": 50,
    "descanso": 50,
    "organizacion": 50,
    "alimentacion": 50,
    "musica": 50,
    "risa": 50,
    "esperanza": 50,
    "indicador_ansiedad": 0
}

# ==========================================================================================
# MANIFIESTOS DEL ORÁCULO SOMÁTICO - ADAPTADO A FOCOS DE CARGA GUBERNAMENTALES
# ==========================================================================================
MANIFIESTOS_ORACULO = {
    "hipervigilancia": [
        "Tu mente, entrenada para la alerta, busca un anclaje. No huyas, redirige. La quietud no es pasividad, es estrategia. Ancla tu atención en el presente, como un oficial en un puesto de observación sereno. Este es tu repliegue táctico. Despliega la calma.",
        "La hipervigilancia es un escudo pesado. Reconócelo. Este momento es una auditoría interna: revisa tu pulso, no amenazas externas. La verdadera seguridad reside en la homeostasis. Permite que tu cuerpo sea tu único punto de control. Misión: auto-regulación.",
        "El servicio exige una atención constante. Ahora, dirige esa precisión hacia tu interior. Cada sonido ambiental, cada sombra en tu visión periférica, es una oportunidad para practicar el desapego. Tu mente merece un permiso de descanso activo. Disfruta tu tregua."
    ],
    "aislamiento": [
        "La soledad institucional puede ser un peso invisible. Esta plataforma es tu puente. Aunque estés solo, eres parte de una comunidad mayor. Busca un eco en el paisaje, un reflejo de tu resiliencia en la naturaleza. Reconecta con el pulso universal. No estás solo.",
        "El distanciamiento, a veces obligatorio, no debe significar desconexión total. Tu espíritu busca comunidad, no una orden. Permítete un momento de contemplación activa; observa el flujo de la vida sin expectativas. Eres un pilar, y los pilares necesitan cimientos firmes. Fortalece tu base.",
        "La mente, aislada, puede tejer narrativas complejas. Desentraña el nudo. Este oráculo te invita a buscar un punto de fuga, una ventana a una perspectiva más amplia. El calor humano puede ser encontrado en el eco de tu propia voz interna, recordándote tu valor. Cultiva tu ecosistema interior."
    ],
    "carga_invisible": [
        "El peso del servicio, de las decisiones cruciales, es una mochila silenciosa. Hoy, suelta esa carga. No es debilidad, es sabiduría logística. Visualiza cada preocupación como una piedra que se disuelve en un río. Eres más que tus responsabilidades. Aligera tu marcha.",
        "La fatiga de decisiones acumuladas requiere una auditoría profunda. Este es tu momento de descompresión. No busques respuestas, busca el espacio para que surjan. La inacción es una herramienta poderosa para recalibrar. Permite que el 'no hacer' sea tu mayor acción estratégica. Reposa tus decisiones.",
        "El servicio público a menudo viene con un costo personal no reconocido. Es hora de recuperar tu capital energético. Cada respiración es una inversión en tu bienestar. No eres una máquina, eres un ser humano esencial. Recarga tus baterías, tu país te necesita entero. Restaura tu equilibrio."
    ],
    "saturacion_urbana": [
        "El ruido burocrático, la prisa de la ciudad, te asfixian. Tu misión es desfragmentar. Busca el silencio en el estruendo, el oasis en el asfalto. Tu mente merece un respiro de la constante 'entrada de datos'. Filtra el caos, encuentra tu frecuencia. Desactiva el ruido.",
        "El estrés de oficina se acumula como polvo. Sacúdelo. Este oráculo te guía hacia entornos que purifican tu percepción. El aire fresco y el espacio abierto son tus aliados. No te resignes a la fatiga urbana; actívate para trascenderla. Escapa al aire libre, sin prisa.",
        "La rutina te encierra, la ciudad te agota. Hoy, busca un punto elevado, una perspectiva que te recuerde la inmensidad más allá de los expedientes. El panorama urbano puede ser deslumbrante, no solo opresivo, si lo observas con intención. Amplía tu visión. Redirige tu enfoque."
    ],
    "agotamiento": [
        "La fatiga estructural acumulada no se resuelve con más esfuerzo. Requiere un repliegue estratégico. Este es tu 'tiempo de inactividad' programado para la recuperación. No te sientas culpable; la recarga es esencial para la misión. Escucha a tu cuerpo. Prioriza tu homeostasis.",
        "Cuando el cuerpo y la mente gritan basta, es una orden, no una sugerencia. La sabiduría ancestral sabía que el descanso no es un lujo, sino una base operativa. Desconecta para reconectar con tu fuente de energía primaria. Tu recuperación es una inversión vital. Restauración profunda.",
        "El agotamiento es el llamado del sistema a una reconfiguración total. Detén la marcha, desactiva los protocolos. Este oráculo te ofrece un santuario temporal para recalibrar tu ser. Eres digno de paz. Permite que la calma te envuelva. Renueva tu contrato con el bienestar."
    ]
}

# ==========================================================================================
# MOTOR DE HISTORIAL INTELIGENTE CWRE V2
# Anti-Repetición + Exploración Controlada
# ==========================================================================================
MAX_HISTORY_SALIR = 5
MAX_HISTORY_CASA = 8
MAX_HISTORY_ORACULO = 12

EXPLORATION_RATE = 0.20
HISTORY_PENALTY_BASE = 40

def limitar_historial(historial, limite):
    if historial is None:
        return []
    return historial[-limite:]

def penalizacion_historial(mision_id, historial):
    if not historial:
        return 0

    historial = list(reversed(historial))

    for posicion, antiguo_id in enumerate(historial):
        if antiguo_id == mision_id:
            if posicion == 0:
                return HISTORY_PENALTY_BASE * 1.5
            elif posicion == 1:
                return HISTORY_PENALTY_BASE
            elif posicion == 2:
                return HISTORY_PENALTY_BASE * 0.70
            elif posicion <= (len(historial) - 1):
                return HISTORY_PENALTY_BASE * 0.30
    return 0

def bonus_exploracion(mision_id, historial):
    if not historial or mision_id not in historial:
        return 20
    limite_reciente = int(MAX_HISTORY_SALIR / 2)
    if mision_id not in limitar_historial(historial, limite_reciente):
        return 5
    return 0

def actualizar_historial(historial, nuevo_id, limite):
    historial = historial or []
    if nuevo_id in historial:
        historial.remove(nuevo_id)
    historial.append(nuevo_id)
    return historial[-limite:]

def diversidad_vector(vec1, vec2):
    score = 0
    all_keys = set(vec1.keys()).union(vec2.keys())
    for key in all_keys:
        val1 = vec1.get(key, 0)
        val2 = vec2.get(key, 0)
        score += abs(val1 - val2)
    return score

TIEMPO_EXTRA_REPOSO_SEGUNDOS = 240
VELOCIDAD_VOZ_HUMANA = 0.95
WHEN_ES = "Tómate tu tiempo. Respira. Levántate sin prisa."
WHEN_EN = "Take your time. Breathe. Move without rushing."
FOR_WHAT_ES = "Romper el piloto automático. Sentirte libre y recordar que estás vivo."
FOR_WHAT_EN = "Break the autopilot. Feel completely free and remember you are alive."

# ==========================================================================================
# BASE DE MISIONES - ADAPTADO A FOCOS DE CARGA GUBERNAMENTALES Y PERFILES ESPECÍFICOS
# ==========================================================================================
link_base = "https://www.google.com/maps/search/?api=1&query="

BASE_MISIONES = {
    "CASA_ES": [
        {"id": 1, "titulo": "Corta el piloto automático", "titulo_en": "Break the autopilot", "descripcion": "Como militar en descanso, escanea tu cuerpo en busca de tensión. Ubica el peso acumulado en tu espalda alta y disuélvelo con cada exhalación. Siente tus latidos firmes y recuerda tu vitalidad, aquí, ahora.", "vector_necesidades": {"contemplacion": 90, "descanso": 80, "silencio": 70, "organizacion": 50, "movimiento": 30}},
        {"id": 2, "titulo": "Desconexión operativa total", "titulo_en": "Total operational disconnection", "descripcion": "Siente la silla como tu base de operación. El suelo sostiene tu peso de forma segura. No luches contra el reposo; permite que la gravedad te ancle en una calma profunda. Estás fuera de servicio, eres libre.", "vector_necesidades": {"descanso": 90, "contemplacion": 80, "silencio": 70, "organizacion": 40, "esperanza": 60}},
        {"id": 3, "titulo": "Despliegue de pantalla", "titulo_en": "Screen deployment", "descripcion": "Coloca tu dispositivo boca abajo, silenciado. Mira un punto fijo en el techo por treinta segundos. Permite que tu mente rompa el ciclo de la alerta digital. Tu campo de visión merece un respiro.", "vector_necesidades": {"silencio": 95, "descanso": 85, "contemplacion": 90, "organizacion": 60, "creatividad": 20}},
        {"id": 4, "titulo": "Aligera la carga logística", "titulo_en": "Lighten the logistical load", "descripcion": "Siente tus hombros libres de condecoraciones invisibles. Visualiza que no cargas con el peso del servicio. Libera la rigidez mental acumulada por decisiones. Respira con la soltura de un civil en casa.", "vector_necesidades": {"descanso": 90, "movimiento": 60, "risa": 40, "esperanza": 80, "organizacion": 30}},
        {"id": 5, "titulo": "El reset del agua vital", "titulo_en": "The vital water reset", "descripcion": "Toma un sorbo pausado de agua fresca. Siente el recorrido del líquido como una corriente vital que renueva tu organismo. Es la purificación que tu sistema necesita. Una tregua hídrica.", "vector_necesidades": {"agua": 100, "descanso": 70, "silencio": 50, "movimiento": 20, "salud": 80}},
        {"id": 6, "titulo": "Ventana de descompresión", "titulo_en": "Decompression window", "descripcion": "Abre la ventana. Deja que el aire fresco irrumpa en tu espacio. Siente cómo se lleva el 'polvo de oficina' y el encierro de la rutina. Es tu conexión con el exterior, tu respiro táctico.", "vector_necesidades": {"aire_fresco": 100, "naturaleza": 80, "contemplacion": 70, "descanso": 60, "movimiento": 30}},
        {"id": 7, "titulo": "Rotación de energía operativa", "titulo_en": "Operational energy rotation", "descripcion": "Gira suavemente muñecas y tobillos. Este cuerpo es tu vehículo más importante. Siente cómo la energía fluye, revitalizando cada articulación, listo para un nuevo despliegue en la vida diaria.", "vector_necesidades": {"movimiento": 95, "descanso": 60, "juego": 40, "salud": 80, "creatividad": 20}},
        {"id": 8, "titulo": "Anclaje al presente (protocolo)", "titulo_en": "Present moment anchoring (protocol)", "descripcion": "Cierra los ojos. Piensa en un logro personal, una pequeña victoria de tu día, o algo que agradeces profundamente. Afírmalo con fuerza. Este es tu anclaje a la realidad inmediata, libre de ruido.", "vector_necesidades": {"contemplacion": 100, "silencio": 90, "esperanza": 95, "aprendizaje": 70, "risa": 30}},
        {"id": 9, "titulo": "Pies en tierra firme", "titulo_en": "Feet on firm ground", "descripcion": "Quítate los zapatos. Apoya las plantas de tus pies directamente en el suelo. Siente la firmeza, la estabilidad. Esta es tu conexión con la base, un recordatorio de tu anclaje al aquí y ahora, a la realidad tangible.", "vector_necesidades": {"naturaleza": 90, "movimiento": 70, "contemplacion": 80, "silencio": 60, "descanso": 70}},
        {"id": 10, "titulo": "Estiramiento hacia el objetivo", "titulo_en": "Stretch towards the objective", "descripcion": "Estira un brazo hacia el cielo, como si buscaras un objetivo lejano. Mantén la tensión un segundo, luego suelta. Es la liberación controlada de la energía. Tu cuerpo es una herramienta precisa.", "vector_necesidades": {"movimiento": 95, "descanso": 60, "salud": 80, "creatividad": 30, "juego": 20}},
    ],
    "CASA_EN": [
        {"id": 1, "titulo": "Break the autopilot", "titulo_en": "Break the autopilot", "descripcion_en": "As a veteran at rest, scan your body for tension. Locate the accumulated weight in your upper back and dissolve it with each exhale. Feel your steady heartbeat and remember your vitality, here, now.", "vector_necesidades": {"contemplacion": 90, "descanso": 80, "silencio": 70, "organizacion": 50, "movimiento": 30}},
        {"id": 2, "titulo": "Total operational disconnection", "titulo_en": "Total operational disconnection", "descripcion_en": "Feel the chair as your base of operations. The ground supports your weight securely. Do not fight repose; allow gravity to anchor you in deep calm. You are off-duty, you are free.", "vector_necesidades": {"descanso": 90, "contemplacion": 80, "silencio": 70, "organizacion": 40, "esperanza": 60}},
        {"id": 3, "titulo": "Screen deployment", "titulo_en": "Screen deployment", "descripcion_en": "Place your device face down, silenced. Stare at a fixed point on the ceiling for thirty seconds. Allow your mind to break the digital alert cycle. Your field of vision deserves a break.", "vector_necesidades": {"silencio": 95, "descanso": 85, "contemplacion": 90, "organizacion": 60, "creatividad": 20}},
        {"id": 4, "titulo": "Lighten the logistical load", "titulo_en": "Lighten the logistical load", "descripcion_en": "Feel your shoulders free of invisible commendations. Visualize that you no longer carry the weight of service. Release the mental rigidity accumulated by decisions. Breathe with the ease of a civilian at home.", "vector_necesidades": {"descanso": 90, "movimiento": 60, "risa": 40, "esperanza": 80, "organizacion": 30}},
        {"id": 5, "titulo": "The vital water reset", "titulo_en": "The vital water reset", "descripcion_en": "Take a slow sip of fresh water. Feel the liquid's journey as a vital current renewing your body. It is the purification your system needs. A hydric truce.", "vector_necesidades": {"agua": 100, "descanso": 70, "silencio": 50, "movimiento": 20, "salud": 80}},
        {"id": 6, "titulo": "Decompression window", "titulo_en": "Decompression window", "descripcion_en": "Open the window. Let the fresh air rush into your space. Feel it carry away the 'office dust' and the confinement of routine. It's your connection to the outside, your tactical breath.", "vector_necesidades": {"aire_fresco": 100, "naturaleza": 80, "contemplacion": 70, "descanso": 60, "movimiento": 30}},
        {"id": 7, "titulo": "Operational energy rotation", "titulo_en": "Operational energy rotation", "descripcion_en": "Gently rotate wrists and ankles. This body is your most important vehicle. Feel energy flow, revitalizing each joint, ready for a new deployment in daily life.", "vector_necesidades": {"movimiento": 95, "descanso": 60, "juego": 40, "salud": 80, "creatividad": 20}},
        {"id": 8, "titulo": "Present moment anchoring (protocol)", "titulo_en": "Present moment anchoring (protocol)", "descripcion_en": "Close your eyes. Think of a personal achievement, a small victory of your day, or something you deeply appreciate. Affirm it strongly. This is your anchor to immediate reality, free from noise.", "vector_necesidades": {"contemplacion": 100, "silencio": 90, "esperanza": 95, "aprendizaje": 70, "risa": 30}},
        {"id": 9, "titulo": "Feet on firm ground", "titulo_en": "Feet on firm ground", "descripcion_en": "Take off your shoes. Place the soles of your feet directly on the floor. Feel the firmness, the stability. This is your connection to the base, a reminder of your anchor to the here and now, to tangible reality.", "vector_necesidades": {"naturaleza": 90, "movimiento": 70, "contemplacion": 80, "silencio": 60, "descanso": 70}},
        {"id": 10, "titulo": "Stretch towards the objective", "titulo_en": "Stretch towards the objective", "descripcion_en": "Stretch an arm towards the sky, as if reaching a distant objective. Hold the tension for a second, then release. It's the controlled release of energy. Your body is a precise tool.", "vector_necesidades": {"movimiento": 95, "descanso": 60, "salud": 80, "creatividad": 30, "juego": 20}},
    ],
    "SALIR": {
        "hipervigilancia": [
            {"id": 101, "titulo": "Repliegue Táctico en Silencio", "titulo_en": "Silent Tactical Retreat", "porque": "Veterano, tu sistema de alerta merece un descanso estratégico. Busca una reserva natural silenciosa. Concéntrate en la quietud profunda, desactiva la 'amenaza' interna y permite que el entorno natural reajuste tu percepción. Siente la tierra firme, un anclaje seguro lejos del combate. Es tu misión de paz: recuperar la soberanía de tu silencio interior. Vive sin apuro.", "porque_en": "Veteran, your alert system deserves a strategic rest. Find a silent nature reserve. Focus on deep stillness, deactivate the internal 'threat', and allow the natural environment to readjust your perception. Feel the firm ground, a secure anchor away from combat. This is your peace mission: reclaim the sovereignty of your inner silence. Live without haste.", "que_hacer": "", "que_hacer_en": "", "cuando": "", "cuando_en": "", "para_que": "", "para_que_en": "", "donde": "Reserva natural silenciosa, parque estatal.", "donde_en": "Silent nature reserve, state park.", "gps": "silent nature reserve for veterans", "enlace_youtube": "https://www.youtube.com/results?search_query=veteran+guided+meditation+nature+sounds", "enlace_spotify": "https://open.spotify.com/search/military+tactical+rest+ambient+sounds", "vector_necesidades": {"naturaleza": 100, "silencio": 100, "contemplacion": 95, "descanso": 90, "aire_fresco": 90, "esperanza": 85}},
            {"id": 102, "titulo": "Auditoría de Paz en Mirador Elevado", "titulo_en": "Peace Audit at Elevated Overlook", "porque": "Trabajador gubernamental, la saturación urbana exige una nueva perspectiva. Dirígete a un mirador elevado. Desde allí, observa la ciudad como un mapa, despersonalizando el caos. Siente el viento en tu rostro, un recordatorio de la inmensidad que te rodea. Es tu auditoría de paz, un momento para alinear tu visión con la calma. Tu mente se desfragmenta con cada vista.", "porque_en": "Government worker, urban saturation demands a new perspective. Head to an elevated overlook. From there, observe the city as a map, depersonalizing the chaos. Feel the wind on your face, a reminder of the vastness surrounding you. This is your peace audit, a moment to align your vision with calm. Your mind defragments with each view.", "que_hacer": "", "que_hacer_en": "", "cuando": "", "cuando_en": "", "para_que": "", "para_que_en": "", "donde": "Mirador urbano, punto panorámico.", "donde_en": "Urban overlook, panoramic point.", "gps": "elevated city viewpoint for government workers", "enlace_youtube": "https://www.youtube.com/results?search_query=urban+desfragmentation+meditation+music", "enlace_spotify": "https://open.spotify.com/search/focus+and+clarity+ambient+soundscapes", "vector_necesidades": {"contemplacion": 100, "aire_fresco": 95, "silencio": 85, "naturaleza": 90, "descanso": 70, "organizacion": 80}},
            {"id": 103, "titulo": "Ruta Botánica de Sabiduría Ancestral", "titulo_en": "Ancestral Wisdom Botanical Route", "porque": "Adulto mayor, el ritmo de vida puede acelerarse. Hoy, ralentiza. Busca una ruta botánica plana y accesible. Permite que la sabiduría de los árboles y el fluir de la naturaleza te guíen a un paso tranquilo. Siente cada paso como un anclaje, una conexión con la paciencia y la resiliencia de la tierra. Es tu misión de sabiduría: honrar tu ritmo natural. Recorre con gracia.", "porque_en": "Senior, life's pace can accelerate. Today, slow down. Find a flat, accessible botanical route. Allow the wisdom of trees and the flow of nature to guide you at a gentle pace. Feel each step as an anchor, a connection to the earth's patience and resilience. This is your wisdom mission: honor your natural rhythm. Walk with grace.", "que_hacer": "", "que_hacer_en": "", "cuando": "", "cuando_en": "", "para_que": "", "para_que_en": "", "donde": "Ruta botánica accesible, jardín público.", "donde_en": "Accessible botanical route, public garden.", "gps": "accessible botanical garden for seniors", "enlace_youtube": "https://www.youtube.com/results?search_query=gentle+nature+walk+senior+meditation", "enlace_spotify": "https://open.spotify.com/search/mindful+walking+for+seniors", "vector_necesidades": {"naturaleza": 100, "movimiento": 70, "contemplacion": 90, "silencio": 80, "descanso": 85, "aprendizaje": 70}},
        ],
        "aislamiento": [
            {"id": 104, "titulo": "Punto de Reunión Silencioso", "titulo_en": "Silent Gathering Point", "porque": "Veterano, el aislamiento no debe ser tu última orden. Dirígete a un parque con áreas tranquilas. Observa a la gente, sin interactuar, reconectando con la energía colectiva. Es un punto de reunión pasivo, una forma de sentir la comunidad sin la presión de la conversación. Siente el pulso de la vida. Tu presencia es valiosa.", "porque_en": "Veteran, isolation should not be your last order. Head to a park with quiet areas. Observe people, without interacting, reconnecting with collective energy. It's a passive gathering point, a way to feel community without conversational pressure. Feel life's pulse. Your presence is valuable.", "que_hacer": "", "que_hacer_en": "", "cuando": "", "cuando_en": "", "para_que": "", "para_que_en": "", "donde": "Parque tranquilo con zonas de asiento.", "donde_en": "Quiet park with seating areas.", "gps": "quiet public park for veterans", "enlace_youtube": "https://www.youtube.com/results?search_query=social+reconnection+guided+meditation", "enlace_spotify": "https://open.spotify.com/search/calm+community+ambient+music", "vector_necesidades": {"comunidad": 90, "silencio": 80, "contemplacion": 85, "naturaleza": 70, "descanso": 60, "esperanza": 75}},
            {"id": 105, "titulo": "Biblioteca de Vínculos Silenciosos", "titulo_en": "Library of Silent Connections", "porque": "Adulto mayor, la soledad es un desafío. Visita una biblioteca pública. Elige un libro que te recuerde un momento feliz. El silencio compartido con otros lectores es una conexión sutil, sin palabras. Siente la sabiduría acumulada en los estantes. Eres parte de una historia más grande. Abraza esta conexión tácita.", "porque_en": "Senior, loneliness is a challenge. Visit a public library. Choose a book that reminds you of a happy moment. The silence shared with other readers is a subtle, wordless connection. Feel the wisdom accumulated on the shelves. You are part of a larger story. Embrace this tacit connection.", "que_hacer": "", "que_hacer_en": "", "cuando": "", "cuando_en": "", "para_que": "", "para_que_en": "", "donde": "Biblioteca pública, sala de lectura.", "donde_en": "Public library, reading room.", "gps": "public library for seniors", "enlace_youtube": "https://www.youtube.com/results?search_query=mindful+reading+music+for+seniors", "enlace_spotify": "https://open.spotify.com/search/gentle+classical+music+for+reflection", "vector_necesidades": {"aprendizaje": 90, "silencio": 100, "contemplacion": 95, "descanso": 85, "comunidad": 60, "esperanza": 70}},
            {"id": 106, "titulo": "Flujo de Gestión Común", "titulo_en": "Common Management Flow", "porque": "Trabajador gubernamental, el distanciamiento institucional puede ser desgastante. Visita una plaza céntrica o un centro de transporte. Observa el flujo de personas, la coreografía anónima de la vida urbana. Eres parte de este sistema. Reconoce la interconexión. El ruido del mundo es también su pulso. Reafirma tu rol, sin la presión directa del cargo.", "porque_en": "Government worker, institutional distancing can be draining. Visit a central plaza or transit hub. Observe the flow of people, the anonymous choreography of urban life. You are part of this system. Recognize the interconnection. The world's noise is also its pulse. Reaffirm your role, without the direct pressure of office.", "que_hacer": "", "que_hacer_en": "", "cuando": "", "cuando_en": "", "para_que": "", "para_que_en": "", "donde": "Plaza pública céntrica, estación de tren/autobús.", "donde_en": "Central public plaza, train/bus station.", "gps": "public plaza or transit hub for government workers", "enlace_youtube": "https://www.youtube.com/results?search_query=observational+meditation+urban+flow", "enlace_spotify": "https://open.spotify.com/search/city+ambient+soundscape+for+focus", "vector_necesidades": {"comunidad": 80, "contemplacion": 90, "movimiento": 50, "silencio": 30, "aire_fresco": 70, "organizacion": 60}},
        ],
        "carga_invisible": [
            {"id": 107, "titulo": "Despliegue de Recarga en la Naturaleza", "titulo_en": "Nature Recharge Deployment", "porque": "Veterano, el peso del servicio es real. Busca un parque con árboles frondosos y zonas de sombra. Deja que la naturaleza absorba la carga invisible. Recuéstate, siente la tierra bajo tu cuerpo. Es un campo de recarga natural, diseñado para tu bienestar. Tu cuerpo y mente tienen derecho a la desmovilización temporal. Desconecta, recarga y vuelve más fuerte.", "porque_en": "Veteran, the weight of service is real. Find a park with leafy trees and shaded areas. Let nature absorb the invisible burden. Lie down, feel the earth beneath your body. It's a natural recharge zone, designed for your well-being. Your body and mind have the right to temporary demobilization. Disconnect, recharge, and return stronger.", "que_hacer": "", "que_hacer_en": "", "cuando": "", "cuando_en": "", "para_que": "", "para_que_en": "", "donde": "Parque con árboles frondosos, área de descanso natural.", "donde_en": "Park with leafy trees, natural rest area.", "gps": "shaded park for veterans mental break", "enlace_youtube": "https://www.youtube.com/results?search_query=veteran+stress+relief+nature+sounds", "enlace_spotify": "https://open.spotify.com/search/military+stress+reduction+ambient", "vector_necesidades": {"naturaleza": 100, "descanso": 95, "silencio": 80, "sombra": 90, "aire_fresco": 90, "contemplacion": 85}},
            {"id": 108, "titulo": "Pausa de Sabiduría y Contemplación", "titulo_en": "Wisdom and Contemplation Pause", "porque": "Adulto mayor, la fatiga de decisiones es un eco. Visita un jardín botánico o un museo tranquilo. Contempla la belleza, la historia, la permanencia de la naturaleza o el arte. Desconecta del 'tener que decidir' y simplemente 'sé'. Tu sabiduría te ha traído hasta aquí. Permítete nutrir tu espíritu sin obligación. Es tu momento de gracia. Encuentra la paz.", "porque_en": "Senior, decision fatigue is an echo. Visit a botanical garden or a quiet museum. Contemplate beauty, history, the permanence of nature or art. Disconnect from 'having to decide' and simply 'be'. Your wisdom has brought you here. Allow yourself to nourish your spirit without obligation. It's your moment of grace. Find peace.", "que_hacer": "", "que_hacer_en": "", "cuando": "", "cuando_en": "", "para_que": "", "para_que_en": "", "donde": "Jardín botánico, museo tranquilo.", "donde_en": "Botanical garden, quiet museum.", "gps": "quiet botanical garden or museum for seniors", "enlace_youtube": "https://www.youtube.com/results?search_query=senior+mindfulness+guided+meditation+art", "enlace_spotify": "https://open.spotify.com/search/classical+music+for+contemplation", "vector_necesidades": {"aprendizaje": 90, "contemplacion": 100, "silencio": 90, "descanso": 85, "naturaleza": 80, "creatividad": 70}},
            {"id": 109, "titulo": "Descompresión Burocrática Activa", "titulo_en": "Active Bureaucratic Decompression", "porque": "Trabajador gubernamental, el peso de la gestión se acumula. Busca una pista de atletismo o un sendero de parque. Camina a paso firme, convierte la carga mental en energía física. Cada paso es una descompresión, liberando la fatiga de tus decisiones. Siente cómo tu cuerpo recupera el control, lejos de los despachos. Es tu protocolo de liberación. Actívate y restaura.", "porque_en": "Government worker, the weight of management accumulates. Find a running track or park trail. Walk at a steady pace, converting mental burden into physical energy. Each step is a decompression, releasing decision fatigue. Feel your body regain control, away from offices. This is your release protocol. Activate and restore.", "que_hacer": "", "que_hacer_en": "", "cuando": "", "cuando_en": "", "para_que": "", "para_que_en": "", "donde": "Pista de atletismo, sendero de parque.", "donde_en": "Running track, park trail.", "gps": "public running track for government workers", "enlace_youtube": "https://www.youtube.com/results?search_query=stress+release+walking+meditation", "enlace_spotify": "https://open.spotify.com/search/motivation+for+government+employees", "vector_necesidades": {"movimiento": 100, "aire_fresco": 90, "salud": 85, "descanso": 60, "organizacion": 70, "esperanza": 75}},
        ],
        "saturacion_urbana": [
            {"id": 110, "titulo": "Oasis de Silencio Urbano", "titulo_en": "Urban Silence Oasis", "porque": "Veterano, el ruido urbano puede reavivar la alerta. Busca un jardín zen o un rincón tranquilo en un parque botánico. Concéntrate en el diseño, las formas. Es un oasis en la ciudad, un santuario de silencio que te permite modular tu percepción. Deja que la armonía visual te ancle. Tu mente merece esta tregua sensorial. Recupera tu centro.", "porque_en": "Veteran, urban noise can reawaken alert. Find a Zen garden or quiet corner in a botanical park. Focus on the design, the shapes. It's an oasis in the city, a sanctuary of silence that allows you to modulate your perception. Let visual harmony anchor you. Your mind deserves this sensory truce. Recover your center.", "que_hacer": "", "que_hacer_en": "", "cuando": "", "cuando_en": "", "para_que": "", "para_que_en": "", "donde": "Jardín zen, rincón tranquilo en botánico.", "donde_en": "Zen garden, quiet corner in botanical park.", "gps": "zen garden or quiet botanical park for veterans", "enlace_youtube": "https://www.youtube.com/results?search_query=veteran+mindfulness+zen+sounds", "enlace_spotify": "https://open.spotify.com/search/calm+zen+ambient+for+focus", "vector_necesidades": {"silencio": 100, "naturaleza": 90, "contemplacion": 95, "descanso": 90, "organizacion": 80, "esperanza": 85}},
            {"id": 111, "titulo": "Desconexión de Rutina en el Agua", "titulo_en": "Routine Disconnection in Water", "porque": "Adulto mayor, el estrés del entorno puede agotar tu energía. Dirígete a una fuente pública o un lago tranquilo. Observa el flujo del agua, su constancia, su calma. Permite que el movimiento del líquido te recuerde la fluidez de la vida. Es una desintoxicación visual y auditiva. Tu ritmo se sincroniza con el agua. Encuentra tu propio caudal.", "porque_en": "Senior, environmental stress can drain your energy. Head to a public fountain or a quiet lake. Observe the water's flow, its constancy, its calm. Let the liquid's movement remind you of life's fluidity. It's a visual and auditory detox. Your rhythm synchronizes with the water. Find your own flow.", "que_hacer": "", "que_hacer_en": "", "cuando": "", "cuando_en": "", "para_que": "", "para_que_en": "", "donde": "Fuente pública, lago tranquilo.", "donde_en": "Public fountain, quiet lake.", "gps": "public fountain or quiet lake for seniors", "enlace_youtube": "https://www.youtube.com/results?search_query=senior+water+meditation+sounds", "enlace_spotify": "https://open.spotify.com/search/relaxing+water+sounds+for+seniors", "vector_necesidades": {"agua": 100, "contemplacion": 90, "silencio": 75, "naturaleza": 80, "descanso": 85, "aire_fresco": 70}},
            {"id": 112, "titulo": "Reconfiguración de Estímulos Urbanos", "titulo_en": "Urban Stimuli Reconfiguration", "porque": "Trabajador gubernamental, el ruido urbano constante te satura. Visita una galería de arte moderna o un centro cultural. Enfócate en una obra abstracta, en sus colores y formas, sin buscar un significado lineal. Es una reconfiguración sensorial, una oportunidad para que tu mente procese la información de manera diferente. Tu creatividad se activa. Reinicia tu percepción. Un respiro visual y mental.", "porque_en": "Government worker, constant urban noise saturates you. Visit a modern art gallery or cultural center. Focus on an abstract work, its colors and shapes, without seeking linear meaning. It's a sensory reconfiguration, an opportunity for your mind to process information differently. Your creativity activates. Reset your perception. A visual and mental breath.", "que_hacer": "", "que_hacer_en": "", "cuando": "", "cuando_en": "", "para_que": "", "para_que_en": "", "donde": "Galería de arte, centro cultural.", "donde_en": "Art gallery, cultural center.", "gps": "modern art gallery or cultural center for government workers", "enlace_youtube": "https://www.youtube.com/results?search_query=abstract+art+meditation+music", "enlace_spotify": "https://open.spotify.com/search/creative+focus+ambient+music", "vector_necesidades": {"creatividad": 100, "contemplacion": 95, "aprendizaje": 80, "silencio": 70, "descanso": 60, "organizacion": 50}},
        ],
        "agotamiento": [
            {"id": 113, "titulo": "Reposición de Energía en el Bosque", "titulo_en": "Forest Energy Replenishment", "porque": "Veterano, la fatiga acumulada es tu enemigo silencioso. Adéntrate en un bosque, una zona de árboles densos. Siente la energía ancestral de la tierra, la sombra protectora. Es tu base de reposición. Desactiva la alerta, permite que tu sistema se reinicie con la calma natural. Tu resistencia se reconstruye aquí. Reconecta con tu fuerza primaria. Misión: restauración total.", "porque_en": "Veteran, accumulated fatigue is your silent enemy. Enter a forest, a dense tree area. Feel the ancestral energy of the earth, the protective shade. This is your replenishment base. Deactivate the alert, allow your system to reset with natural calm. Your resilience is rebuilt here. Reconnect with your primary strength. Mission: total restoration.", "que_hacer": "", "que_hacer_en": "", "cuando": "", "cuando_en": "", "para_que": "", "para_que_en": "", "donde": "Bosque denso, zona de árboles maduros.", "donde_en": "Dense forest, mature tree area.", "gps": "ancient forest for veteran rest", "enlace_youtube": "https://www.youtube.com/results?search_query=forest+therapy+veteran+healing", "enlace_spotify": "https://open.spotify.com/search/deep+forest+healing+sounds", "vector_necesidades": {"naturaleza": 100, "silencio": 90, "sombra": 95, "descanso": 100, "aire_fresco": 95, "contemplacion": 85}},
            {"id": 114, "titulo": "Reasentamiento de la Paz", "titulo_en": "Peace Resettlement", "porque": "Adulto mayor, el agotamiento es un llamado a la pausa. Busca un banco tranquilo en un jardín público con vistas al cielo. Siéntate, apoya tu espalda. Deja que el cielo abierto te recuerde la vasta calma del universo. Es un reasentamiento de tu paz interior, una oportunidad para soltar cualquier peso. Tu tiempo es tuyo. Honra este descanso. Siente la ligereza.", "porque_en": "Senior, exhaustion is a call to pause. Find a quiet bench in a public garden with sky views. Sit, rest your back. Let the open sky remind you of the vast calm of the universe. It's a resettlement of your inner peace, an opportunity to let go of any weight. Your time is yours. Honor this rest. Feel the lightness.", "que_hacer": "", "que_hacer_en": "", "cuando": "", "cuando_en": "", "para_que": "", "para_que_en": "", "donde": "Jardín público con bancos, vistas al cielo.", "donde_en": "Public garden with benches, sky views.", "gps": "public garden with sky view for seniors", "enlace_youtube": "https://www.youtube.com/results?search_query=senior+sky+gazing+meditation", "enlace_spotify": "https://open.spotify.com/search/peaceful+sky+ambient+music", "vector_necesidades": {"contemplacion": 100, "descanso": 95, "silencio": 80, "aire_fresco": 85, "naturaleza": 70, "esperanza": 90}},
            {"id": 115, "titulo": "Cese de Operaciones Temporales", "titulo_en": "Temporary Cease of Operations", "porque": "Trabajador gubernamental, la fatiga estructural pide un cese de operaciones. Dirígete a un parque con una cancha vacía o un espacio amplio. No para actividad intensa, sino para sentir la amplitud, la ausencia de tareas. Camina despacio, sin un propósito fijo. Es tu permiso para simplemente 'estar'. Tu mente necesita desocuparse, no llenarse más. Reinicia tu sistema. Disfruta la inactividad.", "porque_en": "Government worker, structural fatigue calls for a cease of operations. Head to a park with an empty court or a wide open space. Not for intense activity, but to feel the expanse, the absence of tasks. Walk slowly, without a fixed purpose. This is your permit to simply 'be'. Your mind needs to clear, not be filled further. Reset your system. Enjoy inactivity.", "que_hacer": "", "que_hacer_en": "", "cuando": "", "cuando_en": "", "para_que": "", "para_que_en": "", "donde": "Cancha vacía en parque, espacio abierto.", "donde_en": "Empty court in park, open space.", "gps": "open park space for government workers rest", "enlace_youtube": "https://www.youtube.com/results?search_query=empty+space+meditation+for+stress", "enlace_spotify": "https://open.spotify.com/search/quiet+mind+focus+music", "vector_necesidades": {"movimiento": 60, "descanso": 90, "silencio": 85, "aire_fresco": 90, "contemplacion": 75, "organizacion": 80}},
        ]
    }
}

BIG_TECH_RESOURCES = {
    "youtube_base_url": "https://www.youtube.com/results?search_query=",
    "spotify_base_search_url": "https://open.spotify.com/search/",

    "youtube_default_search_es": "sonidos naturaleza relajantes",
    "youtube_default_search_en": "nature sounds relaxing",
    "spotify_default_genre_link_es": "relax-stress-relief", # Will be used as search term for Spotify for more generic results
    "spotify_default_genre_link_en": "relax-stress-relief", # Will be used as search term for Spotify for more generic results

    "youtube_audio_es": "sonidos relajantes para desconectar",
    "youtube_audio_en": "calming sounds to disconnect",
    "spotify_audio_es": "musica relajante para la ansiedad",
    "spotify_audio_en": "calming music for anxiety",
}

# === CONSTANTES DE RESCATE EMOCIONAL Y ANTÍDOTOS DIGITALES UNIFICADOS ===
ANTIDOTOS_DIGITALES_SEARCH_TERMS = {
    "hipervigilancia": "meditacion anclaje veteran", # Alerta táctica/burocrática
    "aislamiento": "musica instrumental reconexion social", # Soledad/distanciamiento institucional
    "carga_invisible": "descarga mental fatiga decisiones", # Peso del servicio/fatiga de decisiones
    "saturacion_urbana": "silencio urbano desfragmentacion mental", # Estrés de oficina/ruido urbano
    "agotamiento": "recarga energia ancestral relax", # Fatiga estructural acumulada
}

# ==========================================================================================
# CWRE V2
# SCORE INTELIGENTE (REFINADO)
# ==========================================================================================
def score_coincidencia(perfil_local, vector_necesidades, historial=None, mission_id=None):
    historial = historial or []
    score = 0

    for necesidad, objetivo in vector_necesidades.items():
        if necesidad == "indicador_ansiedad":
            continue
        usuario = perfil_local.get(necesidad, DEFAULT_NECESSITY_VECTOR.get(necesidad, 50))
        diferencia = abs(usuario - objetivo)
        score += (100 - diferencia) * 0.5

    for necesidad, valor_usuario in perfil_local.items():
        if necesidad == "indicador_ansiedad":
            continue

        obj_mision = vector_necesidades.get(necesidad, 0)
        if valor_usuario > 70 and obj_mision > 70:
            score += (valor_usuario * 0.3)
        elif valor_usuario > 50 and obj_mision > 50:
            score += (valor_usuario * 0.1)

    ansiedad = perfil_local.get("indicador_ansiedad", 0)

    if ansiedad >= 70:
        score += vector_necesidades.get("silencio", 0) * 0.5
        score += vector_necesidades.get("descanso", 0) * 0.5
        score += vector_necesidades.get("esperanza", 0) * 0.4
        score += vector_necesidades.get("naturaleza", 0) * 0.3
        score += vector_necesidades.get("agua", 0) * 0.3
    elif ansiedad >= 40:
        score += vector_necesidades.get("descanso", 0) * 0.2
        score += vector_necesidades.get("silencio", 0) * 0.2

    if mission_id is not None:
        score -= penalizacion_historial(mission_id, historial)
        score += bonus_exploracion(mission_id, historial)

    return round(max(0, score), 2)

def seleccionar_por_ranking(candidatos):
    if not candidatos:
        return None

    candidatos = sorted(candidatos, key=lambda x: x["score"], reverse=True)
    if not candidatos:
        return None

    mejor_score = candidatos[0]["score"]

    if mejor_score <= 100:
        scores_unicos = {c["score"] for c in candidatos}
        if len(scores_unicos) == 1:
            return random.choice(candidatos)

    score_umbral = max(mejor_score * 0.8, mejor_score - 150)
    mejores_candidatos_para_eleccion = [
        c for c in candidatos if c["score"] >= score_umbral
    ]

    if not mejores_candidatos_para_eleccion:
        mejores_candidatos_para_eleccion = candidatos[:min(3, len(candidatos))]

    if not mejores_candidatos_para_eleccion:
        return None

    pesos = [c["score"] for c in mejores_candidatos_para_eleccion]
    pesos = [max(1, p) for p in pesos]

    return random.choices(mejores_candidatos_para_eleccion, weights=pesos, k=1)[0]

def seleccionar_mision_inteligente(misiones, perfil_local, historial=None):
    historial = historial or []
    candidatos = []

    for mision in misiones:
        mission_vector = mision.get("vector_necesidades", DEFAULT_NECESSITY_VECTOR)
        score = score_coincidencia(
            perfil_local=perfil_local,
            vector_necesidades=mission_vector,
            historial=historial,
            mission_id=mision["id"]
        )
        candidatos.append({
            "mision": mision,
            "score": score
        })

    seleccion = seleccionar_por_ranking(candidatos)
    if seleccion == None:
        return random.choice(misiones) if misiones else None

    return seleccion["mision"]

def seleccionar_n_misiones_inteligentes(n, misiones, perfil_local, historial_actual=None):
    historial_actual = historial_actual or []
    candidatos_base = []

    for mision in misiones:
        mission_vector = mision.get("vector_necesidades", DEFAULT_NECESSITY_VECTOR)
        score = score_coincidencia(
            perfil_local=perfil_local,
            vector_necesidades=mission_vector,
            historial=historial_actual,
            mission_id=mision["id"]
        )
        candidatos_base.append({
            "mision": mision,
            "score": score
        })

    candidatos_base.sort(key=lambda x: x["score"], reverse=True)
    seleccionadas = []
    ids_seleccionados = set()

    for cand in candidatos_base:
        if len(seleccionadas) >= n:
            break

        mision_id = cand["mision"]["id"]
        if mision_id not in ids_seleccionados and mision_id not in historial_actual:
            es_diversa = True

            for sel_mision in seleccionadas:
                distancia = diversidad_vector(
                    cand["mision"].get("vector_necesidades", DEFAULT_NECESSITY_VECTOR),
                    sel_mision.get("vector_necesidades", DEFAULT_NECESSITY_VECTOR)
                )
                if distancia < 100:
                    es_diversa = False
                    break

            if es_diversa:
                seleccionadas.append(cand["mision"])
                ids_seleccionados.add(mision_id)

    if len(seleccionadas) < n:
        for cand in candidatos_base:
            if len(seleccionadas) >= n:
                break

            mision_id = cand["mision"]["id"]
            # MECHANICAL FIX: 'm' is undefined, should be 'cand["mision"]'
            if mision_id not in ids_seleccionados and cand["mision"] not in temp_misiones_a_añadir:
                temp_misiones_a_añadir.append(cand["mision"])
                if len(temp_misiones_a_añadir) >= (n - len(seleccionadas)):
                    break
       
        if len(temp_misiones_a_añadir) < (n - len(seleccionadas)):
            random_misions_pool = [m for m in misiones if m["id"] not in ids_seleccionados and m not in temp_misiones_a_añadir]
            random.shuffle(random_misions_pool)
            temp_misiones_a_añadir.extend(random_misions_pool[:(n - len(seleccionadas) - len(temp_misiones_a_añadir))])
       
        seleccionadas.extend(temp_misiones_a_añadir)
        for m in temp_misiones_a_añadir:
            ids_seleccionados.add(m["id"])

    return seleccionadas[:n]

def filtrar_historial(misiones, historial):
    historial = historial or []
    disponibles = [m for m in misiones if m["id"] not in historial]
    return disponibles

def seleccionar_misiones_casa_inteligente(misiones, perfil_local, historial_casa=None, cantidad=3):
    historial_casa = historial_casa or []
    disponibles = filtrar_historial(misiones, historial_casa)
   
    if len(disponibles) < cantidad * 2 and len(misiones) > 0:
        disponibles = misiones

    candidatos = []
    for mision in disponibles:
        mission_vector = mision.get("vector_necesidades", DEFAULT_NECESSITY_VECTOR)
        score = score_coincidencia(
            perfil_local=perfil_local,
            vector_necesidades=mission_vector,
            historial=historial_casa,
            mission_id=mision.get("id")
        )
        candidatos.append({
            "mision": mision,
            "score": score
        })

    candidatos.sort(key=lambda x: x["score"], reverse=True)
    resultado = []
    ids_en_resultado = set()

    for candidato in candidatos:
        mision_actual = candidato["mision"]
        mision_id = mision_actual["id"]
       
        if mision_id in ids_en_resultado:
            continue

        es_diversa = True
        for anterior_mision in resultado:
            distancia = diversidad_vector(
                mision_actual.get("vector_necesidades", DEFAULT_NECESSITY_VECTOR),
                anterior_mision.get("vector_necesidades", DEFAULT_NECESSITY_VECTOR)
            )
            if distancia < 60:
                es_diversa = False
                break

        if es_diversa:
            resultado.append(mision_actual)
            ids_en_resultado.add(mision_id)

        if len(resultado) >= cantidad:
            break

    if len(resultado) < cantidad:
        for candidato in candidatos:
            mision_actual = candidato["mision"]
            if mision_actual["id"] not in ids_en_resultado:
                resultado.append(mision_actual)
                ids_en_resultado.add(mision_actual["id"])
            if len(resultado) >= cantidad:
                break
   
    while len(resultado) < cantidad and len(misiones) > len(ids_en_resultado):
        mision_aleatoria = random.choice(misiones)
        if mision_aleatoria["id"] not in ids_en_resultado:
            resultado.append(mision_aleatoria)
            ids_en_resultado.add(mision_aleatoria["id"])

    return resultado[:cantidad]


@app.get("/")
async def index():
    return FileResponse('static/session.html')

@app.post("/api/mando-integral")
async def mando_integral(request: Request):
    payload = await request.json()
    opcion_usuario = str(payload.get("modo", "")).strip().upper()
    zip_code = str(payload.get("zip", "")).strip()
    mente = str(payload.get("mente", "agotamiento")).lower() # Default to one of the new mind states
    budget = str(payload.get("budget", "0"))
    perfil_tipo = str(payload.get("perfil", "veterano")).lower() # Default to one of the new profiles
    desahogo = str(payload.get("desahogo", "")).lower()
    lang = str(payload.get("lang", "es")).lower()
   
    if zip_code and not re.fullmatch(r"^\d{5}$", zip_code):
        return JSONResponse(
            status_code=400,
            content={"error": "Código Postal inválido. Debe ser 5 dígitos numéricos."}
        )

    perfil_local = payload.get("perfil_local", {})
    if not isinstance(perfil_local, dict):
        perfil_local = {}

    perfil_local = {
        **DEFAULT_NECESSITY_VECTOR,
        **{k: v for k, v in perfil_local.items() if k in DEFAULT_NECESSITY_VECTOR or k == "indicador_ansiedad"}
    }

    if "indicador_ansiedad" not in perfil_local:
        perfil_local["indicador_ansiedad"] = 0

    ADVERTENCIA_LEGAL_ES = (
        "AVISO DE SEGURIDAD: Está prohibido usar esta plataforma mientras manejas. Tu seguridad es lo primero. "
        "El uso es bajo tu propio riesgo y exime de toda responsabilidad al sistema y sus operadores."
    )
    ADVERTENCIA_LEGAL_EN = (
        "SAFETY NOTICE: Using this platform while driving is strictly prohibited. Your safety comes first. "
        "Use is at your own risk and exempts the system and its operators from all liability."
    )

    marca_detectada = None # Will be repurposed for conceptual "stressor detected"
    instruccion_fisiologica_es = "Detente, respira libre."
    instruccion_fisiologica_en = "Stop, breathe free."
    diagnostico_sintoma_es = "Fatiga de servicio acumulada."
    diagnostico_sintoma_en = "Accumulated service fatigue."
    enlace_yt = ""
    enlace_sp = ""
   
    force_recovery_mission = False
    
    # Adapt detection logic for government context (e.g., detecting keywords related to administrative burden)
    keywords_government_stress = ["burocracia", "informes", "turnos", "guardia", "tension", "estres", "normas", "presion", "administrativo", "protocolo", "rutina"]
    if desahogo and any(keyword in desahogo for keyword in keywords_government_stress):
        force_recovery_mission = True
        marca_detectada = "Carga_Administrativa" # Conceptual "brand" for internal processing

    if force_recovery_mission:
        mente_str_es = mente.upper()
        mente_str_en = mente.upper()
        diagnostico_sintoma_es = f"Diagnóstico: El cliente experimenta [{mente_str_es}] en relación al estímulo de [{marca_detectada}] en Zip Code {zip_code}."
        diagnostico_sintoma_en = f"Diagnostic: Client experiences [{mente_str_en}] linked to stimulus [{marca_detectada}] in Zip Code {zip_code}."

        if perfil_tipo == "veterano":
            instruccion_fisiologica_es = "Veterano, tu misión actual es el autocuidado. Despliega un reposo activo. Busca una posición cómoda. Cierra los ojos. 60 segundos de silencio. Eres tu prioridad."
            instruccion_fisiologica_en = "Veteran, your current mission is self-care. Deploy active rest. Find a comfortable position. Close your eyes. 60 seconds of silence. You are your priority."
        elif perfil_tipo == "adulto_mayor":
            instruccion_fisiologica_es = "Adulto mayor, la sabiduría es tu guía. Toma asiento. Apoya tus manos sobre tus rodillas. Siente tu respiración. 60 segundos de calma. Tu paz es tu legado."
            instruccion_fisiologica_en = "Senior, wisdom is your guide. Take a seat. Rest your hands on your knees. Feel your breath. 60 seconds of calm. Your peace is your legacy."
        elif perfil_tipo == "gubernamental":
            instruccion_fisiologica_es = "Trabajador gubernamental, es un repliegue táctico. Desconéctate del flujo de información. Respira profundamente. El sistema te da una pausa. 60 segundos. Restablece tu protocolo interno."
            instruccion_fisiologica_en = "Government worker, this is a tactical retreat. Disconnect from the information flow. Breathe deeply. The system grants you a pause. 60 seconds. Reset your internal protocol."
        else: # Default for any other unhandled profile
            instruccion_fisiologica_es = "Tu mente necesita un desahogo. Usa el aire libre, una ventana. Haz una pausa biológica profunda de 60 segundos. Recupera el control."
            instruccion_fisiologica_en = "Your mind needs release. Use open air, a window. Take a deep 60-sec biological pause. Regain control."


        search_term_antidoto = ANTIDOTOS_DIGITALES_SEARCH_TERMS.get(mente, BIG_TECH_RESOURCES[f'youtube_default_search_{lang}'])
        enlace_yt = f"{BIG_TECH_RESOURCES['youtube_base_url']}{urllib.parse.quote_plus(search_term_antidoto)}"
        enlace_sp = f"{BIG_TECH_RESOURCES['spotify_base_search_url']}{urllib.parse.quote_plus(search_term_antidoto)}"

        matriz_intencional_vibrante = {
            "hipervigilancia": {
                "maps": [
                    "silent nature reserves for veterans",
                    "accessible botanical routes",
                    "elevated urban viewpoints"
                ],
                "youtube": "calm guided meditation for veterans",
                "spotify": "ambient sounds for tactical rest"
            },
            "aislamiento": {
                "maps": [
                    "quiet public parks for seniors",
                    "community libraries quiet zones",
                    "central plazas observational points"
                ],
                "youtube": "reconnection mindfulness video",
                "spotify": "gentle classical music for reflection"
            },
            "carga_invisible": {
                "maps": [
                    "shaded park areas for rest",
                    "botanical gardens or quiet museums",
                    "running tracks or park trails"
                ],
                "youtube": "mindfulness for decision fatigue",
                "spotify": "stress reduction ambient for public service"
            },
            "saturacion_urbana": {
                "maps": [
                    "zen gardens or quiet botanical corners",
                    "public fountains or quiet lakes",
                    "modern art galleries or cultural centers"
                ],
                "youtube": "urban desfragmentation meditation",
                "spotify": "focus and clarity ambient soundscapes"
            },
            "agotamiento": {
                "maps": [
                    "dense forests for deep rest",
                    "public gardens with sky views",
                    "open park spaces for inactivity"
                ],
                "youtube": "deep rest guided meditation",
                "spotify": "ancestral healing ambient music"
            }
        }

        config_actual = matriz_intencional_vibrante.get(mente, matriz_intencional_vibrante["agotamiento"])
        termino_maps_elegido = random.choice(config_actual["maps"])
       
        modificador_perfil = ""
        if perfil_tipo == "veterano": modificador_perfil = "+veterans+support"
        elif perfil_tipo == "adulto_mayor": modificador_perfil = "+seniors+accessible"
        elif perfil_tipo == "gubernamental": modificador_perfil = "+government+workers+focus"

        query_maps = f"{termino_maps_elegido}{modificador_perfil}+in+{zip_code}"
        enlace_yt = f"{BIG_TECH_RESOURCES['youtube_base_url']}{urllib.parse.quote_plus(config_actual['youtube'])}"
        enlace_sp = f"{BIG_TECH_RESOURCES['spotify_base_search_url']}{urllib.parse.quote_plus(config_actual['spotify'])}"
       
        destino_titulo_dinamico = f"REDIRECCIÓN DE CONTENCIÓN: CANALIZACIÓN ACTIVA"
        que_hacer_dinamico = f"Liberación autónoma ejecutada con éxito. Desfragmentando el estímulo inicial."

        target_link = f"{link_base}{urllib.parse.quote_plus(query_maps)}"

        final_misiones_para_frontend = [{
            "destino_id": 999,
            "destino_titulo": destino_titulo_dinamico,
            "destino_titulo_en": f"BREAKOUT DEVIATION ACTIVE",
            "que_hacer": que_hacer_dinamico,
            "que_hacer_en": "Immediate breakout executed by the central processing unit.",
            "destino_entorno": "EJE DE REDIRECCIÓN SOMÁTICA",
            "destino_instruccion": instruccion_fisiologica_es,
            "destino_instruccion_en": instruccion_fisiologica_en,
            "destino_coordenadas_gps": target_link,
            "enlace_youtube": enlace_yt,
            "enlace_spotify": enlace_sp,
            "vector_entorno_seleccionado": {**DEFAULT_NECESSITY_VECTOR, "homeostasis_urgente": True},
            "diagnostico_sintoma_es": diagnostico_sintoma_es,
            "diagnostico_sintoma_en": diagnostico_sintoma_en,
        }]

        return JSONResponse({
            "DIRECCIONAMIENTO_MASTER": "ACCION_CAMPO",
            "misiones": final_misiones_para_frontend,
            "forced_recovery": True,
            "legal_notice_es": ADVERTENCIA_LEGAL_ES,
            "legal_notice_en": ADVERTENCIA_LEGAL_EN,
            "drive_prohibited": True
        })

    elif opcion_usuario == "CASA":
        textos_oraculo_casa = MANIFIESTOS_ORACULO.get(mente, MANIFIESTOS_ORACULO["agotamiento"])
        manif_humano_casa = random.choice(textos_oraculo_casa)
        idioma = "EN" if lang == "en" else "ES"
        target_key = f"CASA_{idioma}"
       
        misiones_completas_base = BASE_MISIONES.get(target_key, [])
           
        final_misiones_casa = []
        if not misiones_completas_base:
            if idioma == "ES":
                final_misiones_casa = [{
                    "id": 801,
                    "titulo": "Pausa de Respiración Somática de Protocolo",
                    "titulo_en": "Somatic Protocol Breathing Pause",
                    "descripcion": "Rompe el bucle de la tensión institucional. Inhala profundamente durante 4 segundos, mantén el aire por 4 segundos y exhala en 4 segundos, como un ejercicio de precisión táctica.",
                    "descripcion_en": "Break the loop of institutional tension. Inhale deeply for 4 seconds, hold for 4 seconds, and exhale for 4 seconds, like a tactical precision exercise.",
                    "vector_necesidades": {"silencio": 100, "descanso": 95, "salud": 90}
                }]
            else:
                final_misiones_casa = [{
                    "id": 801,
                    "titulo": "Somatic Protocol Breathing Pause",
                    "titulo_en": "Somatic Protocol Breathing Pause",
                    "descripcion": "Break the loop of institutional tension. Inhale deeply for 4 seconds, hold for 4 seconds, and exhale for 4 seconds, like a tactical precision exercise.",
                    "descripcion_en": "Break the loop of institutional tension. Inhale deeply for 4 seconds, hold for 4 seconds, and exhale for 4 seconds, like a tactical precision exercise.",
                    "vector_necesidades": {"silencio": 100, "descanso": 95, "salud": 90}
                }]
        else:
             for m in misiones_completas_base:
                if isinstance(m, dict):
                    final_misiones_casa.append({
                        "id": m.get("id", 800),
                        "titulo": m.get("titulo", "Misión de Repliegue Interno"),
                        "titulo_en": m.get("titulo_en", "Internal Retreat Mission"),
                        "descripcion": m.get("descripcion", m.get("que_hacer", m.get("porque", "Pausa de bienestar somática de seguridad."))),
                        "descripcion_en": m.get("descripcion_en", m.get("que_hacer_en", m.get("porque_en", "Somatic safety wellness pause."))),
                        "vector_necesidades": m.get("vector_necesidades", {})
                    })

        misiones_domesticas_finales = seleccionar_misiones_casa_inteligente(
            misiones=final_misiones_casa,
            perfil_local=perfil_local,
            historial_casa=payload.get("historial_casa", []),
            cantidad=3
        )
       
        historial_casa_actualizado = payload.get("historial_casa", [])
        for m in misiones_domesticas_finales:
            historial_casa_actualizado = actualizar_historial(historial_casa_actualizado, m["id"], MAX_HISTORY_CASA)

        return JSONResponse({
            "DIRECCIONAMIENTO_MASTER": "MODO_CASA",
            "misiones": misiones_domesticas_finales,
            "oraculo_manifiesto": manif_humano_casa,
            "historial_casa_actualizado": historial_casa_actualizado,
            "forced_recovery": False,
            "legal_notice_es": ADVERTENCIA_LEGAL_ES,
            "legal_notice_en": ADVERTENCIA_LEGAL_EN,
            "drive_prohibited": False
        })

    else:
        opciones_salir_candidatas = BASE_MISIONES["SALIR"].get(mente, BASE_MISIONES["SALIR"]["agotamiento"])
        historial_salir = payload.get("historial_salir", [])
       
        misiones_seleccionadas_raw = seleccionar_n_misiones_inteligentes(
            n=3,
            misiones=opciones_salir_candidatas,
            perfil_local=perfil_local,
            historial_actual=historial_salir
        )

        final_misiones_para_frontend = []
        antidotos_digitales_default_yt = BIG_TECH_RESOURCES[f'youtube_base_url'] + urllib.parse.quote_plus(BIG_TECH_RESOURCES[f'youtube_default_search_{lang}'])
        antidotos_digitales_default_sp = BIG_TECH_RESOURCES[f'spotify_base_search_url'] + urllib.parse.quote_plus(BIG_TECH_RESOURCES[f'spotify_default_genre_link_{lang}'])


        for info_seleccionada in misiones_seleccionadas_raw:
            precio_real = ""
            if budget == "0":
                precio_real = "GASTO: Cero. Recarga sin costo." if lang == "es" else "COST: Zero. Free recharge."
            elif budget == "1":
                precio_real = "GASTO: Bajo. Pequeño gusto." if lang == "es" else "COST: Low. Small treat."
            elif budget == "2":
                precio_real = "GASTO: Abierto. Tu escape." if lang == "es" else "COST: Open. Your escape."

            quienes_van = ""
            if perfil_tipo == "veterano":
                quienes_van = "ACOMPAÑAMIENTO: Solo. Repliegue táctico." if lang == "es" else "COMPANIONSHIP: Solo. Tactical retreat."
            elif perfil_tipo == "adulto_mayor":
                quienes_van = "ACOMPAÑAMIENTO: Individual. Sabiduría y calma." if lang == "es" else "COMPANIONSHIP: Individual. Wisdom and calm."
            elif perfil_tipo == "gubernamental":
                quienes_van = "ACOMPAÑAMIENTO: Autónomo. Descompresión estratégica." if lang == "es" else "COMPANIONSHIP: Autonomous. Strategic decompression."

            titulo_ganador_lang = (info_seleccionada.get("titulo_en", info_seleccionada["titulo"]) or "").upper() if lang == "en" else (info_seleccionada["titulo"] or "").upper()
            que_hacer_lang = info_seleccionada.get('que_hacer_en', info_seleccionada['que_hacer']) or '' if lang == "en" else info_seleccionada["que_hacer"] or ""
            donde_base_lang = info_seleccionada.get("donde_en", info_seleccionada["donde"]) if lang == "en" else info_seleccionada["donde"]
            guia_masticada_lang = info_seleccionada.get('porque_en', info_seleccionada.get('porque', '')) if lang == "en" else info_seleccionada.get('porque', '')

            search_query_parts = []
            if perfil_tipo == "veterano": search_query_parts.append("veteran specific")
            elif perfil_tipo == "adulto_mayor": search_query_parts.append("senior friendly accessible")
            elif perfil_tipo == "gubernamental": search_query_parts.append("government worker focus")
               
            search_query_parts.append(info_seleccionada.get("gps", "public park"))
            target_link = f"{link_base}{urllib.parse.quote_plus('+'.join(search_query_parts))}+{zip_code}"
            final_vector_necesidades = info_seleccionada.get("vector_necesidades", {})

            enlace_yt = info_seleccionada.get("enlace_youtube", antidotos_digitales_default_yt)
            enlace_sp = info_seleccionada.get("enlace_spotify", antidotos_digitales_default_sp)

            final_misiones_para_frontend.append({
                "destino_id": info_seleccionada.get("id"),
                "destino_titulo": titulo_ganador_lang,
                "destino_titulo_en": (info_seleccionada.get("titulo_en", info_seleccionada["titulo"]) or "").upper(),
                "que_hacer": que_hacer_lang,
                "que_hacer_en": info_seleccionada.get("que_hacer_en", info_seleccionada["que_hacer"]),
                "destino_entorno": donde_base_lang,
                "destino_instruccion": guia_masticada_lang.strip(),
                "destino_instruccion_en": info_seleccionada.get("porque_en", info_seleccionada.get("porque", "")).strip(),
                "destino_coordenadas_gps": target_link,
                "vector_entorno_seleccionado": final_vector_necesidades,
                "enlace_youtube": enlace_yt,
                "enlace_spotify": enlace_sp
            })
            historial_salir = actualizar_historial(historial_salir, info_seleccionada["id"], MAX_HISTORY_SALIR)

        return JSONResponse({
            "DIRECCIONAMIENTO_MASTER": "ACCION_CAMPO",
            "misiones": final_misiones_para_frontend,
            "historial_salir_actualizado": historial_salir,
            "forced_recovery": False,
            "legal_notice_es": ADVERTENCIA_LEGAL_ES,
            "legal_notice_en": ADVERTENCIA_LEGAL_EN,
            "drive_prohibited": True
        })

if __name__ == "__main__":
    import uvicorn
    port_env = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port_env, reload=False)
