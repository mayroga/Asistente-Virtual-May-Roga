    ============================================================
    */

    // ==========================================================
    // CONFIGURACIÓN PRINCIPAL
    // ==========================================================

    // *** CORRECCIÓN CRÍTICA: Configuración de API_URL ***
    // Es fundamental que esta URL apunte al dominio donde se despliega tu backend.
    // Durante el desarrollo local, podría ser "http://localhost:8000".
    // En producción (ej. Render), será la URL de tu servicio backend (ej. "https://nombre-de-tu-app.onrender.com").
    const API_URL = "http://localhost:8000"; // CAMBIA ESTO EN PRODUCCIÓN

    let currentLanguage = "es";
    let currentUserId = null;
    let breathingInterval = null;
    let breathingSeconds = 0;
    let breathingActive = false;

    // ... (TEXTS del sistema - sin cambios)

    // ==========================================================
    // CAMBIO DE IDIOMA
    // ==========================================================

    function changeLanguage(language){
        currentLanguage = language;
        const subtitle = document.getElementById("subtitle");

        if(language === "es"){
            subtitle.innerText = "Tu espacio digital de bienestar y acompañamiento";
            document.documentElement.lang = "es"; // *** CORRECCIÓN: Actualiza el atributo lang del HTML ***
        } else {
            subtitle.innerText = "Your digital wellbeing and support space";
            document.documentElement.lang = "en"; // *** CORRECCIÓN: Actualiza el atributo lang del HTML ***
        }
        // *** MEJORA: Recargar contenido dependiente del idioma ***
        // Esto es necesario para que los textos dentro de las tarjetas (ej. ejercicios, retos) se actualicen.
        loadMentalExercises();
        loadChallenges();
        // Podrías necesitar actualizar otros elementos de texto fijos en la interfaz si no se recargan al cambiar de idioma.
    }

    // ... (ASISTENTE DE VOZ - sin cambios)

    // ==========================================================
    // CREAR PERFIL
    // ==========================================================

    async function createProfile() {
        const name = document.getElementById("userName").value;

        if (!name) {
            alert("Escribe tu nombre");
            return;
        }

        // *** CORRECCIÓN: Manejo robusto de errores en llamadas fetch ***
        try {
            const response = await fetch(API_URL + "/users", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    name: name,
                    language: currentLanguage
                })
            });

            if (!response.ok) { // Verifica si la respuesta HTTP fue exitosa (código 2xx)
                const errorData = await response.json().catch(() => ({ message: "Error desconocido del servidor." }));
                throw new Error(errorData.message || `Error del servidor: ${response.status}`);
            }

            const data = await response.json();
            currentUserId = data.user_id;
            document.getElementById("profileResult").innerText = TEXTS[currentLanguage].profileCreated;
            speak(TEXTS[currentLanguage].profileCreated);

        } catch (error) {
            console.error("Error al crear perfil:", error);
            alert("Ocurrió un error al crear el perfil. Por favor, inténtalo de nuevo. Detalle: " + error.message);
        }
    }

    // ==========================================================
    // GUARDAR ESTADO DIARIO
    // ==========================================================

    async function saveDailyStatus() {
        if (!currentUserId) {
            alert("Primero crea tu perfil");
            return;
        }

        const feeling = document.getElementById("dailyFeeling").value;
        const notes = document.getElementById("dailyNotes").value;

        // *** CORRECCIÓN: Manejo robusto de errores en llamadas fetch ***
        try {
            const response = await fetch(API_URL + "/daily-status", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    user_id: currentUserId,
                    feeling: feeling,
                    notes: notes
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ message: "Error desconocido del servidor." }));
                throw new Error(errorData.message || `Error del servidor: ${response.status}`);
            }

            // Si necesitas la respuesta del backend, aquí iría: const data = await response.json();
            speak(TEXTS[currentLanguage].dailySaved);

        } catch (error) {
            console.error("Error al guardar estado diario:", error);
            alert("Ocurrió un error al guardar tu estado diario. Por favor, inténtalo de nuevo. Detalle: " + error.message);
        }
    }

    // ... (MÓDULO DE RESPIRACIÓN GUIADA - sin cambios)
    // ... (EJERCICIOS MENTALES - se debe aplicar el manejo de errores fetch también en loadMentalExercises)

    async function loadMentalExercises(){
        try {
            const response = await fetch(API_URL + "/mental-exercises");
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ message: "Error desconocido al cargar ejercicios." }));
                throw new Error(errorData.message || `Error al cargar ejercicios mentales: ${response.status}`);
            }
            const exercises = await response.json();
            const container = document.getElementById("mentalExercises");
            container.innerHTML = "";
            exercises.forEach(exercise => {
                let card = document.createElement("div");
                card.className = "mental-card";
                card.innerHTML = `
                    <h3>${currentLanguage === "es" ? exercise.name_es : exercise.name_en}</h3>
                    <p>${currentLanguage === "es" ? exercise.description_es : exercise.description_en}</p>
                `;
                container.appendChild(card);
            });
        } catch (error) {
            console.error("Error cargando ejercicios mentales:", error);
            document.getElementById("mentalExercises").innerHTML = `<p style="color:red;">No se pudieron cargar los ejercicios mentales. Detalle: ${error.message}</p>`;
        }
    }

    // ... (RETOS DIARIOS - se debe aplicar el manejo de errores fetch también en loadChallenges)

    async function loadChallenges(){
        try {
            const response = await fetch(API_URL + "/default-challenges");
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ message: "Error desconocido al cargar retos." }));
                throw new Error(errorData.message || `Error al cargar retos diarios: ${response.status}`);
            }
            const challenges = await response.json();
            const container = document.getElementById("challengeList");
            container.innerHTML = "";
            challenges.forEach(challenge => {
                let item = document.createElement("div");
                item.className = "challenge-item";
                item.innerText = currentLanguage === "es" ? challenge.es : challenge.en;
                container.appendChild(item);
            });
        } catch (error) {
            console.error("Error cargando retos diarios:", error);
            document.getElementById("challengeList").innerHTML = `<p style="color:red;">No se pudieron cargar los retos diarios. Detalle: ${error.message}</p>`;
        }
    }

    // ... (CREAR RUTINA PERSONALIZADA - se debe aplicar el manejo de errores fetch también en saveRoutine)

    async function saveRoutine(){
        if(!currentUserId){
            alert("Primero crea tu perfil");
            return;
        }
        const objective = document.getElementById("routineObjective").value;

        try {
            const response = await fetch(API_URL + "/routines", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    user_id: currentUserId,
                    objective: objective
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ message: "Error desconocido al guardar rutina." }));
                throw new Error(errorData.message || `Error al guardar rutina: ${response.status}`);
            }

            document.getElementById("routineResult").innerText = "Rutina creada: " + objective;
            speak("Tu rutina personalizada fue creada.");
        } catch (error) {
            console.error("Error al guardar rutina:", error);
            alert("Ocurrió un error al guardar tu rutina. Por favor, inténtalo de nuevo. Detalle: " + error.message);
        }
    }

    // ... (RECORDATORIOS PERSONALES - se debe aplicar el manejo de errores fetch también en saveReminder)

    async function saveReminder(){
        if(!currentUserId){
            alert("Primero crea tu perfil");
            return;
        }
        const reminder = document.getElementById("reminderText").value;
        const time = document.getElementById("reminderTime").value;

        try {
            const response = await fetch(API_URL + "/reminders", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    user_id: currentUserId,
                    reminder: reminder,
                    reminder_time: time
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ message: "Error desconocido al guardar recordatorio." }));
                throw new Error(errorData.message || `Error al guardar recordatorio: ${response.status}`);
            }

            document.getElementById("reminderResult").innerText = "Recordatorio guardado correctamente.";
            speak("Recordatorio guardado.");
        } catch (error) {
            console.error("Error al guardar recordatorio:", error);
            alert("Ocurrió un error al guardar tu recordatorio. Por favor, inténtalo de nuevo. Detalle: " + error.message);
        }
    }

    // ... (BOTÓN DE AYUDA EXTERNA - se debe aplicar el manejo de errores fetch también en openHelp)

    async function openHelp(){
        try {
            const response = await fetch(API_URL + "/help");
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ message: "Error desconocido al obtener ayuda." }));
                throw new Error(errorData.message || `Error al obtener información de ayuda: ${response.status}`);
            }
            const data = await response.json();
            let confirmCall = confirm("Contactar servicio externo: " + data.number);
            if(confirmCall){
                window.location.href = "tel:" + data.number;
            }
        } catch (error) {
            console.error("Error al abrir ayuda externa:", error);
            alert("No se pudo obtener la información de ayuda externa. Detalle: " + error.message);
        }
    }

    // ... (PANEL ADMINISTRATIVO - sin cambios, ya tiene un manejo básico)

    // ==========================================================
    // INICIO AUTOMÁTICO
    // ==========================================================

    window.onload = function(){
        loadMentalExercises();
        loadChallenges();
        // *** CORRECCIÓN: Llamar a startAssistant() para manejar el mensaje de bienvenida y su voz. ***
        startAssistant();
    };
