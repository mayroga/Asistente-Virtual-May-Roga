// CORE SOMATIC WELLNESS SYSTEM - Governmental Homeostasis Module V.1.0.0
// Company: Gobierno Federal / Government Agency
// File: static/engine.js (Frontend Logic)

const KERNEL = {
    timerInaccion: null,
    timerEnfocado: null,
    temporizadorCascada: null,
    temporizadorCierre: null,
    salidaSugeridaTimeoutId: null,
    salidaTimerId: null,
    speechQueue: [],
    isSpeaking: false,
    carouselInterval: null,
   
    historialFaseCasaSublime: {},
    historialAudiosCasaSecuenciales: {},
    historialAudiosSalirSecuenciales: {},
    MAX_HISTORY_FASE_CASA_SUBLIME: 28,
    MAX_HISTORY_AUDIOS_CASA_SECUENCIALES: 29,
    MAX_HISTORY_AUDIOS_SALIR_SECUENCIALES: 10,
   
    "AUDIOS_FASE_CASA_SUBLIMES_ES": [
        "Veterano, siente la quietud del cuartel interior. Este es tu santuario. Permítete un descanso estratégico. Tu valía es innegable.",
        "Adulto mayor, cada respiro te ancla a una paz profunda. Estás a salvo. Confía en el presente. Tu serenidad es tu legado.",
        "Trabajador gubernamental, suelta las tensiones burocráticas. Deja ir todo lo que no te sirve en este instante. Libera la carga invisible.",
        "Tu mente es un mapa vasto. La calma es tu verdadera topografía. Siente tu calma operativa. Define tu bienestar.",
        "Imagina un paisaje de descompresión. Tu homeostasis interna está en perfecto equilibrio. Estabiliza tu sistema.",
        "La vida te sostiene con firmeza. Confía en el flujo natural. Todo está en orden ahora. Concéntrate en la ejecución de la paz.",
        "En este silencio, redescubre tu fuerza táctica. Eres resiliente. Siente tu capacidad de recuperación interna.",
        "La sabiduría reside en tu experiencia. Escúchala con atención plena. Tu intuición te guía con precisión.",
        "Permite que la luz de la claridad te envuelva. Eres un faro de integridad. Deja que te inunde. Brilla.",
        "Este es tu momento de regeneración profunda. Absórbelo plenamente. Permítete recargar tu energía vital.",
        "Observa tu respiración consciente. Es el anclaje de tu presencia inquebrantable. Siente tu base en la calma.",
        "El presente es tu informe más importante. Vive cada segundo con gratitud. Agradece cada detalle.",
        "Libera tu mente de protocolos innecesarios. El peso de lo externo se desvanece. Deja ir el ruido administrativo.",
        "Recibe esta energía renovadora con disciplina. Estás floreciendo. Florece en el presente, con propósito.",
        "La belleza reside en la simplicidad estratégica. Encuentra la paz aquí y ahora. Reconoce el valor de la calma.",
        "Eres un universo de posibilidades. Despierta tu potencial. Despierta la luz de tu servicio interior.",
        "Deja que la quietud te hable en código interno. Su mensaje es puro bienestar. Escucha su mensaje.",
        "Cada inhalación te nutre para la próxima misión. Cada exhalación te libera de ataduras. Libera el pasado.",
        "Tu espíritu se eleva con ligereza. Siente la libertad de ser. Vuela con tu esencia más pura.",
        "Este espacio es sagrado. Tu bienestar es la prioridad número uno. Prioriza tu homeostasis.",
        "La armonía te rodea como una formación perfecta. Permite que te llene por completo. Llénate de equilibrio.",
        "Eres digno de esta paz ganada. Acéptala sin reservas. Acepta esta calma profunda.",
        "El tiempo se detiene para tu recuperación. Disfruta este oasis. Vive tu propio reloj biológico.",
        "La calma es tu poder táctico. Manifiéstate desde la serenidad. Usa tu autoridad interior.",
        "Con cada pulso, la vida te susurra esperanza. Escucha el mensaje. La esperanza te envuelve.",
        "Tu esencia es un mandato divino. Reconoce tu magnificencia. Reconoce tu brillo interior.",
        "Entrégate al momento presente. Es todo lo que realmente existe. Vive el aquí y el ahora.",
        "Aquí y ahora, eres completo. Eres luz. Eres fuerza. Eres eterno en tu propósito."
    ],
    "AUDIOS_FASE_CASA_SUBLIMES_EN": [
        "Veteran, feel the stillness of your inner barracks. This is your sanctuary. Allow for a strategic rest. Your worth is undeniable.",
        "Senior, every breath anchors you to deep peace. You are safe. Trust in the present. Your serenity is your legacy.",
        "Government worker, release bureaucratic tensions. Let go of all that no longer serves you in this moment. Release the invisible burden.",
        "Your mind is a vast map. Calm is your true topography. Feel your operational calm. Define your well-being.",
        "Imagine a decompression landscape. Your internal homeostasis is in perfect balance. Stabilize your system.",
        "Life holds you firmly. Trust the natural flow. All is well now. Concentrate on the execution of peace.",
        "In this silence, rediscover your tactical strength. You are resilient. Feel your internal recovery capacity.",
        "Wisdom resides in your experience. Listen with full attention. Your intuition guides you with precision.",
        "Allow the light of clarity to envelop you. You are a beacon of integrity. Let it flood you. Shine bright.",
        "This is your moment of deep regeneration. Absorb it fully. Allow yourself to recharge your vital energy.",
        "Observe your conscious breath. It is the anchor of your unwavering presence. Feel your base in calm.",
        "The present is your most important report. Live each second with gratitude. Appreciate every detail.",
        "Free your mind from unnecessary protocols. The weight of the external fades away. Let go of administrative noise.",
        "Receive this renewing energy with discipline. You are flourishing. Flourish in the present, with purpose.",
        "Beauty resides in strategic simplicity. Find peace here and now. Recognize the value of calm.",
        "You are a universe of possibilities. Awaken your potential. Awaken the light of your inner service.",
        "Let stillness speak to you in internal code. Its message is pure well-being. Listen to its message.",
        "Each inhale nourishes you for the next mission. Each exhale liberates you from ties. Release the past.",
        "Your spirit soars with lightness. Feel the freedom of being. Fly with your purest essence.",
        "This space is sacred. Your well-being is the number one priority. Prioritize your homeostasis.",
        "Harmony surrounds you like a perfect formation. Allow it to fill you completely. Fill with balance.",
        "You are worthy of this earned peace. Accept it without reservation. Accept this deep calm.",
        "Time stops for your recovery. Enjoy this oasis. Live by your own biological clock.",
        "Calm is your tactical power. Manifest from serenity. Use your inner authority.",
        "With every pulse, life whispers hope. Listen to the message. Hope envelops you.",
        "Your essence is a divine mandate. Recognize your magnificence. Recognize your inner glow.",
        "Surrender to the present moment. It is all that truly exists. Live the here and now.",
        "Here and now, you are complete. You are light. You are strength. You are eternal in your purpose."
    ],

    "IMAGENES_CARRUSEL": {
        "hipervigilancia": [
            "static/images/hiper_1_forest_path.jpg", "static/images/hiper_2_calm_lake.jpg", "static/images/hiper_3_mountain_view.jpg",
            "static/images/hiper_4_sun_beach.jpg", "static/images/hiper_5_cozy_cottage.jpg", "static/images/hiper_6_misty_forest.jpg",
            "static/images/hiper_7_river_bend.jpg", "static/images/hiper_8_golden_hour_field.jpg", "static/images/hiper_9_peaceful_stream.jpg",
            "static/images/hiper_10_serene_garden.jpg", "static/images/hiper_11_autumn_woods.jpg", "static/images/hiper_12_sunlit_meadow.jpg",
            "static/images/hiper_13_winter_forest.jpg", "static/images/hiper_14_country_road.jpg", "static/images/hiper_15_spring_flowers.jpg",
            "static/images/hiper_16_ocean_sunset.jpg", "static/images/hiper_17_desert_oasis.jpg", "static/images/hiper_18_tropical_paradise.jpg",
            "static/images/hiper_19_snowy_mountains.jpg", "static/images/hiper_20_ancient_trees.jpg", "static/images/hiper_21_wild_flowers.jpg",
            "static/images/hiper_22_forest_cabin.jpg", "static/images/hiper_23_stone_bridge.jpg", "static/images/hiper_24_moonlit_lake.jpg"
        ],
        "aislamiento": [
            "static/images/ais_1_calm_forest.jpg", "static/images/ais_2_still_water.jpg", "static/images/ais_3_quiet_meadow.jpg",
            "static/images/ais_4_sunrise_mountains.jpg", "static/images/ais_5_peaceful_seaside.jpg", "static/images/ais_6_deep_woods.jpg",
            "static/images/ais_7_misty_river.jpg", "static/images/ais_8_sunset_hills.jpg", "static/images/ais_9_forest_brook.jpg",
            "static/images/ais_10_zen_garden.jpg", "static/images/ais_11_path_through_trees.jpg", "static/images/ais_12_flower_field.jpg",
            "static/images/ais_13_snowy_woods.jpg", "static/images/ais_14_winding_road.jpg", "static/images/ais_15_spring_forest.jpg",
            "static/images/ais_16_calm_ocean.jpg", "static/images/ais_17_desert_canyon.jpg", "static/images/ais_18_tropical_beach.jpg",
            "static/images/ais_19_mountain_lake.jpg", "static/images/ais_20_old_growth_forest.jpg", "static/images/ais_21_green_valley.jpg",
            "static/images/ais_22_log_cabin.jpg", "static/images/ais_23_stone_path.jpg", "static/images/ais_24_starry_night.jpg"
        ],
        "carga_invisible": [
            "static/images/carga_1_green_valley.jpg", "static/images/carga_2_open_sky.jpg", "static/images/carga_3_clear_river.jpg",
            "static/images/carga_4_calm_fields.jpg", "static/images/carga_5_tranquil_coast.jpg", "static/images/carga_6_sunlit_forest.jpg",
            "static/images/carga_7_peaceful_stream.jpg", "static/images/carga_8_golden_meadow.jpg", "static/images/carga_9_waterfall.jpg",
            "static/images/carga_10_open_countryside.jpg", "static/images/carga_11_bright_woods.jpg", "static/images/carga_12_lakeside_view.jpg",
            "static/images/carga_13_forest_clearing.jpg", "static/images/carga_14_path_in_nature.jpg", "static/images/carga_15_spring_hills.jpg",
            "static/images/carga_16_blue_ocean.jpg", "static/images/carga_17_desert_sunset.jpg", "static/images/carga_18_island_paradise.jpg",
            "static/images/carga_19_snowy_peaks.jpg", "static/images/carga_20_ancient_forest.jpg", "static/images/carga_21_rolling_hills.jpg",
            "static/images/carga_22_farm_house.jpg", "static/images/carga_23_rocky_shore.jpg", "static/images/carga_24_day_clouds.jpg"
        ],
        "saturacion_urbana": [
            "static/images/satur_1_serene_forest.jpg", "static/images/satur_2_calm_river.jpg", "static/images/satur_3_quiet_lake.jpg",
            "static/images/satur_4_sunset_beach.jpg", "static/images/satur_5_peaceful_cottage.jpg", "static/images/satur_6_deep_green_woods.jpg",
            "static/images/satur_7_flowing_stream.jpg", "static/images/satur_8_field_at_dusk.jpg", "static/images/satur_9_forest_clearing.jpg",
            "static/images/satur_10_zen_garden_path.jpg", "static/images/satur_11_autumn_path.jpg", "static/images/satur_12_sunlit_forest_floor.jpg",
            "static/images/satur_13_winter_lake.jpg", "static/images/satur_14_country_lane.jpg", "static/images/satur_15_spring_field.jpg",
            "static/images/satur_16_ocean_waves.jpg", "static/images/satur_17_desert_stars.jpg", "static/images/satur_18_tropical_lagoon.jpg",
            "static/images/satur_19_mountain_river.jpg", "static/images/satur_20_ancient_trees_mist.jpg", "static/images/satur_21_lush_valley.jpg",
            "static/images/satur_22_forest_house.jpg", "static/images/satur_23_stone_wall.jpg", "static/images/satur_24_moonlit_forest.jpg"
        ],
        "agotamiento": [
            "static/images/agot_1_ocean_horizon.jpg", "static/images/agot_2_vast_sky.jpg", "static/images/agot_3_calm_water.jpg",
            "static/images/agot_4_open_field.jpg", "static/images/agot_5_forest_clearing.jpg", "static/images/agot_6_mountain_vista.jpg",
            "static/images/agot_7_river_flow.jpg", "static/images/agot_8_peaceful_sunset.jpg", "static/images/agot_9_still_pond.jpg",
            "static/images/agot_10_expansive_beach.jpg", "static/images/agot_11_wide_valley.jpg", "static/images/agot_12_desert_landscape.jpg",
            "static/images/agot_13_clear_lake.jpg", "static/images/agot_14_open_forest.jpg", "static/images/agot_15_grassy_hills.jpg",
            "static/images/agot_16_blue_sea.jpg", "static/images/agot_17_canyon_view.jpg", "static/images/agot_18_tropical_islands.jpg",
            "static/images/agot_19_snowy_peaks.jpg", "static/images/agot_20_cloudy_sky.jpg", "static/images/agot_21_rolling_plains.jpg",
            "static/images/agot_22_countryside_home.jpg", "static/images/agot_23_forest_path_wide.jpg", "static/images/agot_24_bright_sky.jpg"
        ]
    },

    horaInicioSesionAbsoluta: null,
    timeLeft: 600, // 10 minutes (600 seconds) for core breathing phase, total 15 minutes session
    timeLeftCierre: 60,
    isLocked: false,
    idiomaActual: 'es',
    pasosMisiones: [],
    indiceMision: 0,
    datosLugarGlobal: null,
    tipoEscapeGlobal: "",
    contadorToques: 0,
    secuenciaAdelantos: [],
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

    _getDailyNonRepeatingAudio(pool, historyKey, maxSessions = 5) {
        const today = new Date().toISOString().split('T')[0];
        let historyData = JSON.parse(localStorage.getItem(historyKey) || "{}");

        if (!historyData.date || historyData.date !== today || !Array.isArray(historyData.sessions)) {
            historyData = { date: today, sessions: [] };
        }

        let currentSessionPhrases;
        if (historyData.sessions.length === 0 || historyData.sessions[historyData.sessions.length - 1].seed !== KERNEL.sessionSeed) {
            historyData.sessions.push({ seed: KERNEL.sessionSeed, phrases: [] });
        }
        let latestSession = historyData.sessions[historyData.sessions.length - 1];
        if (latestSession.seed !== KERNEL.sessionSeed) {
            historyData.sessions.push({ seed: KERNEL.sessionSeed, phrases: [] });
            latestSession = historyData.sessions[historyData.sessions.length - 1];
        }
        currentSessionPhrases = latestSession.phrases;

        let availableIndices = [];
        let allUsedIndicesToday = new Set();
        historyData.sessions.forEach(session => session.phrases.forEach(idx => allUsedIndicesToday.add(idx)));

        for (let i = 0; i < pool.length; i++) {
            if (!allUsedIndicesToday.has(i)) {
                availableIndices.push(i);
            }
        }

        if (availableIndices.length === 0) {
            historyData.sessions = [];
            historyData.sessions.push({ seed: KERNEL.sessionSeed, phrases: [] });
            latestSession = historyData.sessions[0];
            currentSessionPhrases = latestSession.phrases;
            availableIndices = Array.from({ length: pool.length }, (_, i) => i);
            console.warn(`Daily phrase pool for ${historyKey} exhausted. Resetting daily history.`);
        }

        const randomIndex = availableIndices[Math.floor(Math.random() * availableIndices.length)];
        currentSessionPhrases.push(randomIndex);

        if (historyData.sessions.length > maxSessions) {
            historyData.sessions.shift();
        }

        localStorage.setItem(historyKey, JSON.stringify(historyData));
        return pool[randomIndex];
    },

    activarSensorSegundoPlano() {
        document.addEventListener("visibilitychange", () => {
            if (document.visibilityState === "visible") {
                if (KERNEL.horaInicioSesionAbsoluta) {
                    let tiempoTranscurridoMs = Date.now() - KERNEL.horaInicioSesionAbsoluta;
                    let tiempoTranscurridoSegundos = Math.floor(tiempoTranscurridoMs / 1000);
                   
                    if (tiempoTranscurridoSegundos >= 900) {
                        if (typeof KERNEL.forzarCierre15MinutosEfectivo === 'function') {
                            KERNEL.forzarCierre15MinutosEfectivo();
                        }
                    }
                }
            }
        });
    },

    forzarCierre15MinutosEfectivo() {
        console.warn("Sesión forzada a cerrar después de 15 minutos de inactividad o segundo plano.");
        this.destruirYReiniciar();
    },

    DEFAULT_NECESSITY_PROFILE: {
        "movimiento": 50, "naturaleza": 50, "silencio": 50, "agua": 50, "sol": 50,
        "sombra": 50, "aire_fresco": 50, "creatividad": 50, "comunidad": 50, "aprendizaje": 50,
        "juego": 50, "contemplacion": 50, "descanso": 50, "organizacion": 50,
        "alimentacion": 50, "musica": 50, "risa": 50, "esperanza": 50,
        "indicador_ansiedad": 0
    },
   
    CATALOGO_PREGUNTAS_ES: [
        // Bloque 1: El Bucle del Servicio y la Rutina
        "¿Sientes que tu disciplina de servicio se ha vuelto una cadena, no una elección?",
        "¿La rutina institucional ha borrado tu capacidad de asombro por el mundo real?",
        "¿Usas la radio o la televisión para ahogar el ruido mental de tus responsabilidades?",
        "¿Te cuesta observar tu entorno sin buscar un 'objetivo' o una 'amenaza' potencial?",

        // Bloque 2: Reposo y Carga Física
        "¿Inviertes más tiempo en trámites que en tu bienestar físico, sintiendo que es un 'gasto'?",
        "¿Te refugias en la inactividad para huir de las exigencias del servicio, sin recargar realmente?",
        "¿Conduces sin rumbo, buscando solo una 'desconexión' que no llega a tu mente?",
        "¿Mantienes hábitos por lealtad a la rutina, aunque te drenen más de lo que te nutren?",
        "¿Tu cuerpo te pide movimiento estratégico, pero el sedentarismo burocrático te atrapa?",
        "¿Aplazas tu descanso por el peso de la 'carga invisible' de tus deberes?",

        // Bloque 3: Distanciamiento Social y Espacios Comunes
        "¿Buscas aglomeraciones para sentirte parte de algo, pero mantienes una distancia emocional?",
        "¿Compartes espacios con colegas, sintiendo a la vez un profundo aislamiento personal?",
        "¿Asistes a reuniones por protocolo, anhelando un repliegue a tu espacio personal?",
        "¿Necesitas estímulos externos para sobrellevar conversaciones monótonas de gestión?",
        "¿Aceptas la compañía, pero te escudas detrás de tu dispositivo móvil o tu uniforme?",
        "¿Proyectas una imagen de 'todo bajo control' para ocultar tu verdadero sentir?",

        // Bloque 4: La Familia y el Servicio (Impacto en el Hogar)
        "¿Existen roces por el impacto de tus horarios o turnos en la armonía familiar?",
        "¿Sientes desinterés o apatía ante reuniones familiares, prefiriendo la soledad?",
        "¿Compartes techo, pero la disciplina o el distanciamiento te hacen sentir como un extraño en casa?",
        "¿La visita de un familiar te genera 'alerta táctica' en vez de verdadera paz y conexión?",
        "¿La añoranza por los seres queridos, lejos por el servicio, te paraliza tu presente?",
        "¿Sientes que las interacciones diarias están creando silencios en tus relaciones familiares?",

        // Bloque 5: El Escape del Deber (Fugas y Realidades)
        "¿Subestimas la 'base de operaciones' de tu hogar, soñando con escapes lejanos inalcanzables?",
        "¿Deseas una 'desmovilización' total para que un cambio de escenario resuelva tus crisis internas?",
        "¿Crees que la solución a tu insatisfacción es un cambio radical de ubicación o asignación?",
        "¿Planeas grandes gastos en ocio que podrían comprometer tu 'reserva estratégica' futura?",
        "¿Buscas imágenes de paisajes distantes porque perdiste la capacidad de asombrarte con tu propio cielo?",
        "¿Te sientes atado a tu posición y asumes que la libertad requiere un 'pase' a otro sitio?",

        // Bloque 6: Vulnerabilidad Somática y Alerta Interna
        "¿Aplazas tu bienestar físico por el 'costo operativo' o las 'complicaciones burocráticas'?",
        "¿Sientes molestias en el cuerpo causadas por la 'hipervigilancia' y la tensión diaria?",
        "¿Sientes opresión en el pecho por la prisa del entorno y la incertidumbre del futuro institucional?",
        "¿Has olvidado el consuelo de una respiración profunda, libre de cualquier 'orden' o 'protocolo'?",

        // Bloque 7: El Vacío de la Gestión y la Identidad
        "¿Buscas la tranquilidad en un entorno natural, pero tu mente sigue en el bucle de los 'expedientes'?",
        "¿Tienes comodidades, pero una insatisfacción crónica te consume por dentro, como una 'misión sin fin'?",
        "¿Crees que la acumulación de 'rangos' o 'bienes' te dará un sentido de pertenencia o identidad real?",
        "¿Te paraliza la idea de dejar la 'seguridad' de lo conocido, por miedo a un paso incierto?",
        "¿Te comparas con la 'trayectoria' o las 'posesiones' de tus compañeros de servicio o civiles?",

        // Bloque 8: El Despertar del Mando Interno
        "¿Tu mente se convirtió en tu mayor 'cuartel de reclusión' en este momento?",
        "¿Quieres 'proteger' a tu familia, pero te paraliza no saber cómo empezar tu 'despliegue civil'?",
        "¿Estás cansado de repetir 'protocolos' que consumen tu libertad y energía vital?",
        "¿Sientes que estás perdiendo tus mejores años esperando una 'orden de liberación' que no llega?",
        "¿Te cuesta creer que exista un 'punto de reunión' gratuito capaz de devolverte la esperanza?",
        "¿Estás listo para obedecer al mando, soltar tus indecisiones y salir de tu 'encierro mental' hoy?"
    ],
    CATALOGO_PREGUNTAS_EN: [
        // Block 1: The Service Loop and Routine
        "Do you feel your service discipline has become a chain, not a choice?",
        "Has institutional routine erased your capacity for wonder at the real world?",
        "Do you use radio or TV to drown out the mental noise of your responsibilities?",
        "Is it hard for you to observe your surroundings without looking for a 'target' or a potential 'threat'?",

        // Block 2: Rest and Physical Burden
        "Do you spend more time on paperwork than on your physical well-being, feeling it's an 'expense'?",
        "Do you take refuge in inactivity to escape service demands, without truly recharging?",
        "Do you drive aimlessly, seeking only a 'disconnection' that doesn't reach your mind?",
        "Do you maintain habits out of loyalty to routine, even if they drain you more than they nourish you?",
        "Does your body crave strategic movement, but bureaucratic sedentary life traps you?",
        "Do you postpone your rest due to the 'invisible burden' of your duties?",

        // Block 3: Social Distancing and Common Spaces
        "Do you seek crowds to feel part of something, but maintain an emotional distance?",
        "Do you share spaces with colleagues, yet feel a deep personal isolation?",
        "Do you attend meetings by protocol, longing for a retreat to your personal space?",
        "Do you need external stimuli to endure monotonous management conversations?",
        "Do you accept company but shield yourself behind your mobile device or uniform?",
        "Do you project an image of 'everything under control' to hide your true feelings?",

        // Block 4: Family and Service (Impact at Home)
        "Are there constant frictions due to the impact of your schedules or shifts on family harmony?",
        "Do you feel disinterest or apathy towards family gatherings, preferring solitude?",
        "Do you share a roof, but discipline or distancing makes you feel like a stranger at home?",
        "Does a family visit generate 'tactical alert' instead of true peace and connection?",
        "Does longing for loved ones, far due to service, paralyze your present?",
        "Do you feel that daily interactions are creating silences in your family relationships?",

        // Block 5: The Escape from Duty (Fugues and Realities)
        "Do you underestimate your home 'base of operations', dreaming of unattainable distant escapes?",
        "Do you wish for a total 'demobilization' so a change of scenery resolves your internal crises?",
        "Do you believe that the solution to your dissatisfaction is a radical change of location or assignment?",
        "Do you plan large leisure expenses that could compromise your future 'strategic reserve'?",
        "Do you search for images of distant landscapes because you've lost the ability to be amazed by your own sky?",
        "Do you feel tied to your position and assume that freedom requires a 'pass' to another place?",

        // Block 6: Somatic Vulnerability and Internal Alert
        "Do you postpone your physical well-being for the 'operational cost' or 'bureaucratic complications'?",
        "Do you feel bodily discomfort caused by 'hypervigilance' and daily tension?",
        "Do you feel chest tightness from environmental rush and institutional future uncertainty?",
        "Have you forgotten the comfort of a deep breath, free from any 'order' or 'protocol'?",

        // Block 7: The Void of Management and Identity
        "Do you seek tranquility in a natural environment, but your mind remains in the 'files' loop?",
        "Do you have comforts but a chronic dissatisfaction consumes you within, like an 'endless mission'?",
        "Do you believe that accumulating 'ranks' or 'assets' will give you a sense of belonging or real identity?",
        "Does the idea of leaving the 'security' of the known paralyze you, for fear of an uncertain step?",
        "Do you secretly compare yourself to the 'trajectory' or 'possessions' of your service colleagues or civilians?",

        // Block 8: The Awakening of Inner Command
        "Has your mind become your biggest 'barracks of confinement' right now?",
        "Do you want to 'protect' your family but are paralyzed by not knowing how to start your 'civilian deployment'?",
        "Are you tired of repeating 'protocols' that consume your freedom and vital energy?",
        "Do you feel like you are losing your best years waiting for a 'release order' that won't come?",
        "Is it hard for you to believe there's a free 'gathering point' in your area capable of restoring your hope?",
        "Are you ready to obey the command, let go of your indecisions, and break free from your 'mental imprisonment' today?"
    ],

    "AUDIOS_SECUENCIALES_CASA_ES": [
        "Veterano, sigue el pulso en tu pantalla. Concéntrate profundamente. Estás respirando conmigo en tu base segura.",
        "Adulto mayor, suelta los hombros despacio. Deja caer todo el peso físico y mental de tu jornada acumulada.",
        "Trabajador gubernamental, no pienses en pendientes ahora. Borra tu lista mental y respira con total tranquilidad operativa.",
        "Mantén el ritmo constante. Siente el aire limpio y fresco renovando tu pecho en paz, como una recarga esencial.",
        "Te estoy acompañando en silencio. No estás solo en esta habitación. Permanece aquí, en calma estratégica.",
        "Siente tus pies firmes apoyados en el suelo. La tierra te sostiene, un anclaje gratuito y seguro.",
        "El piloto automático está completamente apagado en este segundo de bienestar. Continúa fluyendo con tu propio ritmo.",
        "Quédate justo en este instante presente. El pasado ya es historia y el futuro aún no requiere tu atención.",
        "Suelta la mandíbula ahora mismo. Libera esa tensión que aprietas, un eco de la presión. Desactívala.",
        "Tu mente está despertando poco a poco. Estás ganando el control real de tus propios pensamientos, tu mando interno.",
        "Eres mucho más grande que tus preocupaciones diarias. Respira muy hondo, despacio y con soltura, como un acto de soberanía.",
        "Rompe el círculo del ruido externo. Quédate aquí conmigo habitando este hermoso momento de tregua operativa.",
        "Escucha mi voz con atención. Nota cómo tu respiración se vuelve más profunda y limpia, un protocolo de calma.",
        "Tus ojos están descansando finalmente de todas las luces artificiales y del brillo de pantallas. Es tu descompresión visual.",
        "Siente los latidos de tu pecho. Es tu maravilloso motor vivo latiendo fuerte para ti, tu núcleo vital.",
        "Siente el peso fuera de tu espalda. Imagina que dejas caer todo tu cansancio acumulado, como una mochila liberada.",
        "No dejes que los pensamientos rápidos te saquen de este hermoso y plácido momento presente. Es tu santuario.",
        "Abandona la prisa de la ciudad el día de hoy. Aquí el tiempo es completamente tuyo, sin cronogramas externos.",
        "Tu calma regresará muy pronto, pero este valioso segundo de paz no se volverá a repetir. Concéntrate en él.",
        "Siente cómo tus pulmones se llenan de fuerza con cada bocanada de aire limpio y puro, tu recarga biológica.",
        "Tu vida necesita que estés muy fuerte por dentro. Regálate este respiro para recuperarte ahora, es una orden vital.",
        "Estás borrando con éxito el ruido del día. Quédate en la sala respirando con total comodidad y disciplina interna.",
        "La rutina diaria se ha roto. Tú gobiernas tus propias decisiones en este segundo exacto, tu autonomía.",
        "El suelo está firme debajo tuyo. Siente la estabilidad real de la tierra sosteniendo tu cuerpo, tu anclaje.",
        "Libera tu pecho de todo agobio ahora. Expulsa lo 'malo' de golpe con tu exhalación. Purifica tu espacio.",
        "Estás recuperando tu centro y tu equilibrio natural. Sigue la luz del círculo en calma, tu faro interno.",
        "Tu mente es fuerte. Has domado con éxito el miedo a las presiones externas de hoy. Victoria interna.",
        "Faltan pocos segundos para terminar el ciclo con calma. Siente la esperanza naciendo en ti, una nueva misión.",
        "Estás completamente a salvo aquí. Quédate en paz absoluta sintiendo el vaivén de tu respiración, tu ritmo natural."
    ],
    "AUDIOS_SECUENCIALES_CASA_EN": [
        "Veteran, follow the pulse on your screen. Concentrate deeply. You are breathing with me in your safe base.",
        "Senior, slowly relax your shoulders now. Let all the physical and mental weight of your accumulated day fall away.",
        "Government worker, don't think about pending tasks now. Clear your mental list and breathe with complete operational tranquility.",
        "Maintain a constant rhythm. Feel the fresh air cleansing your chest in peace, like an essential recharge.",
        "I am accompanying you in silence. You are not alone in this room. Stay here, in strategic calm.",
        "Feel your feet firmly on the ground. The earth supports you, a free and secure anchor.",
        "The autopilot is completely off this second of well-being. Continue flowing at your own pace.",
        "Stay right in this present instant. The past is history and the future does not yet require your attention.",
        "Release your jaw right now. Let go of that tension you clench, an echo of pressure. Deactivate it.",
        "Your mind is slowly awakening now. You are gaining real control over your own thoughts, your inner command.",
        "You are much bigger than your daily worries. Breathe deeply, slowly, and with ease, as an act of sovereignty.",
        "Break the cycle of external noise. Stay here with me inhabiting this beautiful moment of operational truce.",
        "Listen to my voice attentively. Notice how your breathing becomes deeper and cleaner, a protocol of calm.",
        "Your eyes are finally resting from all artificial lights and screen glare. It is your visual decompression.",
        "Feel your heartbeat. It is your wonderful living engine beating strongly for you, your vital core.",
        "Feel the weight off your back. Imagine letting go of all your accumulated tiredness, like a released backpack.",
        "Do not let fast thoughts take you out of this beautiful and placid present moment. It is your sanctuary.",
        "Abandon the city's rush today. Here, time is completely yours, without external schedules.",
        "Your calm will return very soon, but this valuable second of peace will not repeat. Focus on it.",
        "Feel your lungs fill with strength with each breath of clean, pure air, your biological recharge.",
        "Your life needs you to be very strong inside. Grant yourself this breath to recover now; it is a vital order.",
        "You are successfully clearing the day's noise. Stay in the room breathing with complete comfort and internal discipline.",
        "The daily routine is broken. You govern your own decisions at this exact second, your autonomy.",
        "The ground is firm beneath you. Feel the real stability of the earth supporting your body, your anchor.",
        "Free your chest from all overwhelm now. Expel the 'bad' at once with your exhalation. Purify your space.",
        "You are recovering your center and natural balance. Follow the light of the circle in calm, your inner beacon.",
        "Your mind is strong. You have successfully tamed the fear of today's external pressures. Inner victory.",
        "Only a few seconds left to complete the cycle calmly. Feel hope being born within you, a new mission.",
        "You are completely safe here. Remain in absolute peace, feeling the sway of your breath, your natural rhythm."
    ],

    "AUDIOS_SECUENCIALES_SALIR_ES": [
        "Veterano, es momento de un nuevo despliegue. Deja el dispositivo en modo seguro ahora.",
        "Adulto mayor, camina despacio hacia un nuevo horizonte. Respira hondo, con sabiduría.",
        "Trabajador gubernamental, estás retomando el control de tu tiempo. Tu misión de bienestar avanza.",
        "Elige tu camino con total confianza hoy. Visualiza tu zona de impacto de la paz.",
        "Estás en control absoluto de tus pensamientos. Siente la calma operativa.",
        "Siente la agradable emoción de un viaje. Tu próxima misión de bienestar te espera.",
        "Estás a punto de romper el piloto automático institucional. Avanza con propósito.",
        "Concéntrate únicamente en este momento presente. Observa tu entorno como un nuevo campo.",
        "Suelta las cadenas mentales de la rutina burocrática. Muévete libre, con autonomía.",
        "Estás eligiendo tu bienestar de forma consciente. Respira, es una orden prioritaria."
    ],
    "AUDIOS_SECUENCIALES_SALIR_EN": [
        "Veteran, it's time for a new deployment. Leave your device in safe mode now.",
        "Senior, walk slowly towards a new horizon. Breathe deeply, with wisdom.",
        "Government worker, you are regaining control of your time. Your wellness mission advances.",
        "Choose your path with total confidence today. Visualize your peace impact zone.",
        "You are in full control of your thoughts. Feel operational calm.",
        "Feel the pleasant excitement of a journey. Your next wellness mission awaits you.",
        "You are about to break the institutional autopilot. Advance with purpose.",
        "Focus solely on this present moment. Observe your surroundings as a new field.",
        "Release the mental chains of bureaucratic routine. Move freely, with autonomy.",
        "You are choosing your well-being consciously. Breathe, it is a priority order."
    ],

    "AUDIOS_CONDUCCION_ES": "Modo de trayecto seguro activo. Para proteger tu atención vital en la vía, este sistema mantiene la interfaz visual en reposo pasivo. Tu cuerpo viaja en misión por carretera; mantén tus manos firmes en el volante y tus ojos enfocados exclusivamente en el camino por delante. No mires ni manipules este dispositivo bajo ninguna circunstancia. Si notas tensión o agobio por la monotonía del tráfico, regálate una respiración completamente natural, lenta y profunda, sin perder jamás la concentración absoluta en tu entorno vial. Siente el soporte seguro de tu asiento y recuerda que tú gobiernas tu paz interna, no el tráfico. Conduce con total responsabilidad y enfoque.",
    "AUDIOS_CONDUCCION_EN": "Safe travel mode active. To protect your vital attention on the road, this system keeps the visual interface in passive rest. Your body is traveling on a road mission; keep your hands firmly on the wheel and your eyes focused exclusively on the road ahead. Do not look at or handle this device under any circumstances. If you notice tension or overwhelm from traffic monotony, grant yourself a completely natural, slow, and deep breath, never losing absolute concentration on your road environment. Feel the secure support of your seat and remember that you govern your inner peace, not traffic. Drive with full responsibility and focus.",
    
    "CATALOGO_RETOS_ES": [
        {"id": 201, "titulo": "EL RETO DEL FLUJO DE AGUA", "descripcion": "Dirígete con calma hacia tu cocina y abre el grifo muy despacio. Permite que el sonido del agua fluya, lavando la prisa acumulada. Escucha el flujo como un repliegue táctico sonoro. Es una descompresión auditiva para tu mente entrenada.", "img": "nature_sound.svg"},
        {"id": 202, "titulo": "EL RETO DEL CONTACTO CONSCIENTE", "descripcion": "Busca la prenda de ropa o la manta más suave que tengas cerca. Pasa las yemas de tus dedos sobre su textura con absoluta calma. Concéntrate en la sensación física, tu anclaje al presente. Tu cuerpo recupera su paz interna con esta misión sensorial.", "img": "observe.svg"},
        {"id": 203, "titulo": "EL RETO DE LA LÍNEA DE HORIZONTE", "descripcion": "Busca un objeto pequeño y cotidiano sobre tu mesa. Quédate observando fijamente sus bordes, sus sombras, sus colores. Es tu 'línea de horizonte' personal, un punto fijo para desviar tu mirada de las pantallas. Tu visión merece este descanso táctico.", "img": "words.svg"},
        {"id": 204, "titulo": "EL RETO DE LA ECO-AUDITORÍA", "descripcion": "Quédate completamente quieto en tu asiento y cierra los ojos. Presta atención e intenta identificar tres ruidos diferentes dentro de tu hogar. Vacía tu cabeza de los 'reportes' diarios y habita este preciso momento de quietud. Una auditoría de tu entorno sonoro.", "img": "silence.svg"},
        {"id": 205, "titulo": "EL RETO DEL REPORTE DE GRATITUD", "descripcion": "Toma un papel limpio y escribe una sola cosa que te haya hecho sonreír esta semana. Conéctate con esa alegría, respira pausadamente y permite que esa vibración aleje tu 'alerta' interna. Estás a salvo en tu base segura. Un reporte positivo.", "img": "gratitude.svg"},
        {"id": 206, "titulo": "EL RETO DEL PROTOCOLO DE HIDRATACIÓN", "descripcion": "Levántate despacio. Camina con calma, sirve un vaso con agua fresca y tómalo con tranquilidad antes de regresar a tus actividades. Concéntrate en la frescura, tu rehidratación de protocolo. Recarga tu sistema.", "img": "stretch.svg"},
        {"id": 207, "titulo": "EL RETO DE LA VENTANA DE VIGILANCIA", "descripcion": "Abre la ventana más cercana dos minutos. Guarda tu dispositivo, relaja tus brazos y quédate observando la inmensidad del cielo en silencio. Deja que el aire fresco 'limpie el canal' de tu rostro y te dé paz. Una vigilancia pacífica.", "img": "nature_sound.svg"},
        {"id": 208, "titulo": "EL RETO DE LA ORGANIZACIÓN TÁCTICA", "descripcion": "Mira a tu alrededor en tu habitación. Busca cinco objetos desordenados y colócalos pausadamente en su lugar. Con esos bastará para el día. Recupera la armonía en tu 'base'. Tu entorno refleja tu estado interno. Un pequeño despliegue de orden.", "img": "observe.svg"},
        {"id": 209, "titulo": "EL RETO DE LA RESPIRACIÓN CONTROLADA", "descripcion": "Siéntate cómodo. Haz cinco respiraciones profundas y lentas por la nariz, como un ejercicio de cadencia militar. Libera la tensión de tus hombros, vacía tu mente de 'órdenes' y permite que esta tregua biológica te calme. Un protocolo de respiro.", "img": "square_breath.svg"},
        {"id": 210, "titulo": "EL RETO DEL ESCANEO VISUAL EXTERNO", "descripcion": "Busca un punto u objeto muy lejano a ti a través de la ventana. Quédate mirando fijamente dos minutos. Descansa tus ojos de las 'pantallas de control'. Expande tu horizonte visual. Un escaneo de paz. Tu mente se libera en quietud.", "img": "nature_sound.svg"}
    ],
    "CATALOGO_RETOS_EN": [
        {"id": 201, "titulo_en": "THE WATER FLOW CHALLENGE", "descripcion_en": "Calmly head to your kitchen and slowly turn on the faucet. Allow the sound of water to flow, washing away accumulated rush. Listen to the flow as a tactical auditory retreat. It's an auditory decompression for your trained mind.", "img": "nature_sound.svg"},
        {"id": 202, "titulo_en": "THE MINDFUL TOUCH CHALLENGE", "descripcion_en": "Look for the softest piece of clothing or blanket nearby. Gently pass your fingertips over its texture with absolute calm. Concentrate on the physical sensation, your anchor to the present. Your body recovers its inner peace with this sensory mission.", "img": "observe.svg"},
        {"id": 203, "titulo_en": "THE HORIZON LINE CHALLENGE", "descripcion_en": "Find a small, everyday object on your table. Stare fixedly at its edges, shadows, colors. This is your personal 'horizon line', a fixed point to divert your gaze from screens. Your vision deserves this tactical rest.", "img": "words.svg"},
        {"id": 204, "titulo_en": "THE ECO-AUDIT CHALLENGE", "descripcion_en": "Stay completely still in your seat and close your eyes. Pay attention and try to identify three different noises occurring inside your home. Empty your head of daily 'reports' and inhabit this precise moment of stillness. An audit of your sound environment.", "img": "silence.svg"},
        {"id": 205, "titulo_en": "THE GRATITUDE REPORT CHALLENGE", "descripcion_en": "Take a clean paper and write down one beautiful thing that made you smile this week. Connect with that joy, breathe slowly, and allow that vibration to ward off your internal 'alert'. You are safe in your secure base. A positive report.", "img": "gratitude.svg"},
        {"id": 206, "titulo_en": "THE HYDRATION PROTOCOL CHALLENGE", "descripcion_en": "Slowly stand up. Walk calmly, pour a glass of fresh water and drink it peacefully before returning to your activities. Concentrate on the freshness, your protocol rehydration. Recharge your system.", "img": "stretch.svg"},
        {"id": 207, "titulo_en": "THE VIGILANCE WINDOW CHALLENGE", "descripcion_en": "Open the nearest window for two exact minutes. Put your device away, relax your arms, and observe the vastness of the sky in absolute silence. Let the fresh air 'clear the channel' of your face and give you peace. A peaceful vigilance.", "img": "nature_sound.svg"},
        {"id": 208, "titulo_en": "THE TACTICAL ORGANIZATION CHALLENGE", "descripcion_en": "Look around your room. Find five messy objects and slowly put them in their correct place. Those five will suffice for today. Regain harmony in your 'base'. Your environment reflects your internal state. A small deployment of order.", "img": "observe.svg"},
        {"id": 209, "titulo_en": "THE CONTROLLED BREATHING CHALLENGE", "descripcion_en": "Sit comfortably. Take five deep and slow breaths through your nose, like a military cadence exercise. Release tension from your shoulders, empty your mind of 'orders', and allow this biological truce to calm you. A breathing protocol.", "img": "square_breath.svg"},
        {"id": 210, "titulo_en": "THE EXTERNAL VISUAL SCAN CHALLENGE", "descripcion_en": "Look for a spot or object very far from you through the window. Stare fixedly for two minutes. Rest your eyes from 'control screens'. Expand your visual horizon. A scan of peace. Your mind is freed in stillness.", "img": "nature_sound.svg"}
    ],

    obtenerPerfilLocal() {
        let perfilRaw = localStorage.getItem("otg_perfil_dinamico");
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
                console.error("Error parsing otg_perfil_dinamico from localStorage, resetting.", e);
                perfil = { ...this.DEFAULT_NECESSITY_PROFILE };
            }
        }
        const now = Date.now();
        let lastDecayTimestamp = parseInt(localStorage.getItem("otg_last_decay") || now);
        this.sessionSeed = localStorage.getItem("otg_session_seed") || Math.random().toString(36).substring(2, 15);
        const daysPassed = (now - lastDecayTimestamp) / (1000 * 60 * 60 * 24);
        if (daysPassed >= 1) {
            const newPerfil = {};
            const base = 50;
            for (const necesidad in perfil) {
                if (necesidad === "indicador_ansiedad") {
                    newPerfil[necesidad] = Math.max(0, perfil[necesidad] - (daysPassed * 2));
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
        localStorage.setItem("otg_perfil_dinamico", JSON.stringify(perfil));
        localStorage.setItem("otg_last_decay", lastDecayTimestamp.toString());
        localStorage.setItem("otg_session_seed", this.sessionSeed);
        return perfil;
    },

    /**
     * Initializes the KERNEL on DOMContentLoaded.
     * REMOVED: All Stripe and password-related login. Direct entry.
     */
    init() {
        const storedLang = localStorage.getItem("otg_language");
        if (storedLang) {
            this.idiomaActual = storedLang;
        } else {
            localStorage.setItem("otg_language", this.idiomaActual);
        }

        try {
            this.historialSalir = JSON.parse(localStorage.getItem("otg_historial_salir") || "[]");
            this.historialCasa = JSON.parse(localStorage.getItem("otg_historial_casa") || "[]");
            this.historialPreguntas = JSON.parse(localStorage.getItem("otg_historial_oraculo") || "[]");
            this.historialRetosSecuencias = JSON.parse(localStorage.getItem("otg_historial_retos_secuencias") || "[]");
            this.historialFaseCasaSublime = JSON.parse(localStorage.getItem("otg_historial_fase_casa_sublime_daily") || "{}");
            this.historialAudiosCasaSecuenciales = JSON.parse(localStorage.getItem("otg_historial_audios_casa_secuenciales_daily") || "{}");
            this.historialAudiosSalirSecuenciales = JSON.parse(localStorage.getItem("otg_historial_audios_salir_secuenciales_daily") || "{}");
        } catch (e) {
            console.error("Error parsing history from localStorage, resetting specific histories.", e);
            this.historialSalir = [];
            this.historialCasa = [];
            this.historialPreguntas = [];
            this.historialRetosSecuencias = [];
            this.historialFaseCasaSublime = {};
            this.historialAudiosCasaSecuenciales = {};
            this.historialAudiosSalirSecuenciales = {};
            localStorage.removeItem("otg_historial_salir");
            localStorage.removeItem("otg_historial_casa");
            localStorage.removeItem("otg_historial_oraculo");
            localStorage.removeItem("otg_historial_retos_secuencias");
            localStorage.removeItem("otg_historial_fase_casa_sublime_daily");
            localStorage.removeItem("otg_historial_audios_casa_secuenciales_daily");
            localStorage.removeItem("otg_historial_audios_salir_secuenciales_daily");
        }

        this.obtenerPerfilLocal();
        this.mensajeCalidezHumanaActual = "";
        this.activarSensorSegundoPlano();

        const zipInput = document.getElementById('inp-zip');
        if (zipInput) {
            zipInput.addEventListener('input', () => this.validarZip());
            this.validarZip();
        }

        const btnVolverApp = document.getElementById('btn-volver-app');
        if (btnVolverApp) {
            btnVolverApp.addEventListener('click', () => this.reiniciarExperiencia());
        }
        
        // Directly start the initial sequence as there's no auth gate
        this.despertarInicial();
    },

    /**
     * Starts the initial welcome sequence after user interaction.
     * REMOVED: All auth gate logic.
     */
    despertarInicial() {
        const welcomeScreen = document.getElementById('pantalla-bienvenida');
        if (welcomeScreen) welcomeScreen.style.display = 'none';
       
        document.getElementById('wrapper-form').classList.remove('hidden');
        document.getElementById('btn-volver-app').classList.remove('hidden');
        document.getElementById('btn-whatsapp').classList.remove('hidden');
        document.getElementById('btn-messenger').classList.remove('hidden');
        this.cambiarIdioma(this.idiomaActual);
       
        this.horaInicioSesionAbsoluta = Date.now();

        const saludos_es = [
            "Bienvenido al Módulo de Homeostasis. Tu repliegue estratégico. Escucha mis preguntas en pantalla.",
            "El Sistema de Homeostasis está activo. Concéntrate un momento. Mira las opciones en tu pantalla ya.",
            "Has entrado al Módulo de Homeostasis. Rompamos tu piloto automático ahora mismo. Toca lo que sientes hoy."
        ];
        const saludos_en = [
            "Welcome to the Homeostasis Module. Your strategic retreat. Listen to my questions on screen.",
            "The Homeostasis System is active. Focus for a moment. Look at the options on your screen now.",
            "You have entered the Homeostasis Module. Let's break your autopilot right now. Tap what you feel today."
        ];
        const saludos = this.idiomaActual === 'es' ? saludos_es : saludos_en;
        this.hablar(saludos[Math.floor(Math.random() * saludos.length)]);
        this.inyectarBloquePreguntas();
        this.iniciarMonitoreoInaccion();
        this.activarBotonMandoLibreInicial();
    },

    /**
     * Injects a block of 3 questions into the UI, ensuring they are distinct and not recent.
     */
    inyectarBloquePreguntas() {
        const grid = document.getElementById('contenedor-preguntas-oraculo') || document.getElementById('grid-preguntas') || document.getElementById('contenedor-preguntas');
        if (!grid) return;
       
        clearInterval(this.temporizadorCascada);
        grid.innerHTML = "";
        this.indicePreguntaCascada = 0;
        const catalogo = this.idiomaActual === 'es' ? this.CATALOGO_PREGUNTAS_ES : this.CATALOGO_PREGUNTAS_EN;
        let preguntasYaVistasRecientemente = new Set(this.historialPreguntas);
        let unseenIndices = [];
        for (let i = 0; i < catalogo.length; i++) {
            if (!preguntasYaVistasRecientemente.has(i)) {
                unseenIndices.push(i);
            }
        }
        if (unseenIndices.length < 3) {
            this.historialPreguntas = [];
            localStorage.removeItem("otg_historial_oraculo");
            for (let i = 0; i < catalogo.length; i++) {
                unseenIndices.push(i);
            }
        }

       
        for (let i = unseenIndices.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [unseenIndices[i], unseenIndices[j]] = [unseenIndices[j], unseenIndices[i]];
        }
       
        let preguntasSeleccionadasIndices = [];
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
        localStorage.setItem("otg_historial_oraculo", JSON.stringify(this.historialPreguntas));
       
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

    /**
     * Initiates the fading cascade effect for questions.
     */
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

    /**
    * Activates the free writing input field and button from start.
    */
    activarBotonMandoLibreInicial() {
        const textarea = document.getElementById('inp-text-libre');
        const btnLibre = document.getElementById('btn-activar-libre');
        const lblDesahogo = document.getElementById('lbl-desahogo');
        const instruccion = document.getElementById('lbl-oraculo-instruccion');
        const zipInput = document.getElementById('inp-zip');

        if (instruccion) {
            instruccion.innerText = this.idiomaActual === 'es' ? "¿Qué te tiene atrapado hoy?" : "What has you trapped today?";
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
                    this.hablar(this.idiomaActual === 'es' ? "Escribe tu problema en el cuadro antes de activar el mando." : "Write your problem in the box before activating control.");
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

    /**
    * Validates ZIP input and controls button state.
    */
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

    /**
     * Activates the free writing input field and visually indicates readiness.
     */
    liberarCajonEscrituraLibre() {
        const textarea = document.getElementById('inp-text-libre');
        const lblDesahogo = document.getElementById('lbl-desahogo');
        const instruccion = document.getElementById('lbl-oraculo-instruccion');

        if (instruccion) {
            instruccion.innerText = this.idiomaActual === 'es' ? "Mando libre listo. Cuéntame qué te pasa." : "Free control ready. Tell me what is happening.";
            instruccion.style.color = "var(--green-action)";
        }

        if (lblDesahogo) lblDesahogo.style.color = "#fff";
        if (textarea) textarea.focus();

        this.validarZip();
    },

    /**
    * Monitors user inaction and advances question blocks or pauses.
    */
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
                this.hablar(this.idiomaActual === 'es' ? "Disculpa. Te daré tu tiempo. Sé que tu mente está saturada. Estaré aquí esperando." : "Apologies. I will give you time. I know your mind is saturated. I will be waiting here.");
               
                const instruccion = document.getElementById('lbl-oraculo-instruccion');
                if (instruccion) {
                    instruccion.innerText = this.idiomaActual === 'es' ? "Tomando un respiro. Toca cuando estés listo..." : "Taking a breath. Tap when you are ready...";
                    instruccion.style.color = "#666";
                }
            }
        }, 8000);
    },

    /**
     * Handles user selecting a question or entering free text.
     */
    reaccionarPreguntaSeleccionada(textoPregunta) {
        clearInterval(this.timerInaccion);
        clearInterval(this.temporizadorCascada);

        document.getElementById('inp-text-libre').value = textoPregunta;
        this.ejecutar();
    },

    /**
     * Converts text to speech using browser's SpeechSynthesis API.
     */
    hablar(texto) {
        if (!('speechSynthesis' in window)) return;
        if (!texto) return;

        let fx = texto.replace(/Módulo de Homeostasis/gi, "Módulo de Homeostasis").replace(/<[^>]*>/g, '');
        const msg = new SpeechSynthesisUtterance(fx);
        msg.lang = this.idiomaActual === 'es' ? 'es-US' : 'en-US';
        msg.rate = 1.10;
        msg.pitch = 1.05;

        msg.onend = () => {
            this.isSpeaking = false;
            this.speechQueue.shift();
            if (this.speechQueue.length > 0) {
                this._speakNextInQueue();
            }
        };

        msg.onerror = (event) => {
            console.error("Speech synthesis error:", event.error);
            this.isSpeaking = false;
            window.speechSynthesis.cancel();
            this.speechQueue = [];
        };

        this.speechQueue.push(msg);
        if (!this.isSpeaking) {
            this._speakNextInQueue();
        }
    },

    _speakNextInQueue() {
        if (this.speechQueue.length > 0 && !this.isSpeaking) {
            this.isSpeaking = true;
            window.speechSynthesis.speak(this.speechQueue[0]);
        }
    },

    /**
    * Changes the application's language and updates UI elements.
    * @param {string} lang - The target language ('es' or 'en').
    */
    cambiarIdioma(lang) {
        this.idiomaActual = lang;
        localStorage.setItem("otg_language", lang);
        document.getElementById('lang-es').classList.toggle('active', lang === 'es');
        document.getElementById('lang-en').classList.toggle('active', lang === 'en');
       
        const t = {
            es: {
                title: "Módulo de Homeostasis", zip: "Código Postal", instruccion: "¿Qué te tiene atrapado hoy?",
                desahogo: "O describe aquí tu desafío si no aparece arriba:",
                placeholder: "Cuéntale al sistema qué te pasa hoy...", btn: "Activar Mando Interno",
                alert: "Idioma cambiado a español.", budget0: "Gratis", budget1: "Bajo", budget2: "Abierto",
                veterano: "Veterano", adultomayor: "Adulto Mayor", gubernamental: "Gubernamental",
                menteHipervigilancia: "Hipervigilancia", menteAislamiento: "Aislamiento", menteCargaInvisible: "Carga Invisible",
                menteSaturacionUrbana: "Saturación Urbana", menteAgotamiento: "Agotamiento", modoSalir: "SALIR", modoCasa: "CASA",
                recomenzar: "RECOMENZAR EXPERIENCIA", puertaAbierta: "La puerta está abierta. ¿Continuamos?",
                volverApp: "Volver al Módulo"
            },
            en: {
                title: "Homeostasis Module", zip: "ZIP Code", instruccion: "What has you trapped today?",
                desahogo: "Or describe your challenge here if it does not appear above:",
                placeholder: "Tell the system what is happening to you today...", btn: "Activate Inner Command",
                alert: "Language switched to English.", budget0: "Free", budget1: "Low", budget2: "Open",
                veterano: "Veteran", adultomayor: "Senior", gubernamental: "Governmental",
                menteHipervigilancia: "Hypervigilance", menteAislamiento: "Isolation", menteCargaInvisible: "Invisible Burden",
                menteSaturacionUrbana: "Urban Saturation", menteAgotamiento: "Exhaustion", modoSalir: "OUT", modoCasa: "HOME",
                recomenzar: "RESTART EXPERIENCE", puertaAbierta: "The door is open. Shall we continue?",
                volverApp: "Return to Module"
            }
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
        document.getElementById('opt-perfil-adulto_mayor').innerText = t.adultomayor;
        document.getElementById('opt-perfil-gubernamental').innerText = t.gubernamental;
        document.getElementById('opt-mente-hipervigilancia').innerText = t.menteHipervigilancia;
        document.getElementById('opt-mente-aislamiento').innerText = t.menteAislamiento;
        document.getElementById('opt-mente-carga_invisible').innerText = t.menteCargaInvisible;
        document.getElementById('opt-mente-saturacion_urbana').innerText = t.menteSaturacionUrbana;
        document.getElementById('opt-mente-agotamiento').innerText = t.menteAgotamiento;
        document.querySelector('#modo-selector option[value="SALIR"]').innerText = t.modoSalir;
        document.querySelector('#modo-selector option[value="CASA"]').innerText = t.modoCasa;
       
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

    /**
     * Executes the main logic to fetch recommendations from the backend.
     */
    async ejecutar() {
        if (this.isLocked) return;
        this.isLocked = true;
       
        clearInterval(this.timerInaccion);
        clearInterval(this.temporizadorCascada);
        clearInterval(this.timerEnfocado);
        clearInterval(this.salidaTimerId);
        if (this.carouselInterval) {
            clearInterval(this.carouselInterval);
            this.carouselInterval = null;
        }
        this.speechQueue = [];
        this.isSpeaking = false;
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
            mente: document.getElementById('mente-selector') ? document.getElementById('mente-selector').value : "agotamiento",
            budget: document.getElementById('budget-selector') ? document.getElementById('budget-selector').value : "0",
            perfil: document.getElementById('perfil-selector') ? document.getElementById('perfil-selector').value : "veterano",
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
       
        container.innerHTML = `<div style='text-align:center; padding:40px 0;'><h2 style='color:#fff; font-size:1.1rem;'>${this.idiomaActual === 'es' ? 'CONECTANDO CON EL MANDO...' : 'CONNECTING TO CONTROL...'}</h2></div>`;
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
           
            let textoElegido = data.oraculo_manifiesto || (this.idiomaActual === 'es' ? "Respira profundo. Siente. Estás vivo. Respira." : "Breathe deeply. You are here. You are alive.");
           
            this.hablar(textoElegido);
           
            this.mensajeCalidezHumanaActual = textoElegido;
           
            if (this.tipoEscapeGlobal === "ACCION_CAMPO") {
                this.historialSalir = data.historial_salir_actualizado || [];
                localStorage.setItem("otg_historial_salir", JSON.stringify(this.historialSalir));
                this.pasosMisiones = data.misiones || [];
                this.mostrarOpcionesSalir(container);
            } else if (this.tipoEscapeGlobal === "MODO_CASA") {
                this.historialCasa = data.historial_casa_actualizado || [];
                localStorage.setItem("otg_historial_casa", JSON.stringify(this.historialCasa));
                this.pasosMisiones = data.misiones || [];
                this.procesarFlujoSecuencial(container);
            }
           
        } catch (error) {
            console.error("Fetch error:", error);
            alert(this.idiomaActual === 'es'
                ? "Error de conexión con el servidor. Por favor, inténtalo de nuevo."
                : "Connection error with the server. Please try again."
            );
            document.getElementById('wrapper-form').classList.remove('hidden');
            container.classList.add('hidden');
            this.isLocked = false;
            this.validarZip();
        }
    },

    /**
     * Displays the 3 options for SALIR mode and waits for user selection.
     */
    mostrarOpcionesSalir(container) {
        clearInterval(this.timerEnfocado);
        clearInterval(this.salidaTimerId);
        this.speechQueue = [];
        this.isSpeaking = false;
        window.speechSynthesis.cancel();

        const t = {
            es: {
                choosePath: "ELIGE TU CAMINO DE LIBERACIÓN",
                chooseOne: "Toca una opción para continuar tu repliegue:",
                mapsBtn: "🗺️ GOOGLE MAPS",
                ytBtn: "📺 YOUTUBE",
                spBtn: "🎵 SPOTIFY"
            },
            en: {
                choosePath: "CHOOSE YOUR PATH TO LIBERATION",
                chooseOne: "Tap an option to continue your retreat:",
                mapsBtn: "🗺️ GOOGLE MAPS",
                ytBtn: "📺 YOUTUBE",
                spBtn: "🎵 SPOTIFY"
            }
        }[this.idiomaActual];

        container.innerHTML = `
            <div class="mision-choices-container">
                <h2 class="salida-main-title" style="text-align: center; font-weight: 900; letter-spacing: 1px; color: #f8fafc; margin-top: 0;">${t.choosePath}</h2>
                <p class="salida-choose-instruction" style="text-align: center; color: #94a3b8; margin-bottom: 1.5rem;">${t.chooseOne}</p>
                <div id="salida-options-grid" class="salida-grid" style="display: flex; flex-direction: column; gap: 0.85rem; max-width: 380px; margin: 0 auto;">
                </div>
            </div>
        `;

        const optionsGrid = document.getElementById('salida-options-grid');
       
        if (Array.isArray(this.pasosMisiones) && this.pasosMisiones.length > 0) {
            const mission = this.pasosMisiones[0];
           
            const linkMaps = mission.destino_coordenadas_gps || "#";
            const linkYT = mission.enlace_youtube || "#";
            const linkSpotify = mission.enlace_spotify || "#";

            const btnMaps = document.createElement('a');
            btnMaps.href = linkMaps;
            btnMaps.target = "_blank";
            btnMaps.className = "btn-select-salida-clean";
            btnMaps.style = "display: block; text-decoration: none; text-align: center; padding: 1rem; background: #2563eb; color: white; border-radius: 6px; font-weight: bold; font-size: 1rem; cursor: pointer; transition: transform 0.15s; box-shadow: 0 4px 6px rgba(0,0,0,0.2);";
            btnMaps.innerText = t.mapsBtn;
            btnMaps.onclick = () => this.iniciarSalidaConcreta(mission);
            optionsGrid.appendChild(btnMaps);

            const btnYT = document.createElement('a');
            btnYT.href = linkYT;
            btnYT.target = "_blank";
            btnYT.className = "btn-select-salida-clean";
            btnYT.style = "display: block; text-decoration: none; text-align: center; padding: 1rem; background: #dc2626; color: white; border-radius: 6px; font-weight: bold; font-size: 1rem; cursor: pointer; transition: transform 0.15s; box-shadow: 0 4px 6px rgba(0,0,0,0.2);";
            btnYT.innerText = t.ytBtn;
            btnYT.onclick = () => this.iniciarSalidaConcreta(mission);
            optionsGrid.appendChild(btnYT);

            const btnSpotify = document.createElement('a');
            btnSpotify.href = linkSpotify;
            btnSpotify.target = "_blank";
            btnSpotify.className = "btn-select-salida-clean";
            btnSpotify.style = "display: block; text-decoration: none; text-align: center; padding: 1rem; background: #16a34a; color: white; border-radius: 6px; font-weight: bold; font-size: 1rem; cursor: pointer; transition: transform 0.15s; box-shadow: 0 4px 6px rgba(0,0,0,0.2);";
            btnSpotify.innerText = t.spBtn;
            btnSpotify.onclick = () => this.iniciarSalidaConcreta(mission);
            optionsGrid.appendChild(btnSpotify);
        }

        const textoOraculo = this.mensajeCalidezHumanaActual || t.chooseOne;
        this.hablar(textoOraculo);
    },

    /**
     * Initiates the 35s stabilization + 45s phrase injection for a selected SALIR mission.
     * MODIFIED: Includes redirection announcements and split-screen external links.
     * @param {Object} selectedMission - The mission object chosen by the client.
     */
    iniciarSalidaConcreta(selectedMission) {
        this.datosLugarGlobal = selectedMission;
        clearInterval(this.timerEnfocado);
        clearInterval(this.salidaTimerId);
        this.speechQueue = [];
        this.isSpeaking = false;
        window.speechSynthesis.cancel();
       
        const t = {
            es: { listen: "ESCUCHA MI GUÍA DE REPLIEGUE", launch: "ABRIR CANAL EXTERNO YA", maps: "Google Maps", youtube: "YouTube", spotify: "Spotify" },
            en: { listen: "LISTEN TO MY RETREAT GUIDE", launch: "OPEN EXTERNAL CHANNEL NOW", maps: "Google Maps", youtube: "YouTube", spotify: "Spotify" }
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
               
                <div id="external-links-container" class="external-links-grid hidden">
                    <button id="btn-maps-action" class="btn-external" title="${t.maps}">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="24px" height="24px"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
                        <span>${t.maps}</span>
                    </button>
                    <button id="btn-youtube-action" class="btn-external" title="${t.youtube}">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="24px" height="24px"><path d="M10 15l5.5-3.5L10 8V15zm11.23-7.39c-.78-.78-2.05-.78-2.83 0L12 11.02l-6.4-6.4c-.78-.78-2.05-.78-2.83 0-.78.78-.78 2.05 0 2.83L9.17 12l-6.4 6.4c-.78.78-.78 2.05 0 2.83.78.78 2.05.78 2.83 0L12 12.98l6.4 6.4c.78.78 2.05.78 2.83 0 .78-.78.78-2.05 0-2.83L14.83 12l6.4-6.4c.78-.78.78-2.05 0-2.83z"/></svg>
                        <span>${t.youtube}</span>
                    </button>
                    <button id="btn-spotify-action" class="btn-external" title="${t.spotify}">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="24px" height="24px"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm5 14.5c-.27 0-.53-.11-.72-.32-.97-1.04-2.45-1.72-4.28-1.72-1.83 0-3.31.68-4.28 1.72-.19.21-.45.32-.72.32-.27 0-.53-.11-.72-.32-.19-.21-.29-.48-.29-.78 0-.3.1-.57.29-.78.97-1.04 2.45-1.72 4.28-1.72 1.83 0 3.31.68 4.28 1.72.19.21.29.48.29.78 0 .3-.1.57-.29.78zM12 4c-3.72 0-6.76 2.97-7 6.64-.17 1.83.33 3.5 1.34 4.8-.45.54-1.04.99-1.77 1.25-.73.27-1.57.4-2.43.34-.1-.1-.2-.1-.28-.18-.08-.08-.13-.18-.13-.28 0-.05-.01-.1-.01-.14 0-.04 0-.08.01-.12.44-2.26 1.95-4.14 3.93-5.22.61-.34 1.25-.56 1.9-.66.65-.11 1.3-.13 1.93-.06.72-.05 1.44-.01 2.16.1 2.03.4 3.65 1.88 4.6 3.6.95 1.7.99 3.56.12 5.21-.55.8-1.25 1.37-2.01 1.63-.76.26-1.55.28-2.31.1-.09-.03-.18-.05-.27-.05-.09 0-.17.02-.25.06l-.28.1-.02-.1.01-.1-.01-.11v-.15c-.01-.06-.01-.12-.01-.17 0-.05 0-.1.01-.15z"/></svg>
                        <span>${t.spotify}</span>
                    </button>
                </div>
            </div>
        `;
       
        let speechText = (this.idiomaActual === 'es' ? this.datosLugarGlobal.destino_titulo : this.datosLugarGlobal.destino_titulo_en || this.datosLugarGlobal.destino_titulo) + ". " + (this.idiomaActual === 'es' ? this.datosLugarGlobal.destino_instruccion : this.datosLugarGlobal.destino_instruccion_en || this.datosLugarGlobal.destino_instruccion);
        this.hablar(speechText);
       
        let retencion = 35;
        const btnCount = document.getElementById('btn-countdown-salida');
        const externalLinksContainer = document.getElementById('external-links-container');
        const btnMaps = document.getElementById('btn-maps-action');
        const btnYoutube = document.getElementById('btn-youtube-action');
        const btnSpotify = document.getElementById('btn-spotify-action');
        const phrasesDiv = document.getElementById('salida-countdown-phrases');
        const AUDIOS_SECUENCIALES_SALIR = this.idiomaActual === 'es' ? this.AUDIOS_SECUENCIALES_SALIR_ES : this.AUDIOS_SECUENCIALES_SALIR_EN;
       
        let lastSalirAudioTime = -1;
       
        this.salidaTimerId = setInterval(() => {
            if (retencion > 0) {
                retencion--;
                if (btnCount) btnCount.innerText = `${retencion}s ${t.listen}`;
                if (retencion === 0) {
                    retencion = -45;
                    if (btnCount) btnCount.innerText = `${Math.abs(retencion)}s...`;
                   
                    let currentPhrase = this._getDailyNonRepeatingAudio(
                        AUDIOS_SECUENCIALES_SALIR,
                        "otg_historial_audios_salir_secuenciales_daily",
                        5
                    );
                    if (phrasesDiv) phrasesDiv.innerText = currentPhrase;
                    this.hablar(currentPhrase);
                    lastSalirAudioTime = retencion;
                }
            } else if (retencion < 0) {
                retencion++;
                if (btnCount) btnCount.innerText = `${Math.abs(retencion)}s...`;
                if (Math.abs(retencion) % 15 === 0 && retencion !== lastSalirAudioTime && Math.abs(retencion) > 0) {
                    lastSalirAudioTime = retencion;
                    let currentPhrase = this._getDailyNonRepeatingAudio(
                        AUDIOS_SECUENCIALES_SALIR,
                        "otg_historial_audios_salir_secuenciales_daily",
                        5
                    );
                    if (phrasesDiv) phrasesDiv.innerText = currentPhrase;
                    this.hablar(currentPhrase);
                }
                if (retencion === 0) {
                    clearInterval(this.salidaTimerId);
                    if (btnCount) btnCount.style.display = 'none';
                    if (phrasesDiv) phrasesDiv.innerText = "";
                   
                    if (externalLinksContainer) {
                        externalLinksContainer.classList.remove('hidden');

                        if (btnMaps && this.datosLugarGlobal.destino_coordenadas_gps) {
                            btnMaps.onclick = () => {
                                this.hablar(this.idiomaActual === 'es' ? `Abriendo ${t.maps}.` : `Opening ${t.maps}.`);
                                window.open(this.datosLugarGlobal.destino_coordenadas_gps, '_blank');
                                this._updateProfileAndRestartMonitor();
                            };
                        } else if (btnMaps) { btnMaps.disabled = true; btnMaps.style.opacity = 0.5; }

                        if (btnYoutube && this.datosLugarGlobal.enlace_youtube) {
                            btnYoutube.onclick = () => {
                                this.hablar(this.idiomaActual === 'es' ? `Abriendo ${t.youtube}.` : `Opening ${t.youtube}.`);
                                window.open(this.datosLugarGlobal.enlace_youtube, '_blank');
                                this._updateProfileAndRestartMonitor();
                            };
                        } else if (btnYoutube) { btnYoutube.disabled = true; btnYoutube.style.opacity = 0.5; }

                        if (btnSpotify && this.datosLugarGlobal.enlace_spotify) {
                            btnSpotify.onclick = () => {
                                this.hablar(this.idiomaActual === 'es' ? `Abriendo ${t.spotify}.` : `Opening ${t.spotify}.`);
                                window.open(this.datosLugarGlobal.enlace_spotify, '_blank');
                                this._updateProfileAndRestartMonitor();
                            };
                        } else if (btnSpotify) { btnSpotify.disabled = true; btnSpotify.style.opacity = 0.5; }
                    }
                }
            }
        }, 1000);
    },

    _updateProfileAndRestartMonitor() {
        try {
            let perfil = KERNEL.obtenerPerfilLocal();
            const selectedVector = KERNEL.datosLugarGlobal.vector_entorno_seleccionado;
            for (const need in selectedVector) {
                if (need !== "indicador_ansiedad" && perfil[need] !== undefined) {
                    perfil[need] = Math.min(perfil[need] + (selectedVector[need] * 0.1), 100);
                }
            }
            perfil["indicador_ansiedad"] = Math.max(0, perfil["indicador_ansiedad"] - 10);
            localStorage.setItem("otg_perfil_dinamico", JSON.stringify(perfil));
        } catch (e) {
            console.error("Error updating local profile after action:", e);
        }

        this.iniciarMonitoreoInaccion();
        this.horaInicioSesionAbsoluta = Date.now();
    },

    procesarFlujoSecuencial(container) {
        clearInterval(this.timerEnfocado);
        this.speechQueue = [];
        this.isSpeaking = false;
        window.speechSynthesis.cancel();

        const t = {
            es: {
                inspira: "Inhala ahora", expira: "Exhala ahora", fin: "Protocolo completado. Borrando rastro.",
                listen: "ESCUCHA MI GUÍA", launch: "ABRIR CANAL EXTERNO YA", fieldAction: "Acción de Campo",
                internalMission: "Misión de Repliegue Interno", doItNow: "EJECUTAR AHORA", suggestedEscape: "Acción de Campo sugerida"
            },
            en: {
                inspira: "Inhale now", expira: "Exhale now", fin: "Protocol completed. Clearing tracks.",
                listen: "LISTEN TO THE GUIDE", launch: "OPEN EXTERNAL CHANNEL NOW", fieldAction: "Field Action",
                internalMission: "Internal Retreat Mission", doItNow: "EXECUTE NOW", suggestedEscape: "Suggested Field Action"
            }
        }[this.idiomaActual];

        if (this.indiceMision >= this.pasosMisiones.length) {
            this.iniciarRelojEnfocadoCasa(container, t);
            return;
        }

        const paso = this.pasosMisiones[this.indiceMision];
        container.innerHTML = `
            <div class="mision-card">
                <small>${t.internalMission}</small>
                <h3>${this.idiomaActual === 'es' ? paso.titulo : paso.titulo_en || paso.titulo}</h3>
                <p>${this.idiomaActual === 'es' ? paso.descripcion : paso.descripcion_en || paso.descripcion}</p>
                <button id="btn-next" style="width:100%; background:var(--green-action); color:#fff; padding:16px; font-weight:bold; text-transform:uppercase; border-radius:6px; cursor:pointer; border:none; margin-top:15px; font-size:0.95rem;">${t.doItNow}</button>
            </div>`;

        this.hablar((this.idiomaActual === 'es' ? paso.titulo : paso.titulo_en || paso.titulo) + " . " + (this.idiomaActual === 'es' ? paso.descripcion : paso.descripcion_en || paso.descripcion));
       
        document.getElementById('btn-next').onclick = () => {
            try {
                let perfil = this.obtenerPerfilLocal();
                const missionVector = paso.vector_necesidades || this.DEFAULT_NECESSITY_PROFILE;
                for (const need in missionVector) {
                    if (need !== "indicador_ansiedad" && perfil[need] !== undefined) {
                        perfil[need] = Math.min(perfil[need] + (missionVector[need] * 0.05), 100);
                    }
                }
                perfil["indicador_ansiedad"] = Math.max(0, perfil["indicador_ansiedad"] - 5);
                localStorage.setItem("otg_perfil_dinamico", JSON.stringify(perfil));
            } catch (e) {
                console.error("Error updating local profile after CASA mission:", e);
            }

            this.iniciarMonitoreoInaccion();
            this.horaInicioSesionAbsoluta = Date.now();
           
            this.avanzarPaso();
        };
    },
   
    /**
     * Starts the 10-minute clinical breathing timer for CASA mode.
     */
    iniciarRelojEnfocadoCasa(container, t) {
        if (this.temporizadorCascada) {
            clearInterval(this.temporizadorCascada);
            this.temporizadorCascada = null;
        }

        clearInterval(this.timerInaccion);
        clearInterval(this.timerEnfocado);

        if (this.intervaloVozCasa) {
            clearInterval(this.intervaloVozCasa);
            this.intervaloVozCasa = null;
        }

        if (this.carouselInterval) {
            clearInterval(this.carouselInterval);
            this.carouselInterval = null;
        }

        this.speechQueue = [];
        this.isSpeaking = false;
        window.speechSynthesis.cancel();

        let msg = this.idiomaActual === 'es' ? "Iniciamos quince minutos de limpieza mental profunda. Respira." : "Starting fifteen minutes of deep mental clearing. Breathe.";
        this.hablar(msg);

        container.innerHTML = `
            <div id="carousel-background" class="carousel-container"></div>
            <div style="text-align:center; width:100%; position:relative; z-index:10;">
                <div id="breath-circle" style="cursor:pointer;" title="${this.idiomaActual === 'es' ? 'Toca para enfocar tu mente' : 'Tap to focus your mind'}"></div>
                <div id="timer">15:00</div>
                <p id="txt-pulmon">INHALA / INHALE</p>
                <div id="fase-sublime-text" style="margin-top:20px; text-align:center; font-size:1.1rem; min-height:40px; color:var(--green-action); font-weight:bold; letter-spacing:0.5px;"></div>
                <div id="salida-sugerida" class="hidden" style="margin-top: 30px; padding: 15px; border: 1px dashed #444; border-radius: 8px; font-size: 0.9rem; color: #888;">
                    <p style="margin:0;">${t.suggestedEscape}: <a href="#" id="link-salida-sugerida" style="color: var(--accent); text-decoration: none; font-weight: bold;">Cargando...</a></p>
                </div>
            </div>
        `;

        this.timeLeft = 900;
        this.contadorToques = 0;

        const carouselBackground = document.getElementById('carousel-background');
        const circleElement = document.getElementById('breath-circle');
        const timerDiv = document.getElementById('timer');
        const pulmonDiv = document.getElementById('txt-pulmon');
        const faseSublimeTextDiv = document.getElementById('fase-sublime-text');
        const salidaSugeridaDiv = document.getElementById('salida-sugerida');
        const linkSalidaSugerida = document.getElementById('link-salida-sugerida');

        const AUDIOS_SECUENCIALES_CASA = this.idiomaActual === 'es' ? this.AUDIOS_SECUENCIALES_CASA_ES : this.AUDIOS_SECUENCIALES_CASA_EN;
        const AUDIOS_FASE_SUBLIMES = this.idiomaActual === 'es' ? this.AUDIOS_FASE_CASA_SUBLIMES_ES : this.AUDIOS_FASE_CASA_SUBLIMES_EN;

        let currentImageIndex = 0;
        let imagesForMente = [];
        let imageChangeIntervalId = null;

        const currentMente = this.obtenerPerfilLocal().mente || document.getElementById('mente-selector').value || "agotamiento";
        imagesForMente = this.IMAGENES_CARRUSEL[currentMente] || this.IMAGENES_CARRUSEL["agotamiento"];
       
        for (let i = imagesForMente.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [imagesForMente[i], imagesForMente[j]] = [imagesForMente[j], imagesForMente[i]];
        }

        const startCarousel = () => {
            if (carouselBackground && imagesForMente.length > 0) {
                carouselBackground.style.backgroundImage = `url('${imagesForMente[currentImageIndex % imagesForMente.length]}')`;
                carouselBackground.classList.remove('hidden');
                this.carouselInterval = setInterval(() => {
                    currentImageIndex++;
                    carouselBackground.style.backgroundImage = `url('${imagesForMente[currentImageIndex % imagesForMente.length]}')`;
                }, 10000);
            }
        };

        const stopCarousel = () => {
            if (this.carouselInterval) {
                clearInterval(this.carouselInterval);
                this.carouselInterval = null;
            }
            if (carouselBackground) {
                carouselBackground.classList.add('hidden');
                carouselBackground.style.backgroundImage = 'none';
            }
        };

        if (this.salidaSugeridaTimeoutId) {
            clearTimeout(this.salidaSugeridaTimeoutId);
            this.salidaSugeridaTimeoutId = null;
        }

        this.salidaSugeridaTimeoutId = setTimeout(async () => {
            try {
                const payloadForSuggestion = {
                    modo: "SALIR",
                    lang: this.idiomaActual,
                    mente: document.getElementById('mente-selector') ? document.getElementById('mente-selector').value : "agotamiento",
                    budget: document.getElementById('budget-selector') ? document.getElementById('budget-selector').value : "0",
                    perfil: document.getElementById('perfil-selector') ? document.getElementById('perfil-selector').value : "veterano",
                    desahogo: document.getElementById('inp-text-libre') ? document.getElementById('inp-text-libre').value.trim() : "",
                    zip: document.getElementById('inp-zip') ? document.getElementById('inp-zip').value.trim() : "",
                    perfil_local: this.obtenerPerfilLocal(),
                    historial_salir: this.historialSalir
                };

                const r = await fetch("/api/mando-integral", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payloadForSuggestion) });
                const data = await r.json();

                if (data.drive_prohibited && data.legal_notice_es) {
                    console.warn("ALERT:", this.idiomaActual === 'es' ? data.legal_notice_es : data.legal_notice_en);
                }

                if (data.DIRECCIONAMIENTO_MASTER === "ACCION_CAMPO" && data.misiones && data.misiones.length > 0 && linkSalidaSugerida && salidaSugeridaDiv) {
                    const suggestedMission = data.misiones[0];
                    if (data.historial_salir_actualizado) {
                        this.historialSalir = data.historial_salir_actualizado;
                        localStorage.setItem("otg_historial_salir", JSON.stringify(this.historialSalir));
                    }
                    linkSalidaSugerida.innerText = this.idiomaActual === 'es' ? suggestedMission.destino_titulo : suggestedMission.destino_titulo_en || suggestedMission.destino_titulo;
                    linkSalidaSugerida.href = suggestedMission.destino_coordenadas_gps;
                    salidaSugeridaDiv.classList.remove('hidden');

                    this.hablar(this.idiomaActual === 'es' ? `Considera también esta Acción de Campo: ${suggestedMission.destino_titulo}` : `Also consider this Field Action: ${suggestedMission.destino_titulo_en || suggestedMission.destino_titulo}`);
                }

            } catch (e) {
                console.error("Error fetching SALIR suggestion in CASA mode:", e);
            } finally {
                this.salidaSugeridaTimeoutId = null;
            }
        }, 180000); // After 3 minutes

        if (circleElement) {
            circleElement.onclick = () => {
                if (typeof iniciarMusicaRelajantePropia === 'function') {
                    iniciarMusicaRelajantePropia();
                } else {
                    console.warn("iniciarMusicaRelajantePropia() no está definida.");
                }

                if (this.contadorToques < this.secuenciaAdelantos.length) {
                    // MECHANICAL FIX: Provide a default value for adelantoSegundos to prevent NaN,
                    // as this.secuenciaAdelantos is an empty array and never populated.
                    let adelantoSegundos = this.secuenciaAdelantos[this.contadorToques] || 0;
                    this.timeLeft = Math.max(this.timeLeft - adelantoSegundos, 0);
                    this.contadorToques++;
                    try {
                        let perfil = this.obtenerPerfilLocal();
                        perfil["indicador_ansiedad"] = Math.min((perfil["indicador_ansiedad"] || 0) + 5, 100);
                        localStorage.setItem("otg_perfil_dinamico", JSON.stringify(perfil));
                    } catch (e) {
                        console.error("Error updating anxiety indicator:", e);
                    }
                    let m = Math.floor(this.timeLeft / 60);
                    let s = this.timeLeft % 60;
                    if (timerDiv) {
                        timerDiv.innerText = `${m}:${s.toString().padStart(2, '0')}`;
                    }
                }
            };
        }

        let lastFaseSublimeAudioTime = -1;
        let lastCasaSecuencialAudioTime = -1;

        this.timerEnfocado = setInterval(() => {
            if (this.timeLeft > 0) {
                this.timeLeft--;
            }

            let m = Math.floor(this.timeLeft / 60);
            let s = this.timeLeft % 60;

            if (timerDiv) {
                timerDiv.innerText = `${m}:${s.toString().padStart(2, '0')}`;
            }

            if (this.timeLeft >= 300) {
                if (pulmonDiv) {
                    pulmonDiv.classList.remove('hidden');
                    let ciclo = (this.timeLeft - 300) % 8;
                    if (ciclo >= 4) {
                        pulmonDiv.innerText = t.inspira.toUpperCase();
                        pulmonDiv.style.color = "var(--cyan-inhale)";
                    } else {
                        pulmonDiv.innerText = t.expira.toUpperCase();
                        pulmonDiv.style.color = "var(--accent)";
                    }
                }
                if (faseSublimeTextDiv) faseSublimeTextDiv.innerText = "";
                stopCarousel();

                if (this.timeLeft < 900 && (900 - this.timeLeft) % 20 === 0 && (900 - this.timeLeft) !== lastCasaSecuencialAudioTime) {
                    lastCasaSecuencialAudioTime = (900 - this.timeLeft);
                    let recordatorioTexto = this._getDailyNonRepeatingAudio(
                        AUDIOS_SECUENCIALES_CASA,
                        "otg_historial_audios_casa_secuenciales_daily",
                        5
                    );
                    if (recordatorioTexto) {
                        this.hablar(recordatorioTexto);
                    }
                }
            }
            else if (this.timeLeft < 300 && this.timeLeft >= 60) {
                if (pulmonDiv) {
                    pulmonDiv.innerText = "";
                    pulmonDiv.classList.add('hidden');
                }
                if (faseSublimeTextDiv) {
                    faseSublimeTextDiv.classList.remove('hidden');
                }

                if (!this.carouselInterval) {
                    startCarousel();
                }

                if (this.timeLeft % 20 === 0 && this.timeLeft !== lastFaseSublimeAudioTime) {
                    lastFaseSublimeAudioTime = this.timeLeft;
                    let sublimeAudioText = this._getDailyNonRepeatingAudio(
                        AUDIOS_FASE_SUBLIMES,
                        "otg_historial_fase_casa_sublime_daily",
                        5
                    );
                    if (sublimeAudioText) {
                        faseSublimeTextDiv.innerText = sublimeAudioText;
                        this.hablar(sublimeAudioText);
                    }
                }
            }
            else if (this.timeLeft < 60) {
                if (pulmonDiv) pulmonDiv.innerText = "";
                if (faseSublimeTextDiv) faseSublimeTextDiv.innerText = "";
                stopCarousel();
            }

            if (this.timeLeft <= 0) {
                clearInterval(this.timerEnfocado);
                clearTimeout(this.salidaSugeridaTimeoutId);
                this.salidaSugeridaTimeoutId = null;
                stopCarousel();

                if (circleElement) {
                    circleElement.style.animation = "none";
                    circleElement.style.transform = "scale(1)";
                }
                this.iniciarRetoCierre60Segundos();
            }
        }, 1000);
    },

    /**
     * Advances to the next internal mission step.
     */
    avanzarPaso() {
        this.indiceMision++;
        const container = document.getElementById('wrapper-interactive');
        this.procesarFlujoSecuencial(container);
    },

    /**
     * Initiates the 60-second closing challenge phase.
     */
    iniciarRetoCierre60Segundos() {
        clearInterval(this.timerEnfocado);
        clearInterval(this.temporizadorCierre);
        this.speechQueue = [];
        this.isSpeaking = false;
        window.speechSynthesis.cancel();
       
        const t = {
            es: {
                logo: "Módulo de Homeostasis",
                cierreMensaje: "Gracias por tu presencia.",
                recomenzar: "RECOMENZAR EXPERIENCIA",
                puertaAbierta: "El despliegue ha concluido. ¿Continuamos?",
                retoInicial: "Prepárate para una misión de cierre en 3, 2, 1..."
            },
            en: {
                logo: "Homeostasis Module",
                cierreMensaje: "Thank you for your presence.",
                recomenzar: "RESTART EXPERIENCE",
                puertaAbierta: "The deployment has concluded. Shall we continue?",
                retoInicial: "Get ready for a closing mission in 3, 2, 1..."
            }
        }[this.idiomaActual];

        const container = document.getElementById('wrapper-interactive');
        const cierrePantalla = document.getElementById('pantalla-cierre');
        const retoTitulo = document.getElementById('reto-titulo');
        const retoDescripcion = document.getElementById('reto-descripcion');
        const retoImg = document.getElementById('reto-img');
        const cierreTimer = document.getElementById('cierre-timer');
        const btnRecomenzar = document.getElementById('btn-recomenzar-experiencia');
        const cierreMensajeFinal = document.getElementById('cierre-mensaje-final');
       
        if (container) container.classList.add('hidden');
        if (cierrePantalla) cierrePantalla.classList.remove('hidden');
        if (cierreMensajeFinal) cierreMensajeFinal.classList.add('hidden');
        if (btnRecomenzar) {
            btnRecomenzar.classList.add('hidden');
            btnRecomenzar.disabled = true;
        }
       
        this.timeLeftCierre = 60;
        const catalogoRetos = this.idiomaActual === 'es' ? this.CATALOGO_RETOS_ES : this.CATALOGO_RETOS_EN;
        let secuenciaRetos = [];
        let numRetos = 3;
        let candidateSequenceIds;
        let sequenceString;
        let maxAttempts = 10;
       
        while (maxAttempts > 0) {
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
                console.warn("Could not find a unique challenge sequence after multiple attempts, reusing one.");
                sequenceString = candidateSequenceIds;
            }
        }
       
        if (sequenceString) {
            this.historialRetosSecuencias.push(sequenceString);
            this.historialRetosSecuencias = this.historialRetosSecuencias.slice(-this.MAX_HISTORY_RETOS_SECUENCIAS);
            localStorage.setItem("otg_historial_retos_secuencias", JSON.stringify(this.historialRetosSecuencias));
        }

        let currentRetoIndex = 0;
       
        const displayNextReto = () => {
            if (currentRetoIndex < secuenciaRetos.length) {
                const reto = secuenciaRetos[currentRetoIndex];
                if (retoTitulo) {
                    retoTitulo.innerText = this.idiomaActual === 'es' ? reto.titulo : reto.titulo_en || reto.titulo;
                    retoTitulo.classList.remove('hidden');
                }
                if (retoDescripcion) {
                    retoDescripcion.innerText = this.idiomaActual === 'es' ? reto.descripcion : reto.descripcion_en || reto.descripcion;
                    retoDescripcion.classList.remove('hidden');
                }
                if (retoImg) {
                    retoImg.src = `/static/${reto.img}`;
                    retoImg.classList.remove('hidden');
                }
                this.hablar(this.idiomaActual === 'es' ? reto.descripcion : reto.descripcion_en || reto.descripcion);
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
                if (cierreTimer) {
                    cierreTimer.innerText = this.timeLeftCierre.toString().padStart(2, '0');
                }
               
                if (this.timeLeftCierre > 0 && currentRetoIndex < numRetos && (this.timeLeftCierre % Math.floor(60 / numRetos) === 0)) {
                    if (retoTitulo) retoTitulo.classList.add('hidden');
                    if (retoDescripcion) retoDescripcion.classList.add('hidden');
                    if (retoImg) retoImg.classList.add('hidden');
                    displayNextReto();
                }
               
                if (this.timeLeftCierre <= 0) {
                    clearInterval(this.temporizadorCierre);
                   
                    if (retoTitulo) retoTitulo.innerText = "";
                    if (retoDescripcion) retoDescripcion.innerText = "";
                    if (retoImg) retoImg.src = "";
                   
                    if (cierreTimer) cierreTimer.classList.add('hidden');
                    if (cierreMensajeFinal) cierreMensajeFinal.classList.remove('hidden');
                   
                    if (btnRecomenzar) {
                        btnRecomenzar.classList.remove('hidden');
                        btnRecomenzar.disabled = false;
                    }
                    this.hablar(t.puertaAbierta);
                }
            }, 1000);
        }, 5000);
       
        if (btnRecomenzar) {
            btnRecomenzar.onclick = () => {
                this.reiniciarExperiencia();
            };
        }
    },

    /**
     * Resets the UI to the initial form state without clearing persistent data.
     */
    reiniciarExperiencia() {
        clearInterval(this.timerInaccion);
        clearInterval(this.timerEnfocado);
        clearInterval(this.temporizadorCascada);
        clearInterval(this.temporizadorCierre);
        clearInterval(this.salidaTimerId);
        if (this.carouselInterval) {
            clearInterval(this.carouselInterval);
            this.carouselInterval = null;
        }
        this.speechQueue = [];
        this.isSpeaking = false;
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
       
        const pantallaCierre = document.getElementById('pantalla-cierre');
        const wrapperInteractive = document.getElementById('wrapper-interactive');
        const wrapperForm = document.getElementById('wrapper-form');
        const inpTextLibre = document.getElementById('inp-text-libre');

        if (pantallaCierre) pantallaCierre.classList.add('hidden');
        if (wrapperInteractive) wrapperInteractive.classList.add('hidden');
        if (wrapperForm) wrapperForm.classList.remove('hidden');
        if (inpTextLibre) inpTextLibre.value = "";
       
        this.inyectarBloquePreguntas();
        this.activarBotonMandoLibreInicial();
       
        const saludos_es = [
            "Bienvenido de nuevo al Módulo de Homeostasis. Tu repliegue estratégico. Escucha mis preguntas en pantalla.",
            "Módulo de Homeostasis activo. Toca lo que sientes hoy para continuar tu misión de bienestar."
        ];
        const saludos_en = [
            "Welcome back to the Homeostasis Module. Your strategic retreat. Listen to my questions on screen.",
            "Homeostasis Module active. Tap what you feel today to continue your wellness mission."
        ];
       
        const saludos = this.idiomaActual === 'es' ? saludos_es : saludos_en;
        this.hablar(saludos[Math.floor(Math.random() * saludos.length)]);
    },

    /**
     * Clears ALL session data and reloads the application.
     */
    destruirYReiniciar() {
        clearInterval(this.timerInaccion);
        clearInterval(this.timerEnfocado);
        clearInterval(this.temporizadorCascada);
        clearInterval(this.temporizadorCierre);
        clearInterval(this.salidaTimerId);
        if (this.carouselInterval) {
            clearInterval(this.carouselInterval);
            this.carouselInterval = null;
        }
        this.speechQueue = [];
        this.isSpeaking = false;
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
        this.historialFaseCasaSublime = {};
        this.historialAudiosCasaSecuenciales = {};
        this.historialAudiosSalirSecuenciales = {};
       
        this.pasosMisiones = [];
        this.indiceMision = 0;
        this.isLocked = false;
        this.contadorToques = 0;
        this.datosLugarGlobal = null;
       
        location.reload();
    }
};

if (typeof iniciarMusicaRelajantePropia === 'undefined') {
    window.iniciarMusicaRelajantePropia = function() {
        console.log("Música relajante propia iniciada (función de placeholder).");
    };
}

document.addEventListener('DOMContentLoaded', () => {
    if (typeof KERNEL !== 'undefined' && KERNEL.init) {
        KERNEL.init();
    }
});

window.KERNEL = KERNEL;
