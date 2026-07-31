// MANDO INTEGRAL DE BIENESTAR - Kernel Somatic Voice Engine V.6.0.1
// Compañía: SAMS GOBERMENT CONTRACTOR
// Archivo: static/motor.js (Lógica Frontend)

const KERNEL = {
    timerInaccion: null,
    timerEnfocado: null,
    temporizadorCascada: null,
    temporizadorCierre: null,
    salidaSugeridaTimeoutId: null,
    salidaTimerId: null, // Timer para frases en modo SALIR (45s)
    timeLeft: 600,
    timeLeftCierre: 60,
    isLocked: false,
    idiomaActual: 'es',
    pasosMisiones: [],
    indiceMision: 0,
    datosLugarGlobal: null, // Guarda la misión seleccionada para SALIR
    tipoEscapeGlobal: "",
   
    contadorToques: 0,
    secuenciaAdelantos: [5, 7, 9, 10, 14, 16, 17, 19, 21, 5],
   
    historialSalir: [],
    historialCasa: [],
    historialPreguntas: [],
    historialRetosSecuencias: [],

    lastDecayTimestamp: null,
    sessionSeed: null,

    MAX_HISTORY_SALIR: 5,
    MAX_HISTORY_CASA: 8,
    MAX_HISTORY_ORACULO: 12,
    MAX_HISTORY_RETOS_SECUENCIAS: 3,
    DECAY_PER_DAY: 0.985,

    conteoInaccion: 0,
    indicePreguntaCascada: 0,

    DEFAULT_NECESSITY_PROFILE: {
        "movimiento": 50, "naturaleza": 50, "silencio": 50, "agua": 50, "sol": 50,
        "sombra": 50, "aire_fresco": 50, "creatividad": 50, "comunidad": 50, "aprendizaje": 50,
        "juego": 50, "contemplacion": 50, "descanso": 50, "organizacion": 50,
        "alimentacion": 50, "musica": 50, "risa": 50, "esperanza": 50,
        "carga_trabajo": 50, "responsabilidad": 50, "soledad": 50, "aislamiento": 50,
        "prision_mental": 0, "agotamiento_mental": 0, "ansiedad": 0
    },
   
    CATALOGO_PREGUNTAS_ES: [
        // Bloque 1: Carga y Sobrecarga (Veteranos, Trabajadores del Gobierno)
        "¿Sientes una carga mental pesada que te persigue a todas partes?",
        "¿El peso de tus responsabilidades te impide encontrar momentos de calma?",
        "¿Te sientes agotado no solo físicamente, sino en lo más profundo de tu ser?",
        "¿La monotonía de la rutina diaria ha convertido tu mente en una prisión?",
        "¿El ruido constante de tu entorno te impide escuchar tu propia voz interior?",

        // Bloque 2: Aislamiento y Búsqueda de Conexión (Adultos Mayores, Veteranos)
        "¿La soledad te acompaña incluso cuando estás rodeado de gente?",
        "¿Anhelas una conexión genuina, pero te cuesta dar el primer paso?",
        "¿Sientes que el mundo avanza rápido y te deja en un segundo plano?",
        "¿Te cuesta encontrar la energía para salir y buscar nuevos horizontes?",
        "¿Hay un sentimiento de abandono que te pesa en el alma?",

        // Bloque 3: Estrés y Desgaste (Trabajadores del Gobierno, Veteranos)
        "¿Experimentas un estrés persistente que no te permite descansar plenamente?",
        "¿Tu cuerpo te habla a través de tensiones y malestares que ignoras?",
        "¿Sientes que has dado tanto que ya no queda mucho para ti mismo?",
        "¿La incertidumbre del futuro o el pasado te agobia de forma recurrente?",
        "¿Buscas distracciones constantes para no enfrentar lo que sientes?",

        // Bloque 4: Desconexión y Anhelo de Propósito (Todos)
        "¿Has perdido la capacidad de asombrarte con las pequeñas cosas de la vida?",
        "¿Te sientes desconectado de tu propio propósito, de aquello que te impulsa?",
        "¿Crees que no hay un espacio accesible donde puedas encontrar alivio sin juicio?",
        "¿Estás listo para soltar la armadura y permitirte ser vulnerable en este momento?",
        "¿Deseas profundamente recuperar el control de tus emociones y tu paz mental?",
        "¿Estás preparado para seguir una guía que te impulse a la acción, hoy mismo?"
    ],
    CATALOGO_PREGUNTAS_EN: [
        // Block 1: Burden and Overload (Veterans, Government Workers)
        "Do you feel a heavy mental burden that follows you everywhere?",
        "Does the weight of your responsibilities prevent you from finding moments of calm?",
        "Do you feel exhausted not just physically, but in the deepest part of your being?",
        "Has the monotony of daily routine turned your mind into a prison?",
        "Does the constant noise of your environment prevent you from hearing your own inner voice?",

        // Block 2: Isolation and Search for Connection (Seniors, Veterans)
        "Does loneliness accompany you even when you're surrounded by people?",
        "Do you long for genuine connection, but find it hard to take the first step?",
        "Do you feel like the world is moving fast and leaving you behind?",
        "Do you find it hard to find the energy to go out and seek new horizons?",
        "Is there a feeling of abandonment that weighs on your soul?",

        // Block 3: Stress and Wear (Government Workers, Veterans)
        "Do you experience persistent stress that prevents you from resting fully?",
        "Does your body speak to you through tensions and discomforts that you ignore?",
        "Do you feel like you've given so much that there's not much left for yourself?",
        "Does the uncertainty of the future or the past overwhelm you recurrently?",
        "Do you constantly seek distractions to avoid facing what you feel?",

        // Block 4: Disconnection and Longing for Purpose (All)
        "Have you lost the ability to be amazed by the small things in life?",
        "Do you feel disconnected from your own purpose, from what drives you?",
        "Do you believe there's no accessible space where you can find relief without judgment?",
        "Are you ready to shed the armor and allow yourself to be vulnerable right now?",
        "Do you deeply wish to regain control of your emotions and mental peace?",
        "Are you prepared to follow a guide that impels you to action, today?"
    ],

    AUDIOS_SECUENCIALES_CASA_ES: [
        "Sigue el pulso en tu pantalla. Concéntrate. Estás conmigo hoy.",
        "Suelta los hombros despacio. Deja caer todo el peso físico y mental de tu día.",
        "No pienses en pendientes ahora. No mires tu lista mental. Respira ya.",
        "Mantén el ritmo constante. Siente el aire fresco limpiando tu pecho.",
        "Te estoy acompañando en silencio. No estás solo en esta habitación.",
        "Siente tus pies firmes apoyados en el suelo. La tierra te sostiene gratis.",
        "El piloto automático está apagado en este segundo. Continúa así.",
        "Quédate justo en este instante. El pasado ya pasó, el presente es tuyo.",
        "Suelta la mandíbula ahora. Libera esa carga que aprietas sin darte cuenta.",
        "Tu mente está despertando poco a poco. Estás ganando control real.",
        "Eres mucho más grande que tus preocupaciones. Respira hondo y despacio.",
        "Rompe el bucle que el ruido externo quiere que seas. Quédate en la sala conmigo.",
        "Escucha mi voz. Nota cómo tu respiración se vuelve más profunda y limpia.",
        "Tus ojos están descansando finalmente de las luces artificiales de la pantalla.",
        "Siente los latidos de tu pecho. Es tu motor vivo latiendo para ti.",
        "Siente el peso fuera de tu espalda. Imagina que dejas caer el cansancio.",
        "No dejes que los pensamientos rápidos te saquen de este momento de paz.",
        "Abandona la prisa de la ciudad hoy. Aquí el tiempo es tuyo.",
        "Tu calma regresará, pero este segundo de paz no se repite.",
        "Siente cómo tus pulmones se llenan de fuerza con cada ciclo de aire azul.",
        "Tu bienestar es prioridad. Recupérate ahora.",
        "Estás borrando el ruido del día. Quédate en la sala respirando conmigo.",
        "La rutina diaria se ha roto. Tú gobiernas tus decisiones en este instante.",
        "El suelo está firme debajo tuyo. Siente la estabilidad de la tierra.",
        "Tu pecho está libre de agobios ahora. Expulsa todo lo malo de golpe.",
        "Estás recuperando tu centro vital. Sigue la luz del círculo.",
        "Tu mente es fuerte. Has domado el miedo a las presiones de hoy.",
        "Faltan pocos segundos para el reinicio definitivo. Siente la esperanza.",
        "Estás completamente a salvo aquí. Quédate en paz absoluta en este segundo."
    ],
    AUDIOS_SECUENCIALES_CASA_EN: [
        "Follow the pulse on your screen. Concentrate. You are with me today.",
        "Slowly relax your shoulders. Let all the physical and mental weight of your day fall away.",
        "Don't think about pending tasks now. Don't look at your mental list. Breathe now.",
        "Maintain a constant rhythm. Feel the fresh air cleansing your chest.",
        "I am accompanying you in silence. You are not alone in this room.",
        "Feel your feet firmly on the ground. The earth supports you for free.",
        "The autopilot is off this second. Keep going.",
        "Stay right in this instant. The past is gone, the present is yours.",
        "Release your jaw now. Let go of that tension you hold without realizing.",
        "Your mind is slowly awakening. You are gaining real control.",
        "You are much bigger than your worries. Breathe deeply and slowly.",
        "Break the loop the external noise wants you to be. Stay in the room with me.",
        "Listen to my voice. Notice how your breathing becomes deeper and cleaner.",
        "Your eyes are finally resting from the artificial lights of the screen.",
        "Feel your heartbeat. It's your living engine beating for you.",
        "Feel the weight off your back. Imagine shaking off tiredness.",
        "Don't let racing thoughts take you out of this peaceful moment.",
        "Abandon the city's rush today. Here, time is yours.",
        "Your calm will return, but this second of peace will not repeat.",
        "Feel your lungs fill with strength with each cycle of blue air.",
        "Your well-being is a priority. Recover now.",
        "You are erasing the day's noise. Stay in the room breathing with me.",
        "The daily routine is broken. You govern your decisions at this instant.",
        "The ground is firm beneath you. Feel the stability of the earth.",
        "Your chest is free from worries now. Expel all negativity at once.",
        "You are regaining your vital center. Follow the light of the circle.",
        "Your mind is strong. You have tamed the fear of today's pressures.",
        "Only a few seconds left for the definitive reset. Feel the hope.",
        "You are completely safe here. Remain in absolute peace this second."
    ],

    AUDIOS_SECUENCIALES_SALIR_ES: [
        "Respira hondo. El mundo exterior espera, pero tú controlas tu paz.",
        "Cada segundo es una oportunidad para soltar lo que no te sirve.",
        "Visualiza tu destino. Siente la libertad de ir hacia él con propósito.",
        "Elige tu camino. No hay errores, solo nuevas rutas de bienestar.",
        "Estás en control. Tu decisión te guía a un nuevo espacio de calma.",
        "Siente la expectativa. La aventura te espera, sin agobios ni prisa.",
        "Estás a punto de romper el patrón. Un nuevo aire te revitaliza.",
        "Concéntrate en el momento. Tu mente es libre para explorar y disfrutar.",
        "Suelta las cadenas mentales. Tu cuerpo te pide movimiento y libertad.",
        "Estás eligiendo tu bienestar. Cada paso es un acto de amor propio."
    ],
    AUDIOS_SECUENCIALES_SALIR_EN: [
        "Breathe deeply. The outside world waits, but you control your peace.",
        "Every second is an opportunity to release what doesn't serve you.",
        "Visualize your destination. Feel the freedom of moving towards it with purpose.",
        "Choose your path. There are no mistakes, only new routes to well-being.",
        "You are in control. Your decision guides you to a new space of calm.",
        "Feel the anticipation. Adventure awaits you, without worries or rush.",
        "You are about to break the pattern. A fresh air revitalizes you.",
        "Focus on the moment. Your mind is free to explore and enjoy.",
        "Release mental chains. Your body craves movement and freedom.",
        "You are choosing your well-being. Every step is an act of self-love."
    ],

    AUDIOS_CONDUCCION_ES: "Atención. Tu Mando Integral de Bienestar ha bloqueado tu pantalla por tu seguridad. Estás en un entorno de tránsito, donde tu cuerpo se mueve mecánicamente, pero tu mente está atrapada en una prisión de monotonía o estrés. No mires este teléfono. Mantén tus ojos fijos en tu entorno. Hackea este trayecto mediante el Módulo de Ventilación Pasiva: inhala profundamente por la nariz, retén el aire sintiendo los latidos, y exhala de forma lenta y prolongada vaciando el aire acumulado. Utiliza tu asiento y tus manos como anclas táctiles de presencia. Observa la inmensidad de las nubes o el cielo sobre el horizonte sin perder la concentración. Estás en control de tu vida, no del tráfico. Has transformado este trayecto en tu pista de descompresión cerebral a costo cero. Ejecución pasiva activada.",
    AUDIOS_CONDUCCION_EN: "Attention. Your Integral Well-being Command has locked your screen for your safety. You are in a transit environment, where your body moves mechanically, but your mind is trapped in a prison of monotony or stress. Do not look at this phone. Keep your eyes fixed on your surroundings. Hack this journey through the Passive Ventilation Module: inhale deeply through your nose, hold your breath feeling your heart beat, and exhale slowly and prolonged emptying accumulated air. Use your seat and hands as tactile anchors of presence. Observe the vastness of the clouds or the sky over the horizon without losing concentration. You are in control of your life, not of traffic. You have transformed this journey into your brain decompression track at zero cost. Passive execution activated.",


    CATALOGO_RETOS_ES: [
        {"id": 201, "titulo": "EL RETO DEL SILENCIO RADICAL", "descripcion": "Silencia las aplicaciones que más ruido te generan por una hora. Tu atención es un recurso valioso que necesita descanso. Reconecta con la quietud.", "img": "silence.svg"},
        {"id": 202, "titulo": "EL RETO DEL MICRO-ORDEN", "descripcion": "Guarda solo cinco objetos que estén fuera de lugar en tu entorno. Cinco son suficientes por hoy. Siente el control restaurado en pequeñas acciones.", "img": "observe.svg"},
        {"id": 203, "titulo": "EL RETO DE LA RESPIRACIÓN CONSCIENTE", "descripcion": "Realiza cinco respiraciones profundas y lentas. Concéntrate en el aire que entra y sale de tu cuerpo. No tienes que hacer nada más. Este es tu ancla.", "img": "square_breath.svg"},
        {"id": 204, "titulo": "EL RETO DE LA GRATITUD PERSONAL", "descripcion": "Escribe en una nota mental o en papel tres cosas que hoy tienes y que en algún momento deseabas. Tu mente necesita recordar tu propio avance y valor.", "img": "gratitude.svg"},
        {"id": 205, "titulo": "EL RETO DEL AGUA VITAL", "descripcion": "Levántate despacio, bebe un vaso completo de agua fresca. Siente el líquido. Vuelve a tu asiento respirando con calma. Es un reinicio sencillo.", "img": "stretch.svg"},
        {"id": 206, "titulo": "EL RETO DEL HORIZONTE ABIERTO", "descripcion": "Abre una ventana durante dos minutos y observa el cielo o un punto lejano sin mirar tu teléfono. Permite que tus ojos y tu mente se expandan.", "img": "nature_sound.svg"},
        {"id": 207, "titulo": "EL RETO DEL ESTIRAMIENTO SUTIL", "descripcion": "Realiza un estiramiento suave de cuello u hombros. Suelta la tensión acumulada. Permite que tu cuerpo se libere de la rigidez mental.", "img": "stretch.svg"},
        {"id": 208, "titulo": "EL RETO DEL SONIDO AMBIENTAL", "descripcion": "Cierra los ojos por un minuto y concéntrate en el sonido más lejano que puedas escuchar. Despierta tu oído a los detalles que habitualmente ignoras.", "img": "silence.svg"},
        {"id": 209, "titulo": "EL RETO DE LA POSTURA FUERTE", "descripcion": "Endereza tu espalda y siente cómo te sostienes a ti mismo. Una postura firme puede influir en tu estado mental. Siente tu dignidad.", "img": "observe.svg"},
        {"id": 210, "titulo": "EL RETO DE LA RISA INTERNA", "descripcion": "Sonríe por 15 segundos, incluso si no tienes ganas. La acción de sonreír puede iniciar un cambio positivo en tu química interna. Siente la chispa.", "img": "laugh.svg"},
    ],
    CATALOGO_RETOS_EN: [
        {"id": 201, "titulo": "THE RADICAL SILENCE CHALLENGE", "descripcion": "Mute the apps that generate the most noise for an hour. Your attention is a valuable resource that needs rest. Reconnect with stillness.", "img": "silence.svg"},
        {"id": 202, "titulo": "THE MICRO-ORDER CHALLENGE", "descripcion": "Put away only five misplaced objects in your environment. Five are enough for today. Feel control restored in small actions.", "img": "observe.svg"},
        {"id": 203, "titulo": "THE CONSCIOUS BREATHING CHALLENGE", "descripcion": "Take five deep, slow breaths. Concentrate on the air entering and leaving your body. You don't have to do anything else. This is your anchor.", "img": "square_breath.svg"},
        {"id": 204, "titulo": "THE PERSONAL GRATITUDE CHALLENGE", "descripcion": "Write in a mental note or on paper three things you have today that you once desired. Your mind needs to remember your own progress and worth.", "img": "gratitude.svg"},
        {"id": 205, "titulo": "THE VITAL WATER CHALLENGE", "descripcion": "Slowly stand up, drink a full glass of fresh water. Feel the liquid. Return to your seat breathing calmly. It's a simple reset.", "img": "stretch.svg"},
        {"id": 206, "titulo": "THE OPEN HORIZON CHALLENGE", "descripcion": "Open a window for two minutes and observe the sky or a distant point without looking at your phone. Allow your eyes and mind to expand.", "img": "nature_sound.svg"},
        {"id": 207, "titulo": "THE SUBTLE STRETCH CHALLENGE", "descripcion": "Perform a gentle neck or shoulder stretch. Release accumulated tension. Allow your body to free itself from mental stiffness.", "img": "stretch.svg"},
        {"id": 208, "titulo": "THE AMBIENT SOUND CHALLENGE", "descripcion": "Close your eyes for one minute and focus on the farthest sound you can hear. Awaken your ear to details you usually ignore.", "img": "silence.svg"},
        {"id": 209, "titulo": "THE STRONG POSTURE CHALLENGE", "descripcion": "Straighten your back and feel how you support yourself. A firm posture can influence your mental state. Feel your dignity.", "img": "observe.svg"},
        {"id": 210, "titulo": "THE INNER LAUGHTER CHALLENGE", "descripcion": "Smile for 15 seconds, even if you don't feel like it. The act of smiling can initiate a positive change in your internal chemistry. Feel the spark.", "img": "laugh.svg"},
    ],

    obtenerPerfilLocal() {
        let perfilRaw = localStorage.getItem("mib_perfil_dinamico");
        let perfil = {};

        if (!perfilRaw) {
            perfil = { ...this.DEFAULT_NECESSITY_PROFILE };
        } else {
            try {
                perfil = JSON.parse(perfilRaw);
                for (const need in this.DEFAULT_NECESSITY_PROFILE) {
                    if (!(need in perfil)) {
                        perfil[need] = this.DEFAULT_NECESSITY_PROFILE[need];
                    }
                }
            } catch (e) {
                console.error("Error al analizar mib_perfil_dinamico de localStorage, reiniciando.", e);
                perfil = { ...this.DEFAULT_NECESSITY_PROFILE };
            }
        }

        const now = Date.now();
        let lastDecayTimestamp = parseInt(localStorage.getItem("mib_last_decay") || now);
        this.sessionSeed = localStorage.getItem("mib_session_seed") || Math.random().toString(36).substring(2, 15);

        const daysPassed = (now - lastDecayTimestamp) / (1000 * 60 * 60 * 24);

        if (daysPassed >= 0.5) { // Aplicar "decay" cada 12 horas para mayor reactividad
            const newPerfil = {};
            const base = 50; // Valor base para necesidades
            for (const necesidad in perfil) {
                if (necesidad === "prision_mental" || necesidad === "agotamiento_mental" || necesidad === "ansiedad") {
                    newPerfil[necesidad] = Math.max(0, perfil[necesidad] - (daysPassed * 5)); // Decay más rápido para indicadores negativos
                    continue;
                }
                const valor = perfil[necesidad];
                let diferencia = valor - base;
                diferencia *= (this.DECAY_PER_DAY ** daysPassed);
                newPerfil[necesidad] = Math.round((base + diferencia) * 100) / 100;
            }
            perfil = newPerfil;
            lastDecayTimestamp = now;
        }

        perfil.fecha = new Date(now).toISOString().split('T')[0];
        perfil.timestamp = now;

        localStorage.setItem("mib_perfil_dinamico", JSON.stringify(perfil));
        localStorage.setItem("mib_last_decay", lastDecayTimestamp.toString());
        localStorage.setItem("mib_session_seed", this.sessionSeed);

        return perfil;
    },

    init() {
        const storedLang = localStorage.getItem("mib_language");
        if (storedLang) {
            this.idiomaActual = storedLang;
        } else {
            localStorage.setItem("mib_language", this.idiomaActual);
        }
        try {
            this.historialSalir = JSON.parse(localStorage.getItem("mib_historial_salir") || "[]");
            this.historialCasa = JSON.parse(localStorage.getItem("mib_historial_casa") || "[]");
            this.historialPreguntas = JSON.parse(localStorage.getItem("mib_historial_oraculo") || "[]");
            this.historialRetosSecuencias = JSON.parse(localStorage.getItem("mib_historial_retos_secuencias") || "[]");
        } catch (e) {
            console.error("Error al analizar el historial de localStorage, reiniciando historiales específicos.", e);
            this.historialSalir = [];
            this.historialCasa = [];
            this.historialPreguntas = [];
            this.historialRetosSecuencias = [];
            localStorage.removeItem("mib_historial_salir");
            localStorage.removeItem("mib_historial_casa");
            localStorage.removeItem("mib_historial_oraculo");
            localStorage.removeItem("mib_historial_retos_secuencias");
        }
        this.obtenerPerfilLocal();

        const zipInput = document.getElementById('inp-zip');
        if (zipInput) {
            zipInput.addEventListener('input', () => this.validarZip());
            this.validarZip();
        }

        // Add event listeners for the new floating buttons
        document.getElementById('btn-volver-app').addEventListener('click', () => this.reiniciarExperiencia());
        document.getElementById('btn-reporte-bienestar').addEventListener('click', () => this.mostrarReporteBienestar());
    },

    despertarInicial() {
        document.getElementById('pantalla-bienvenida').style.display = 'none';
        document.getElementById('wrapper-form').classList.remove('hidden');
        document.getElementById('btn-volver-app').classList.remove('hidden'); // Mostrar botón de volver
        // Los botones de WhatsApp y Messenger deben permanecer visibles si se usan
        // document.getElementById('btn-whatsapp').classList.remove('hidden');
        // document.getElementById('btn-messenger').classList.remove('hidden');
        document.getElementById('btn-reporte-bienestar').classList.remove('hidden'); // Mostrar botón de reporte
       
        this.cambiarIdioma(this.idiomaActual);
       
        const saludos_es = [
            "Bienvenido al Mando Integral de Bienestar. Tu espacio seguro. Escucha mis preguntas en pantalla.",
            "Mando Integral de Bienestar activo. Concéntrate un momento. Mira las opciones en tu pantalla ya.",
            "Entraste al Mando Integral de Bienestar. Rompamos tu piloto automático ahora mismo. Toca lo que sientes hoy."
        ];
        const saludos_en = [
            "Welcome to the Integral Well-being Command. Your safe space. Listen to my questions on screen.",
            "Integral Well-being Command active. Focus for a moment. Look at the options on your screen now.",
            "You entered the Integral Well-being Command. Let's break your autopilot right now. Tap what you feel today."
        ];
        const saludos = this.idiomaActual === 'es' ? saludos_es : saludos_en;
        this.hablar(saludos[Math.floor(Math.random() * saludos.length)]);
       
        this.inyectarBloquePreguntas();
        this.iniciarMonitoreoInaccion();
       
        this.activarBotonMandoLibreInicial();
    },

    inyectarBloquePreguntas() {
        const grid = document.getElementById('contenedor-preguntas-oraculo');
        if (!grid) return;
       
        clearInterval(this.temporizadorCascada);
        grid.innerHTML = "";
        this.indicePreguntaCascada = 0;
       
        const catalogo = this.idiomaActual === 'es' ? this.CATALOGO_PREGUNTAS_ES : this.CATALOGO_PREGUNTAS_EN;
        let preguntasDisponiblesIndices = [];
        let preguntasYaVistasRecientemente = new Set(this.historialPreguntas);

        let unseenIndices = [];
        for (let i = 0; i < catalogo.length; i++) {
            if (!preguntasYaVistasRecientemente.has(i)) {
                unseenIndices.push(i);
            }
        }

        if (unseenIndices.length < 3) {
            this.historialPreguntas = [];
            localStorage.removeItem("mib_historial_oraculo");
            for (let i = 0; i < catalogo.length; i++) {
                unseenIndices.push(i);
            }
        }
       
        for (let i = unseenIndices.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [unseenIndices[i], unseenIndices[j]] = [unseenIndices[j], unseenIndices[i]];
        }

        let preguntasSeleccionadasIndices = [];
        let blockIndices = Array.from({length: Math.ceil(catalogo.length / 3)}, (_, i) => i);
        let blocksUsedInCurrentSelection = new Set();
       
        for (let i = 0; i < 3; i++) {
            if (unseenIndices.length === 0) break;

            let candidateIndex = -1;
            for (let j = 0; j < unseenIndices.length; j++) {
                const currentIdx = unseenIndices[j];
                const currentBlock = Math.floor(currentIdx / 3);
                if (!blocksUsedInCurrentSelection.has(currentBlock)) {
                    candidateIndex = j;
                    blocksUsedInCurrentSelection.add(currentBlock);
                    break;
                }
            }

            if (candidateIndex === -1) {
                candidateIndex = 0;
                const currentBlock = Math.floor(unseenIndices[candidateIndex] / 3);
                blocksUsedInCurrentSelection.add(currentBlock);
            }
           
            const selectedIndex = unseenIndices.splice(candidateIndex, 1)[0];
            preguntasSeleccionadasIndices.push(selectedIndex);
           
            this.historialPreguntas.push(selectedIndex);
        }
        this.historialPreguntas = this.historialPreguntas.slice(-this.MAX_HISTORY_ORACULO);
        localStorage.setItem("mib_historial_oraculo", JSON.stringify(this.historialPreguntas));

        preguntasSeleccionadasIndices.forEach((questionIdx, i) => {
            let preguntaTexto = catalogo[questionIdx];
            if (!preguntaTexto) return;

            let btn = document.createElement('button');
            btn.className = 'btn-pregunta-crisis';
            btn.id = `btn-pregunta-${i}`;
            btn.innerText = `${i + 1}. ${preguntaTexto}`;
            btn.onclick = () => this.reaccionarPreguntaSeleccionada(preguntaTexto);
            grid.appendChild(btn);
        });

        this.iniciarEfectoCascada();
    },

    iniciarEfectoCascada() {
        this.indicePreguntaCascada = 0;
       
        const totalButtons = document.querySelectorAll('.btn-pregunta-crisis').length;
        if (totalButtons === 0) {
            this.liberarCajonEscrituraLibre();
            return;
        }

        this.temporizadorCascada = setInterval(() => {
            let botonParaEliminar = document.getElementById(`btn-pregunta-${this.indicePreguntaCascada}`);
           
            if (botonParaEliminar) {
                botonParaEliminar.classList.add('fade-out');
               
                let siguienteIdx = this.indicePreguntaCascada + 1;
                let siguienteBoton = document.getElementById(`btn-pregunta-${siguienteIdx}`);
                if (siguienteBoton) {
                    let textoLimpio = siguienteBoton.innerText.substring(3);
                    this.hablar(textoLimpio);
                }
                this.indicePreguntaCascada++;
            } else {
                clearInterval(this.temporizadorCascada);
                this.liberarCajonEscrituraLibre();
            }
        }, 8000);
    },

    activarBotonMandoLibreInicial() {
        const textarea = document.getElementById('inp-text-libre');
        const btnLibre = document.getElementById('btn-activar-libre');
        const lblDesahogo = document.getElementById('lbl-desahogo');
        const instruccion = document.getElementById('lbl-oraculo-instruccion');
        const zipInput = document.getElementById('inp-zip');

        if (instruccion) {
            instruccion.innerText = this.idiomaActual === 'es' ? "¿Qué te agobia hoy?" : "What weighs on you today?";
            instruccion.style.color = "var(--accent)";
        }
        if (lblDesahogo) lblDesahogo.style.color = "#666";

        if (btnLibre) {
            const isZipInvalid = zipInput && zipInput.value.trim().length > 0 && !zipInput.checkValidity();
            const isTextareaEmpty = textarea.value.trim().length <= 3;

            if (isZipInvalid || isTextareaEmpty) {
                btnLibre.style.background = "#111";
                btnLibre.style.color = "#555";
                btnLibre.style.borderColor = "#222";
                btnLibre.disabled = true;
            } else {
                btnLibre.style.background = "var(--green-action)";
                btnLibre.style.color = "#fff";
                btnLibre.style.borderColor = "var(--green-action)";
                btnLibre.disabled = false;
            }

            btnLibre.onclick = () => {
                let textoEscrito = textarea.value.trim();
                const isZipInvalidOnSubmit = zipInput && zipInput.value.trim().length > 0 && !zipInput.checkValidity();

                if (isZipInvalidOnSubmit) {
                    this.hablar(this.idiomaActual === 'es' ? "Por favor, introduce un código postal válido." : "Please enter a valid ZIP code.");
                    zipInput.focus();
                    return;
                }
                if (textoEscrito.length > 3) {
                    this.reaccionarPreguntaSeleccionada(textoEscrito);
                } else {
                    this.hablar(this.idiomaActual === 'es' ? "Escribe tu sentir en el cuadro antes de iniciar la intervención." : "Write your feeling in the box before starting the intervention.");
                }
            };
        }
        if (textarea) {
            textarea.removeEventListener('input', this.textareaInputHandler);
            this.textareaInputHandler = () => {
                const isZipInvalid = zipInput && zipInput.value.trim().length > 0 && !zipInput.checkValidity();
               
                if (textarea.value.trim().length > 3 && !isZipInvalid) {
                    if (btnLibre) {
                        btnLibre.style.background = "var(--green-action)";
                        btnLibre.style.color = "#fff";
                        btnLibre.style.borderColor = "var(--green-action)";
                        btnLibre.disabled = false;
                    }
                } else {
                    if (btnLibre) {
                        btnLibre.style.background = "#111";
                        btnLibre.style.color = "#555";
                        btnLibre.style.borderColor = "#222";
                        btnLibre.disabled = true;
                    }
                }
                this.validarZip();
            };
            textarea.addEventListener('input', this.textareaInputHandler);
        }
        this.validarZip();
    },

    validarZip() {
        const zipInput = document.getElementById('inp-zip');
        const btnActivarLibre = document.getElementById('btn-activar-libre');
        const textarea = document.getElementById('inp-text-libre');

        if (!zipInput || !btnActivarLibre || !textarea) return;

        const zipValue = zipInput.value.trim();
        const isValidZip = zipInput.checkValidity();
        const hasTextareaContent = textarea.value.trim().length > 3;

        if (zipValue.length > 0 && !isValidZip) {
            zipInput.style.borderColor = "var(--accent)";
            btnActivarLibre.disabled = true;
            btnActivarLibre.style.background = "#111";
            btnActivarLibre.style.color = "#555";
            btnActivarLibre.style.borderColor = "#222";
        } else {
            zipInput.style.borderColor = "#222";
            if (hasTextareaContent) {
                btnActivarLibre.disabled = false;
                btnActivarLibre.style.background = "var(--green-action)";
                btnActivarLibre.style.color = "#fff";
                btnActivarLibre.style.borderColor = "var(--green-action)";
            } else {
                btnActivarLibre.disabled = true;
                btnActivarLibre.style.background = "#111";
                btnActivarLibre.style.color = "#555";
                btnActivarLibre.style.borderColor = "#222";
            }
        }
    },

    liberarCajonEscrituraLibre() {
        const textarea = document.getElementById('inp-text-libre');
        const lblDesahogo = document.getElementById('lbl-desahogo');
        const instruccion = document.getElementById('lbl-oraculo-instruccion');

        if (instruccion) {
            instruccion.innerText = this.idiomaActual === 'es' ? "Mando libre listo. Cuéntame qué te sucede." : "Free command ready. Tell me what's happening.";
            instruccion.style.color = "var(--green-action)";
        }
        if (lblDesahogo) lblDesahogo.style.color = "#fff";
        if (textarea) textarea.focus();
        this.validarZip();
    },

    iniciarMonitoreoInaccion() {
        clearInterval(this.timerInaccion);
        this.conteoInaccion = 0;
        this.timerInaccion = setInterval(() => {
            this.conteoInaccion++;
            if (this.conteoInaccion === 3 || this.conteoInaccion === 6) {
                clearInterval(this.temporizadorCascada);
                this.inyectarBloquePreguntas();
                this.hablar(this.idiomaActual === 'es' ? "Avanzamos de nivel. Mira estas otras opciones en pantalla." : "Moving up. Look at these other options on screen.");
            } else if (this.conteoInaccion >= 9) {
                clearInterval(this.timerInaccion);
                clearInterval(this.temporizadorCascada);
                this.hablar(this.idiomaActual === 'es' ? "Disculpa. Te daré tu tiempo. Sé que tu mente está cansada. Estaré aquí esperando." : "Apologies. I will give you time. I know your mind is tired. I will be waiting here.");
                const instruccion = document.getElementById('lbl-oraculo-instruccion');
                if (instruccion) {
                    instruccion.innerText = this.idiomaActual === 'es' ? "Tomando un respiro. Toca cuando estés listo..." : "Taking a breath. Tap when you are ready...";
                    instruccion.style.color = "#666";
                }
            }
        }, 8000);
    },

    reaccionarPreguntaSeleccionada(textoPregunta) {
        clearInterval(this.timerInaccion);
        clearInterval(this.temporizadorCascada);
       
        document.getElementById('inp-text-libre').value = textoPregunta;
        this.ejecutar();
    },

    hablar(texto) {
        if (!('speechSynthesis' in window)) {
            console.warn("Speech Synthesis API no soportada en este navegador.");
            return;
        }
        if (!texto) return;
        window.speechSynthesis.cancel();
        let fx = texto.replace(/MANDO INTEGRAL DE BIENESTAR/gi, "MANDO INTEGRAL").replace(/<[^>]*>/g, '');
        const msg = new SpeechSynthesisUtterance(fx);
        msg.lang = this.idiomaActual === 'es' ? 'es-US' : 'en-US';
        msg.rate = 1.10; // Velocidad ligeramente más lenta para mayor claridad
        msg.volume = 1; // Asegurar volumen máximo
        window.speechSynthesis.speak(msg);
    },

    cambiarIdioma(lang) {
        this.idiomaActual = lang;
        localStorage.setItem("mib_language", lang);
        document.getElementById('lang-es').classList.toggle('active', lang === 'es');
        document.getElementById('lang-en').classList.toggle('active', lang === 'en');
       
        const t = {
            es: { title: "MANDO INTEGRAL DE BIENESTAR", zip: "Código Postal", instruccion: "¿Qué te agobia hoy?", desahogo: "O escribe aquí el peso que llevas si no aparece arriba:", placeholder: "Describe tu situación actual sin rodeos...", btn: "INICIAR INTERVENCIÓN", budget0: "Cero Costo", budget1: "Mínimo Gasto", budget2: "Gasto Abierto", veterano: "Veterano de Guerra", adultoMayor: "Adulto Mayor", trabajadorGob: "Trabajador del Gobierno", menteAburrido: "Aburrido", menteAgotado: "Agotado", menteEstresado: "Estresado", menteCansado: "Cansado", menteAnsioso: "Ansioso", modoSalir: "ACCIÓN", modoCasa: "CASA", recomenzar: "REINICIAR SESIÓN", puertaAbierta: "La puerta está abierta. ¿Continuamos?", volverApp: "Volver al Inicio", reporteBienestar: "Reporte de Bienestar", alert: "Idioma cambiado a español." },
            en: { title: "INTEGRAL WELL-BEING COMMAND", zip: "ZIP Code", instruccion: "What weighs on you today?", desahogo: "Or freely write the burden you carry if it doesn't appear above:", placeholder: "Describe your current situation directly...", btn: "START INTERVENTION", budget0: "Zero Cost", budget1: "Minimal Expense", budget2: "Open Expense", veterano: "War Veteran", adultoMayor: "Senior Adult", trabajadorGob: "Government Worker", menteAburrido: "Bored", menteAgotado: "Exhausted", menteEstresado: "Stressed", menteCansado: "Tired", menteAnsioso: "Anxious", modoSalir: "ACTION", modoCasa: "HOME", recomenzar: "RESTART SESSION", puertaAbierta: "The door is open. Shall we continue?", volverApp: "Return to Home", reporteBienestar: "Well-being Report", alert: "Language switched to English." }
        }[lang];
       
        document.getElementById('html-title').innerText = t.title;
        document.getElementById('txt-app-title').innerText = t.title;
        document.getElementById('lbl-zip').innerText = t.zip;
        document.getElementById('lbl-oraculo-instruccion').innerText = t.instruccion;
        document.getElementById('lbl-desahogo').innerText = t.desahogo;
        document.getElementById('inp-text-libre').placeholder = t.placeholder;
        document.getElementById('btn-activar-libre').innerText = t.btn;
        document.getElementById('opt-budget-0').innerText = t.budget0;
        document.getElementById('opt-budget-1').innerText = t.budget1;
        document.getElementById('opt-budget-2').innerText = t.budget2;
        document.getElementById('opt-perfil-veterano').innerText = t.veterano;
        document.getElementById('opt-perfil-adulto-mayor').innerText = t.adultoMayor;
        document.getElementById('opt-perfil-trabajador-gobierno').innerText = t.trabajadorGob;
        document.getElementById('opt-mente-aburrido').innerText = t.menteAburrido;
        document.getElementById('opt-mente-agotado').innerText = t.menteAgotado;
        document.getElementById('opt-mente-estresado').innerText = t.menteEstresado;
        document.getElementById('opt-mente-cansado').innerText = t.menteCansado;
        document.getElementById('opt-mente-ansioso').innerText = t.menteAnsioso;
        document.querySelector('#modo-selector option[value="SALIR"]').innerText = t.modoSalir;
        document.querySelector('#modo-selector option[value="CASA"]').innerText = t.modoCasa;
        document.getElementById('btn-reporte-bienestar').title = t.reporteBienestar;
       
        const cierreLogo = document.getElementById('cierre-logo');
        if (cierreLogo) cierreLogo.innerText = t.title;
        const cierreBoton = document.getElementById('btn-recomenzar-experiencia');
        if (cierreBoton) cierreBoton.innerText = t.recomenzar;
        const cierreMensajeFinal = document.getElementById('cierre-mensaje-final');
        if (cierreMensajeFinal) cierreMensajeFinal.innerText = t.puertaAbierta;
        const btnVolverApp = document.getElementById('btn-volver-app');
        if (btnVolverApp) btnVolverApp.title = t.volverApp;

        this.hablar(t.alert);
        this.inyectarBloquePreguntas();
        this.activarBotonMandoLibreInicial();
    },

    async ejecutar() {
        if (this.isLocked) return;
        this.isLocked = true;

        clearInterval(this.timerInaccion);
        clearInterval(this.temporizadorCascada);
        clearInterval(this.timerEnfocado);
        clearInterval(this.salidaTimerId);
        window.speechSynthesis.cancel();
        if (this.salidaSugeridaTimeoutId) {
            clearTimeout(this.salidaSugeridaTimeoutId);
            this.salidaSugeridaTimeoutId = null;
        }

        const modoActual = document.getElementById('modo-selector') ? document.getElementById('modo-selector').value : "SALIR";
        const zipInput = document.getElementById('inp-zip');
        const desahogoInput = document.getElementById('inp-text-libre');

        if (zipInput && zipInput.value.trim().length > 0 && !zipInput.checkValidity()) {
            alert(this.idiomaActual === 'es' ? "Error: Código Postal inválido. Por favor, corrígelo." : "Error: Invalid ZIP Code. Please correct it.");
            this.isLocked = false;
            zipInput.focus();
            return;
        }

        const payload = {
            zip: zipInput ? zipInput.value.trim() : "",
            modo: modoActual,
            desahogo: desahogoInput ? desahogoInput.value.trim() : "",
            lang: this.idiomaActual,
            mente: document.getElementById('mente-selector') ? document.getElementById('mente-selector').value : "aburrido",
            budget: document.getElementById('budget-selector') ? document.getElementById('budget-selector').value : "0",
            perfil: document.getElementById('perfil-selector') ? document.getElementById('perfil-selector').value : "veterano_guerra",
            perfil_local: this.obtenerPerfilLocal(),
        };

        if (modoActual === "CASA") {
            payload.historial_casa = this.historialCasa;
        } else {
            payload.historial_salir = this.historialSalir;
        }

        const container = document.getElementById('wrapper-interactive');
        document.getElementById('wrapper-form').classList.add('hidden');
        document.getElementById('pantalla-cierre').classList.add('hidden');
        container.innerHTML = `<div style='text-align:center; padding:40px 0;'><h2 style='color:#fff; font-size:1.1rem;'>${this.idiomaActual === 'es' ? 'CONECTANDO CON EL MANDO INTEGRAL...' : 'CONNECTING TO INTEGRAL COMMAND...'}</h2></div>`;
        container.classList.remove('hidden');

        try {
            const r = await fetch("/api/mando-integral", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await r.json();

            if (data.error) {
                alert(data.error);
                document.getElementById('wrapper-form').classList.remove('hidden');
                container.classList.add('hidden');
                this.isLocked = false;
                this.validarZip();
                return;
            }

            this.tipoEscapeGlobal = data.DIRECCIONAMIENTO_MASTER;
            this.indiceMision = 0;
           
            if (this.tipoEscapeGlobal === "ACCION_CAMPO" && data.historial_salir_actualizado) {
                this.historialSalir = data.historial_salir_actualizado;
                localStorage.setItem("mib_historial_salir", JSON.stringify(this.historialSalir));
                this.pasosMisiones = data.misiones;
                this.mostrarOpcionesSalir(container);
            }
            else if (this.tipoEscapeGlobal === "INTERVENCION_DOMESTICA" && data.historial_casa_actualizado) {
                this.historialCasa = data.historial_casa_actualizado;
                localStorage.setItem("mib_historial_casa", JSON.stringify(this.historialCasa));
                this.pasosMisiones = data.misiones;
                this.procesarFlujoSecuencial(container);
            }


        } catch (error) {
            console.error("Error de conexión:", error);
            alert(this.idiomaActual === 'es' ? "Error de conexión con el servidor. Por favor, inténtalo de nuevo." : "Connection error with the server. Please try again.");
            document.getElementById('wrapper-form').classList.remove('hidden');
            container.classList.add('hidden');
            this.isLocked = false;
            this.validarZip();
        }
    },

    mostrarOpcionesSalir(container) {
        clearInterval(this.timerEnfocado);
        clearInterval(this.salidaTimerId);
        window.speechSynthesis.cancel();

        const t = {
            es: { choosePath: "ELIGE TU CAMINO DE ACCIÓN", chooseOne: "Toca una opción para activar la guía:" },
            en: { choosePath: "CHOOSE YOUR PATH OF ACTION", chooseOne: "Tap an option to activate the guide:" }
        }[this.idiomaActual];

        container.innerHTML = `
        <div class="mision-choices-container">
            <h2 class="salida-main-title">${t.choosePath}</h2>
            <p class="salida-choose-instruction">${t.chooseOne}</p>
            <div id="salida-options-grid" class="salida-grid">
                <!-- Las opciones se inyectarán aquí -->
            </div>
        </div>`;

        const optionsGrid = document.getElementById('salida-options-grid');
        this.pasosMisiones.forEach((mission, index) => {
            const missionTitle = this.idiomaActual === 'es' ? mission.destino_titulo : mission.destino_titulo_en || mission.destino_titulo;
            const missionWhatToDo = this.idiomaActual === 'es' ? mission.que_hacer : mission.que_hacer_en || mission.que_hacer;
            const card = document.createElement('div');
            card.className = 'salida-option-card';
            card.innerHTML = `
                <h3 class="salida-option-title">${missionTitle}</h3>
                <p class="salida-option-desc">${missionWhatToDo}</p>
                <button class="btn-select-salida">${this.idiomaActual === 'es' ? 'Activar Guía' : 'Activate Guide'}</button>
            `;
            card.querySelector('.btn-select-salida').onclick = () => this.iniciarSalidaConcreta(mission);
            optionsGrid.appendChild(card);
        });

        this.hablar(t.chooseOne);
    },

    iniciarSalidaConcreta(selectedMission) {
        this.datosLugarGlobal = selectedMission;
        clearInterval(this.timerEnfocado);
        clearInterval(this.salidaTimerId);
        window.speechSynthesis.cancel();

        const t = {
            es: { listen: "ESCUCHA MI GUÍA", launch: "ABRIR CANAL DE ACCIÓN" },
            en: { listen: "LISTEN TO THE GUIDE", launch: "OPEN ACTION CHANNEL" }
        }[this.idiomaActual];

        const container = document.getElementById('wrapper-interactive');
        let textoFormateado = (this.idiomaActual === 'es' ? this.datosLugarGlobal.destino_instruccion : this.datosLugarGlobal.destino_instruccion_en || this.datosLugarGlobal.destino_instruccion).replace(/\n/g, '<br>');
       
        container.innerHTML = `
        <div class="mision-card">
            <small>${this.idiomaActual === 'es' ? 'Acción de Campo' : 'Field Action'}</small>
            <h2>${this.idiomaActual === 'es' ? this.datosLugarGlobal.destino_titulo : this.datosLugarGlobal.destino_titulo_en || this.datosLugarGlobal.destino_titulo}</h2>
            <div class="instruccion-text">${textoFormateado}</div>
            <div id="salida-countdown-phrases" style="margin-top:20px; text-align:center; font-size:1.1rem; min-height:40px; color:var(--cyan-inhale); font-weight:bold; letter-spacing:0.5px;"></div>
            <button id="btn-countdown-salida" style="width:100%; background:#222; color:#aaa; padding:17px; font-weight:bold; margin-top:15px; border:none; text-transform:uppercase; border-radius:4px; font-size:0.9rem;" disabled>35s ${t.listen}</button>
            <button id="btn-gps-action" class="hidden" style="width:100%; background:var(--secondary); color:#fff; padding:17px; font-weight:bold; margin-top:15px; border:none; text-transform:uppercase; border-radius:4px; cursor:pointer; font-size:0.95rem; letter-spacing:0.5px;">${t.launch}</button>
        </div>`;

        let speechText = (this.idiomaActual === 'es' ? this.datosLugarGlobal.destino_titulo : this.datosLugarGlobal.destino_titulo_en || this.datosLugarGlobal.destino_titulo) + ". " + (this.idiomaActual === 'es' ? this.datosLugarGlobal.destino_instruccion : this.datosLugarGlobal.destino_instruccion_en || this.datosLugarGlobal.destino_instruccion);
        this.hablar(speechText);
       
        let retencion = 35;
        const btnCount = document.getElementById('btn-countdown-salida');
        const btnGps = document.getElementById('btn-gps-action');
        const phrasesDiv = document.getElementById('salida-countdown-phrases');
        const AUDIOS_SECUENCIALES_SALIR = this.idiomaActual === 'es' ? this.AUDIOS_SECUENCIALES_SALIR_ES : this.AUDIOS_SECUENCIALES_SALIR_EN;
        let phraseIndex = 0;

        this.salidaTimerId = setInterval(() => {
            if (retencion > 0) {
                retencion--;
                if (btnCount) btnCount.innerText = `${retencion}s ${t.listen}`;
                if (retencion === 0) {
                    retencion = -45;
                    if (btnCount) btnCount.innerText = `${Math.abs(retencion)}s...`;
                    if (phrasesDiv && AUDIOS_SECUENCIALES_SALIR[phraseIndex]) phrasesDiv.innerText = AUDIOS_SECUENCIALES_SALIR[phraseIndex];
                    this.hablar(AUDIOS_SECUENCIALES_SALIR[phraseIndex]);
                    phraseIndex++;
                }
            } else if (retencion < 0) {
                retencion++;
                if (btnCount) btnCount.innerText = `${Math.abs(retencion)}s...`;
                if ((Math.abs(retencion) % 10 === 0) && phraseIndex < AUDIOS_SECUENCIALES_SALIR.length && retencion !== 0) {
                    if (phrasesDiv) phrasesDiv.innerText = AUDIOS_SECUENCIALES_SALIR[phraseIndex];
                    this.hablar(AUDIOS_SECUENCIALES_SALIR[phraseIndex]);
                    phraseIndex++;
                }
                if (retencion === 0) {
                    clearInterval(this.salidaTimerId);
                    window.speechSynthesis.cancel();
                    if (btnCount) btnCount.style.display = 'none';
                    if (phrasesDiv) phrasesDiv.innerText = "";
                    if (btnGps) {
                        btnGps.classList.remove('hidden');
                        btnGps.onclick = () => {
                            try {
                                let perfil = KERNEL.obtenerPerfilLocal();
                                const selectedVector = KERNEL.datosLugarGlobal.vector_entorno_seleccionado;
                               
                                for (const need in selectedVector) {
                                    if (perfil[need] !== undefined) {
                                        if (need === "prision_mental" || need === "agotamiento_mental" || need === "ansiedad") {
                                            perfil[need] = Math.max(0, perfil[need] + selectedVector[need]); // Sumar valores negativos para reducir indicador
                                        } else {
                                            perfil[need] = Math.min(perfil[need] + (selectedVector[need] * 0.1), 100);
                                        }
                                    }
                                }
                                localStorage.setItem("mib_perfil_dinamico", JSON.stringify(perfil));
                            } catch (e) {
                                console.error("Error al actualizar perfil local después de acción:", e);
                            }
                            window.open(this.datosLugarGlobal.destino_coordenadas_gps, '_blank');
                        };
                    }
                }
            }
        }, 1000);
    },

    procesarFlujoSecuencial(container) {
        clearInterval(this.timerEnfocado);
        window.speechSynthesis.cancel();

        const t = {
            es: { inspira: "Inhala ahora", expira: "Exhala ahora", fin: "Protocolo completado. Borrando rastro.", listen: "ESCUCHA MI GUÍA", launch: "ABRIR CANAL EXTERNO YA", fieldAction: "Acción de Campo", internalMission: "Misión Interna", doItNow: "ACTIVAR", suggestedEscape: "Acción sugerida" },
            en: { inspira: "Inhale now", expira: "Exhale now", fin: "Protocol completed. Clearing tracks.", listen: "LISTEN TO THE GUIDE", launch: "OPEN EXTERNAL CHANNEL NOW", fieldAction: "Field Action", internalMission: "Internal Mission", doItNow: "ACTIVATE", suggestedEscape: "Suggested Action" }
        }[this.idiomaActual];

        if (this.indiceMision >= this.pasosMisiones.length) {
            this.iniciarRelojEnfocadoCasa(container, t);
            return;
        }

        const paso = this.pasosMisiones[this.indiceMision];
       
        container.innerHTML = `
        <div class="mision-card">
            <small>${t.internalMission}</small>
            <h3>${paso.titulo}</h3>
            <p>${paso.descripcion}</p>
            <button id="btn-next" style="width:100%; background:var(--green-action); color:#fff; padding:16px; font-weight:bold; text-transform:uppercase; border-radius:6px; cursor:pointer; border:none; margin-top:15px; font-size:0.95rem;">${t.doItNow}</button>
        </div>`;

        this.hablar(paso.titulo + " . " + paso.descripcion);
        document.getElementById('btn-next').onclick = () => {
            try {
                let perfil = this.obtenerPerfilLocal();
                const missionVector = paso.vector_necesidades || this.DEFAULT_NECESSITY_PROFILE;
                for (const need in missionVector) {
                    if (perfil[need] !== undefined) {
                        if (need === "prision_mental" || need === "agotamiento_mental" || need === "ansiedad") {
                            perfil[need] = Math.max(0, perfil[need] + (missionVector[need] || 0)); // Sumar valores negativos para reducir
                        } else {
                            perfil[need] = Math.min(perfil[need] + (missionVector[need] * 0.05), 100);
                        }
                    }
                }
                localStorage.setItem("mib_perfil_dinamico", JSON.stringify(perfil));
            } catch (e) {
                console.error("Error al actualizar perfil local después de misión CASA:", e);
            }
            this.avanzarPaso();
        };
    },

    iniciarRelojEnfocadoCasa(container, t) {
        clearInterval(this.timerEnfocado);
        window.speechSynthesis.cancel();
       
        let msg = this.idiomaActual === 'es' ? "Iniciamos diez minutos de limpieza mental profunda. Enfócate en tu respiración." : "Starting ten minutes of deep mental clearing. Focus on your breath.";
        this.hablar(msg);
       
        container.innerHTML = `
        <div style="text-align:center; width:100%;">
            <div id="breath-circle" style="cursor:pointer;" title="${this.idiomaActual === 'es' ? 'Toca para enfocar tu mente' : 'Tap to focus your mind'}"></div>
            <div id="timer">10:00</div>
            <p id="txt-pulmon">INHALA / INHALE</p>
            <div id="salida-sugerida" class="hidden" style="margin-top: 30px; padding: 15px; border: 1px dashed #444; border-radius: 8px; font-size: 0.9rem; color: #888;">
                <p style="margin:0;">${t.suggestedEscape}: <a href="#" id="link-salida-sugerida" style="color: var(--accent); text-decoration: none; font-weight: bold;">Cargando...</a></p>
            </div>
        </div>`;

        this.timeLeft = 600;
        this.contadorToques = 0;

        const circleElement = document.getElementById('breath-circle');
        const timerDiv = document.getElementById('timer');
        const pulmonDiv = document.getElementById('txt-pulmon');
        const salidaSugeridaDiv = document.getElementById('salida-sugerida');
        const linkSalidaSugerida = document.getElementById('link-salida-sugerida');

        const AUDIOS_SECUENCIALES_CASA = this.idiomaActual === 'es' ? this.AUDIOS_SECUENCIALES_CASA_ES : this.AUDIOS_SECUENCIALES_CASA_EN;

        if (circleElement) {
            circleElement.onclick = () => {
                if (this.contadorToques < this.secuenciaAdelantos.length) {
                    let adelantoSegundos = this.secuenciaAdelantos[this.contadorToques];
                    this.timeLeft = Math.max(this.timeLeft - adelantoSegundos, 0);
                    this.contadorToques++;
                    try {
                        let perfil = this.obtenerPerfilLocal();
                        perfil["ansiedad"] = Math.min((perfil["ansiedad"] || 0) + 5, 100); // Tocar mucho eleva la ansiedad
                        localStorage.setItem("mib_perfil_dinamico", JSON.stringify(perfil));
                    } catch (e) {
                        console.error("Error al actualizar indicador de ansiedad:", e);
                    }
                    let m = Math.floor(this.timeLeft / 60);
                    let s = this.timeLeft % 60;
                    if (timerDiv) {
                        timerDiv.innerText = `${m}:${s.toString().padStart(2, '0')}`;
                    }
                }
            };
        }

        if (this.salidaSugeridaTimeoutId) {
            clearTimeout(this.salidaSugeridaTimeoutId);
            this.salidaSugeridaTimeoutId = null;
        }

        this.salidaSugeridaTimeoutId = setTimeout(async () => {
            try {
                const r = await fetch("/api/mando-integral", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        modo: "SALIR",
                        lang: this.idiomaActual,
                        mente: "agotado", // Asume que si pide sugerencia, está agotado
                        budget: "0",
                        perfil: document.getElementById('perfil-selector') ? document.getElementById('perfil-selector').value : "veterano_guerra",
                        desahogo: "",
                        zip: document.getElementById('inp-zip') ? document.getElementById('inp-zip').value.trim() : "",
                        perfil_local: this.obtenerPerfilLocal(),
                        historial_salir: this.historialSalir
                    })
                });
                const data = await r.json();
               
                if (data.DIRECCIONAMIENTO_MASTER === "ACCION_CAMPO" && data.misiones && data.misiones.length > 0 && linkSalidaSugerida && salidaSugeridaDiv) {
                    const suggestedMission = data.misiones[0];
                    if (data.historial_salir_actualizado) {
                        this.historialSalir = data.historial_salir_actualizado;
                        localStorage.setItem("mib_historial_salir", JSON.stringify(this.historialSalir));
                    }

                    linkSalidaSugerida.innerText = suggestedMission.destino_titulo;
                    linkSalidaSugerida.href = suggestedMission.destino_coordenadas_gps;
                    salidaSugeridaDiv.classList.remove('hidden');
                    this.hablar(this.idiomaActual === 'es' ? `Considera también esta acción sugerida: ${suggestedMission.destino_titulo}` : `Also consider this suggested action: ${suggestedMission.destino_titulo_en || suggestedMission.destino_titulo}`);
                }
            } catch (e) {
                console.error("Error al obtener sugerencia SALIR en modo CASA:", e);
            } finally {
                this.salidaSugeridaTimeoutId = null;
            }
        }, 180000); // 3 minutos para sugerir una misión SALIR

        this.timerEnfocado = setInterval(() => {
            if (this.timeLeft > 0) this.timeLeft--;

            let m = Math.floor(this.timeLeft / 60);
            let s = this.timeLeft % 60;
            if (timerDiv) timerDiv.innerText = `${m}:${s.toString().padStart(2, '0')}`;
           
            if (pulmonDiv) {
                let ciclo = this.timeLeft % 8;
                if (ciclo >= 4) {
                    pulmonDiv.innerText = t.inspira.toUpperCase();
                    pulmonDiv.style.color = "var(--cyan-inhale)";
                } else {
                    pulmonDiv.innerText = t.expira.toUpperCase();
                    pulmonDiv.style.color = "var(--accent)";
                }
            }

            if (this.timeLeft < 600 && (600 - this.timeLeft) % 20 === 0 && (600 - this.timeLeft) !== 0) {
                let pasoAudioIdx = Math.floor((600 - this.timeLeft) / 20) - 1;
                if (pasoAudioIdx >= 0 && pasoAudioIdx < AUDIOS_SECUENCIALES_CASA.length) {
                    let recordatorioTexto = AUDIOS_SECUENCIALES_CASA[pasoAudioIdx];
                    if (recordatorioTexto) {
                        this.hablar(recordatorioTexto);
                    }
                }
            }

            if (this.timeLeft <= 0) {
                clearInterval(this.timerEnfocado);
                clearTimeout(this.salidaSugeridaTimeoutId);
                this.salidaSugeridaTimeoutId = null;
                window.speechSynthesis.cancel();
                if (circleElement) {
                    circleElement.style.animation = "none";
                    circleElement.style.transform = "scale(1)";
                }
                this.iniciarRetoCierre60Segundos();
            }
        }, 1000);
    },

    avanzarPaso() {
        this.indiceMision++;
        const container = document.getElementById('wrapper-interactive');
        this.procesarFlujoSecuencial(container);
    },

    iniciarRetoCierre60Segundos() {
        clearInterval(this.timerEnfocado);
        clearInterval(this.temporizadorCierre);
        window.speechSynthesis.cancel();

        const t = {
            es: { logo: "MANDO INTEGRAL", cierreMensaje: "Gracias por tu presencia.", recomenzar: "REINICIAR SESIÓN", puertaAbierta: "La puerta está abierta. ¿Continuamos?", retoInicial: "Prepárate para un micro-reto de reconexión en 3, 2, 1..." },
            en: { logo: "INTEGRAL COMMAND", cierreMensaje: "Thank you for your presence.", recomenzar: "RESTART SESSION", puertaAbierta: "The door is open. Shall we continue?", retoInicial: "Get ready for a micro-reconnection challenge in 3, 2, 1..." }
        }[this.idiomaActual];

        const container = document.getElementById('wrapper-interactive');
        const cierrePantalla = document.getElementById('pantalla-cierre');
        const retoTitulo = document.getElementById('reto-titulo');
        const retoDescripcion = document.getElementById('reto-descripcion');
        const retoImg = document.getElementById('reto-img');
        const cierreTimer = document.getElementById('cierre-timer');
        const btnRecomenzar = document.getElementById('btn-recomenzar-experiencia');
        const cierreMensajeFinal = document.getElementById('cierre-mensaje-final');

        container.classList.add('hidden');
        cierrePantalla.classList.remove('hidden');
       
        cierreMensajeFinal.classList.add('hidden');
        btnRecomenzar.classList.add('hidden');
        btnRecomenzar.disabled = true;

        this.timeLeftCierre = 60;

        const catalogoRetos = this.idiomaActual === 'es' ? this.CATALOGO_RETOS_ES : this.CATALOGO_RETOS_EN;
       
        let secuenciaRetos = [];
        let numRetos = 3;
       
        let candidateSequenceIds;
        let sequenceString;
        let maxAttempts = 10;

        while(maxAttempts > 0) {
            secuenciaRetos = [];
            let tempRetos = [...catalogoRetos];
            for (let i = tempRetos.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [tempRetos[i], tempRetos[j]] = [tempRetos[j], tempRetos[i]];
            }

            for (let i = 0; i < numRetos; i++) {
                if (tempRetos.length === 0) break;
                secuenciaRetos.push(tempRetos.shift());
            }
           
            candidateSequenceIds = secuenciaRetos.map(r => r.id).sort((a, b) => a - b).join('-');
           
            if (!this.historialRetosSecuencias.includes(candidateSequenceIds)) {
                sequenceString = candidateSequenceIds;
                break;
            }
            maxAttempts--;
            if (maxAttempts === 0) {
                console.warn("No se pudo encontrar una secuencia de retos única después de múltiples intentos, reutilizando una.");
                sequenceString = candidateSequenceIds;
            }
        }
       
        if (sequenceString) {
            this.historialRetosSecuencias.push(sequenceString);
            this.historialRetosSecuencias = this.historialRetosSecuencias.slice(-this.MAX_HISTORY_RETOS_SECUENCIAS);
            localStorage.setItem("mib_historial_retos_secuencias", JSON.stringify(this.historialRetosSecuencias));
        }

        let currentRetoIndex = 0;
        const displayNextReto = () => {
            if (currentRetoIndex < secuenciaRetos.length) {
                const reto = secuenciaRetos[currentRetoIndex];
                if (retoTitulo) {
                    retoTitulo.innerText = reto.titulo;
                    retoTitulo.classList.remove('hidden');
                }
                if (retoDescripcion) {
                    retoDescripcion.innerText = reto.descripcion;
                    retoDescripcion.classList.remove('hidden');
                }
                if (retoImg) {
                    retoImg.src = `/static/${reto.img}`;
                    retoImg.classList.remove('hidden');
                }
                this.hablar(reto.descripcion);
                currentRetoIndex++;
            }
        };
        if (retoTitulo) retoTitulo.classList.add('hidden');
        if (retoDescripcion) retoDescripcion.classList.add('hidden');
        if (retoImg) retoImg.classList.add('hidden');

        this.hablar(t.retoInicial);
        setTimeout(() => {
            displayNextReto();
            this.temporizadorCierre = setInterval(() => {
                this.timeLeftCierre--;
                if (cierreTimer) cierreTimer.innerText = this.timeLeftCierre.toString().padStart(2, '0');

                if (this.timeLeftCierre > 0 && currentRetoIndex < numRetos && (this.timeLeftCierre % Math.floor(60 / numRetos) === 0)) {
                    if (retoTitulo) retoTitulo.classList.add('hidden');
                    if (retoDescripcion) retoDescripcion.classList.add('hidden');
                    if (retoImg) retoImg.classList.add('hidden');
                    displayNextReto();
                }

                if (this.timeLeftCierre <= 0) {
                    clearInterval(this.temporizadorCierre);
                    window.speechSynthesis.cancel();
                    if (retoTitulo) retoTitulo.innerText = "";
                    if (retoDescripcion) retoDescripcion.innerText = "";
                    if (retoImg) retoImg.src = "";
                   
                    cierreTimer.classList.add('hidden');
                    cierreMensajeFinal.classList.remove('hidden');
                    btnRecomenzar.classList.remove('hidden');
                    btnRecomenzar.disabled = false;
                    this.hablar(t.puertaAbierta);
                }
            }, 1000);
        }, 5000);

        btnRecomenzar.onclick = () => {
            this.reiniciarExperiencia();
        };
    },

    reiniciarExperiencia() {
        clearInterval(this.timerInaccion);
        clearInterval(this.timerEnfocado);
        clearInterval(this.temporizadorCascada);
        clearInterval(this.temporizadorCierre);
        clearInterval(this.salidaTimerId);
        window.speechSynthesis.cancel();
        if (this.salidaSugeridaTimeoutId) {
            clearTimeout(this.salidaSugeridaTimeoutId);
            this.salidaSugeridaTimeoutId = null;
        }

        this.pasosMisiones = [];
        this.indiceMision = 0;
        this.isLocked = false;
        this.contadorToques = 0;
        this.datosLugarGlobal = null;

        document.getElementById('pantalla-cierre').classList.add('hidden');
        document.getElementById('wrapper-interactive').classList.add('hidden');
        document.getElementById('wrapper-form').classList.remove('hidden');
       
        document.getElementById('inp-text-libre').value = "";
        this.inyectarBloquePreguntas();
        this.activarBotonMandoLibreInicial();
       
        const saludos_es = ["Bienvenido de nuevo. Tu espacio seguro. Escucha mis preguntas en pantalla.", "Mando Integral activo. Toca lo que sientes hoy para continuar."];
        const saludos_en = ["Welcome back. Your safe space. Listen to my questions on screen.", "Integral Command active. Tap what you feel today to continue."];
        const saludos = this.idiomaActual === 'es' ? saludos_es : saludos_en;
        this.hablar(saludos[Math.floor(Math.random() * saludos.length)]);
    },

    mostrarReporteBienestar() {
        const perfil = this.obtenerPerfilLocal();
        const t = {
            es: { title: "Reporte de Bienestar Personal", close: "Cerrar", save: "Guardar Reporte", intro: "Este es un reflejo de tus necesidades y estados internos actuales, basado en tu interacción con el sistema. Úsalo como una guía para tu autoconocimiento, sin valor médico o psicológico.",
                necesidades: "Necesidades Clave:", indicadores: "Indicadores de Estado:",
                nivel: "Nivel", bajo: "Bajo (necesita atención)", medio: "Medio (equilibrio)", alto: "Alto (satisfecho)",
                ansiedad_alta: "Indica una posible sobrecarga o tensión interna. Busca momentos de calma y atención plena.",
                ansiedad_media: "Muestra cierta inquietud. Enfócate en actividades que promuevan la relajación.",
                ansiedad_baja: "Estado de calma y equilibrio. Continúa fortaleciendo tu paz interior.",
                agotamiento_alta: "Sugerencia de fatiga mental profunda. Prioriza el descanso, el silencio y la desconexión total.",
                agotamiento_media: "Presencia de cansancio mental. Busca pausas activas y momentos de renovación.",
                agotamiento_baja: "Mente clara y con energía. Mantén hábitos que preserven tu vitalidad.",
                prision_alta: "Sensación de encierro mental o monotonía. Explora nuevas perspectivas y cambios en tu rutina.",
                prision_media: "Muestra cierta rigidez mental. Busca la creatividad y la exploración de nuevas ideas.",
                prision_baja: "Mente abierta y adaptable. Mantén la curiosidad y la capacidad de asombro.",
                carga_alta: "Indica un gran peso de responsabilidades. Prioriza la organización y delega si es posible. Busca micro-logros.",
                carga_media: "Nivel manejable de responsabilidades. Gestiona tus tareas con pausas activas.",
                carga_baja: "Carga de trabajo equilibrada. Disfruta de la ligereza de tus días.",
                soledad_alta: "Sugerencia de profundo aislamiento emocional. Busca conexión genuina o actividades en comunidad, incluso pasivas.",
                soledad_media: "Cierta distancia social. Activa pequeñas interacciones o momentos de comunidad.",
                soledad_baja: "Conexión social equilibrada. Fortalece tus lazos y comparte.",
            },
            en: { title: "Personal Well-being Report", close: "Close", save: "Save Report", intro: "This is a reflection of your current needs and internal states, based on your interaction with the system. Use it as a guide for self-awareness, with no medical or psychological value.",
                necesidades: "Key Needs:", indicadores: "State Indicators:",
                nivel: "Level", bajo: "Low (needs attention)", medio: "Medium (balance)", alto: "High (satisfied)",
                ansiedad_alta: "Indicates potential overload or internal tension. Seek moments of calm and mindfulness.",
                ansiedad_media: "Shows some restlessness. Focus on activities that promote relaxation.",
                ansiedad_baja: "State of calm and balance. Continue strengthening your inner peace.",
                agotamiento_alta: "Suggestion of deep mental fatigue. Prioritize rest, silence, and total disconnection.",
                agotamiento_media: "Presence of mental tiredness. Seek active breaks and moments of renewal.",
                agotamiento_baja: "Clear and energetic mind. Maintain habits that preserve your vitality.",
                prision_alta: "Feeling of mental confinement or monotony. Explore new perspectives and changes in your routine.",
                prision_media: "Shows some mental rigidity. Seek creativity and exploration of new ideas.",
                prision_baja: "Open and adaptable mind. Maintain curiosity and sense of wonder.",
                carga_alta: "Indicates a heavy weight of responsibilities. Prioritize organization and delegate if possible. Seek micro-achievements.",
                carga_media: "Manageable level of responsibilities. Manage your tasks with active breaks.",
                carga_baja: "Balanced workload. Enjoy the lightness of your days.",
                soledad_alta: "Suggestion of deep emotional isolation. Seek genuine connection or community activities, even passive ones.",
                soledad_media: "Some social distance. Activate small interactions or community moments.",
                soledad_baja: "Balanced social connection. Strengthen your bonds and share.",
            }
        }[this.idiomaActual];

        let reportContent = `<div class="report-modal">`;
        reportContent += `<h3>${t.title}</h3>`;
        reportContent += `<p class="report-intro">${t.intro}</p>`;
        reportContent += `<p class="report-date">${t.fecha}: ${perfil.fecha}</p>`;
       
        reportContent += `<div class="report-section"><h4>${t.necesidades}</h4>`;
        for (const key in perfil) {
            if (perfil.hasOwnProperty(key) && !(key in {"prision_mental":0, "agotamiento_mental":0, "ansiedad":0, "fecha":0, "timestamp":0})) {
                let value = perfil[key];
                let level = "";
                if (value <= 30) level = ` (${t.bajo})`;
                else if (value <= 70) level = ` (${t.medio})`;
                else level = ` (${t.alto})`;
                reportContent += `<p class="report-item">${key.replace(/_/g, ' ').toUpperCase()}: <strong>${value.toFixed(1)}</strong>${level}</p>`;
            }
        }
        reportContent += `</div>`;

        reportContent += `<div class="report-section"><h4>${t.indicadores}</h4>`;
        const indicators = ["ansiedad", "agotamiento_mental", "prision_mental", "carga_trabajo", "soledad"];
        indicators.forEach(indicator => {
            let value = perfil[indicator];
            let description = "";
            let level = "";

            if (indicator === "ansiedad") {
                if (value >= 70) { level = ` (${t.alto})`; description = t.ansiedad_alta; }
                else if (value >= 40) { level = ` (${t.medio})`; description = t.ansiedad_media; }
                else { level = ` (${t.baja})`; description = t.ansiedad_baja; }
            } else if (indicator === "agotamiento_mental") {
                if (value >= 70) { level = ` (${t.alto})`; description = t.agotamiento_alta; }
                else if (value >= 40) { level = ` (${t.medio})`; description = t.agotamiento_media; }
                else { level = ` (${t.baja})`; description = t.agotamiento_baja; }
            } else if (indicator === "prision_mental") {
                if (value >= 70) { level = ` (${t.alto})`; description = t.prision_alta; }
                else if (value >= 40) { level = ` (${t.medio})`; description = t.prision_media; }
                else { level = ` (${t.baja})`; description = t.prision_baja; }
            } else if (indicator === "carga_trabajo") {
                if (value >= 70) { level = ` (${t.alto})`; description = t.carga_alta; }
                else if (value >= 40) { level = ` (${t.medio})`; description = t.carga_media; }
                else { level = ` (${t.baja})`; description = t.carga_baja; }
            } else if (indicator === "soledad") {
                if (value >= 70) { level = ` (${t.alto})`; description = t.soledad_alta; }
                else if (value >= 40) { level = ` (${t.medio})`; description = t.soledad_media; }
                else { level = ` (${t.baja})`; description = t.soledad_baja; }
            }
            reportContent += `<p class="report-item">${indicator.replace(/_/g, ' ').toUpperCase()}: <strong>${value.toFixed(1)}</strong>${level}<br><small>${description}</small></p>`;
        });
        reportContent += `</div>`;

        reportContent += `<div class="report-actions">
            <button class="report-btn" onclick="KERNEL.descargarReporte()">${t.save}</button>
            <button class="report-btn" onclick="this.closest('.report-modal').remove()">${t.close}</button>
        </div>`;
        reportContent += `</div>`;

        let overlay = document.createElement('div');
        overlay.id = 'report-overlay';
        overlay.innerHTML = reportContent;
        document.body.appendChild(overlay);
        this.hablar(t.title);
    },

    descargarReporte() {
        const perfil = this.obtenerPerfilLocal();
        const t = {
            es: { title: "Reporte de Bienestar Personal", intro: "Este es un reflejo de tus necesidades y estados internos actuales, basado en tu interacción con el sistema. Úsalo como una guía para tu autoconocimiento, sin valor médico o psicológico.",
                necesidades: "Necesidades Clave:", indicadores: "Indicadores de Estado:",
                nivel: "Nivel", bajo: "Bajo (necesita atención)", medio: "Medio (equilibrio)", alto: "Alto (satisfecho)",
                ansiedad_alta: "Indica una posible sobrecarga o tensión interna. Busca momentos de calma y atención plena.",
                ansiedad_media: "Muestra cierta inquietud. Enfócate en actividades que promuevan la relajación.",
                ansiedad_baja: "Estado de calma y equilibrio. Continúa fortaleciendo tu paz interior.",
                agotamiento_alta: "Sugerencia de fatiga mental profunda. Prioriza el descanso, el silencio y la desconexión total.",
                agotamiento_media: "Presencia de cansancio mental. Busca pausas activas y momentos de renovación.",
                agotamiento_baja: "Mente clara y con energía. Mantén hábitos que preserven tu vitalidad.",
                prision_alta: "Sensación de encierro mental o monotonía. Explora nuevas perspectivas y cambios en tu rutina.",
                prision_media: "Muestra cierta rigidez mental. Busca la creatividad y la exploración de nuevas ideas.",
                prision_baja: "Mente abierta y adaptable. Mantén la curiosidad y la capacidad de asombro.",
                carga_alta: "Indica un gran peso de responsabilidades. Prioriza la organización y delega si es posible. Busca micro-logros.",
                carga_media: "Nivel manejable de responsabilidades. Gestiona tus tareas con pausas activas.",
                carga_baja: "Carga de trabajo equilibrada. Disfruta de la ligereza de tus días.",
                soledad_alta: "Sugerencia de profundo aislamiento emocional. Busca conexión genuina o actividades en comunidad, incluso pasivas.",
                soledad_media: "Cierta distancia social. Activa pequeñas interacciones o momentos de comunidad.",
                soledad_baja: "Conexión social equilibrada. Fortalece tus lazos y comparte.",
            }
        }[this.idiomaActual];

        let content = `${t.title}\n`;
        content += `${t.intro}\n`;
        content += `Fecha del reporte: ${perfil.fecha}\n\n`;
       
        content += `${t.necesidades}\n`;
        for (const key in perfil) {
            if (perfil.hasOwnProperty(key) && !(key in {"prision_mental":0, "agotamiento_mental":0, "ansiedad":0, "fecha":0, "timestamp":0})) {
                let value = perfil[key];
                let level = "";
                if (value <= 30) level = ` (${t.bajo})`;
                else if (value <= 70) level = ` (${t.medio})`;
                else level = ` (${t.alto})`;
                content += `- ${key.replace(/_/g, ' ').toUpperCase()}: ${value.toFixed(1)}${level}\n`;
            }
        }
        content += `\n`;

        content += `${t.indicadores}\n`;
        const indicators = ["ansiedad", "agotamiento_mental", "prision_mental", "carga_trabajo", "soledad"];
        indicators.forEach(indicator => {
            let value = perfil[indicator];
            let description = "";
            let level = "";

            if (indicator === "ansiedad") {
                if (value >= 70) { level = ` (${t.alto})`; description = t.ansiedad_alta; }
                else if (value >= 40) { level = ` (${t.medio})`; description = t.ansiedad_media; }
                else { level = ` (${t.baja})`; description = t.ansiedad_baja; }
            } else if (indicator === "agotamiento_mental") {
                if (value >= 70) { level = ` (${t.alto})`; description = t.agotamiento_alta; }
                else if (value >= 40) { level = ` (${t.medio})`; description = t.agotamiento_media; }
                else { level = ` (${t.baja})`; description = t.agotamiento_baja; }
            } else if (indicator === "prision_mental") {
                if (value >= 70) { level = ` (${t.alto})`; description = t.prision_alta; }
                else if (value >= 40) { level = ` (${t.medio})`; description = t.prision_media; }
                else { level = ` (${t.baja})`; description = t.prision_baja; }
            } else if (indicator === "carga_trabajo") {
                if (value >= 70) { level = ` (${t.alto})`; description = t.carga_alta; }
                else if (value >= 40) { level = ` (${t.medio})`; description = t.carga_media; }
                else { level = ` (${t.baja})`; description = t.carga_baja; }
            } else if (indicator === "soledad") {
                if (value >= 70) { level = ` (${t.alto})`; description = t.soledad_alta; }
                else if (value >= 40) { level = ` (${t.medio})`; description = t.soledad_media; }
                else { level = ` (${t.baja})`; description = t.soledad_baja; }
            }
            content += `- ${indicator.replace(/_/g, ' ').toUpperCase()}: ${value.toFixed(1)}${level}\n  Descripción: ${description}\n`;
        });
        content += `\n--- Fin del Reporte ---`;

        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Reporte_Bienestar_${perfil.fecha}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    },

    destruirYReiniciar() {
        clearInterval(this.timerInaccion);
        clearInterval(this.timerEnfocado);
        clearInterval(this.temporizadorCascada);
        clearInterval(this.temporizadorCierre);
        clearInterval(this.salidaTimerId);
        window.speechSynthesis.cancel();
        if (this.salidaSugeridaTimeoutId) {
            clearTimeout(this.salidaSugeridaTimeoutId);
            this.salidaSugeridaTimeoutId = null;
        }

        localStorage.clear();

        this.historialSalir = [];
        this.historialCasa = [];
        this.historialPreguntas = [];
        this.historialRetosSecuencias = [];
        this.pasosMisiones = [];
        this.indiceMision = 0;
        this.isLocked = false;
        this.contadorToques = 0;
        this.datosLugarGlobal = null;

        location.reload();
    }
};

document.addEventListener('DOMContentLoaded', () => KERNEL.init());

window.KERNEL = KERNEL;
