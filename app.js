/*
============================================================
4you&me
Digital Wellbeing Companion

Archivo:
app.js

Lógica del navegador

============================================================
*/


// ==========================================================
// CONFIGURACIÓN PRINCIPAL
// ==========================================================


const API_URL = "";


let currentLanguage = "es";


let currentUserId = null;



let breathingInterval = null;

let breathingSeconds = 0;

let breathingActive = false;




// ==========================================================
// TEXTOS DEL SISTEMA
// ==========================================================


const TEXTS = {


    es: {


        welcome:
        "Bienvenido a tu espacio de bienestar y acompañamiento.",


        profileCreated:
        "Tu perfil fue creado correctamente.",


        dailySaved:
        "Tu estado diario fue guardado.",


        breathingStart:
        "Comenzamos la respiración guiada. Inhala lentamente.",


        breathingStop:
        "La sesión terminó. Gracias por dedicar este momento para ti."


    },



    en: {


        welcome:
        "Welcome to your wellbeing and support space.",


        profileCreated:
        "Your profile was created successfully.",


        dailySaved:
        "Your daily status was saved.",


        breathingStart:
        "We begin guided breathing. Breathe in slowly.",


        breathingStop:
        "The session has ended. Thank you for taking this moment for yourself."

    }


};





// ==========================================================
// CAMBIO DE IDIOMA
// ==========================================================


function changeLanguage(language){


    currentLanguage = language;


    const subtitle =
    document.getElementById(
        "subtitle"
    );



    if(language==="es"){


        subtitle.innerText =
        "Tu espacio digital de bienestar y acompañamiento";


    }

    else{


        subtitle.innerText =
        "Your digital wellbeing and support space";


    }


}





// ==========================================================
// ASISTENTE DE VOZ
// ==========================================================


function speak(text){



    if(
        "speechSynthesis" 
        in window
    ){


        let speech =
        new SpeechSynthesisUtterance(
            text
        );



        speech.lang =
        currentLanguage==="es"
        ?
        "es-ES"
        :
        "en-US";



        speech.rate =
        0.9;



        speech.pitch =
        1;



        window.speechSynthesis.speak(
            speech
        );


    }


}





function speakMessage(){


    const message =
    TEXTS[currentLanguage].welcome;


    document.getElementById(
        "voiceMessage"
    ).innerText =
    message;



    speak(message);


}




function startAssistant(){


    speakMessage();


}





// ==========================================================
// CREAR PERFIL
// ==========================================================


async function createProfile(){



    const name =
    document.getElementById(
        "userName"
    ).value;



    if(!name){


        alert(
            "Escribe tu nombre"
        );


        return;


    }




    const response =
    await fetch(
        API_URL + "/users",
        {


            method:
            "POST",


            headers:
            {


                "Content-Type":
                "application/json"


            },


            body:
            JSON.stringify(
                {


                    name:
                    name,


                    language:
                    currentLanguage


                }
            )


        }
    );




    const data =
    await response.json();




    currentUserId =
    data.user_id;




    document.getElementById(
        "profileResult"
    ).innerText =
    TEXTS[currentLanguage]
    .profileCreated;



    speak(
        TEXTS[currentLanguage]
        .profileCreated
    );



}




// ==========================================================
// GUARDAR ESTADO DIARIO
// ==========================================================


async function saveDailyStatus(){



    if(!currentUserId){


        alert(
            "Primero crea tu perfil"
        );


        return;


    }




    const feeling =
    document.getElementById(
        "dailyFeeling"
    ).value;




    const notes =
    document.getElementById(
        "dailyNotes"
    ).value;





    await fetch(
        API_URL + "/daily-status",
        {


            method:
            "POST",


            headers:
            {


                "Content-Type":
                "application/json"


            },


            body:
            JSON.stringify(
                {


                    user_id:
                    currentUserId,


                    feeling:
                    feeling,


                    notes:
                    notes


                }
            )


        }
    );




    speak(
        TEXTS[currentLanguage]
        .dailySaved
    );


}
/* ==========================================================
   MÓDULO DE RESPIRACIÓN GUIADA
========================================================== */


function startBreathing(minutes){


    stopBreathing();



    breathingActive = true;



    breathingSeconds =
    minutes * 60;




    document.getElementById(
        "breathingInstruction"
    ).innerText =
    TEXTS[currentLanguage]
    .breathingStart;




    speak(
        TEXTS[currentLanguage]
        .breathingStart
    );



    updateBreathingTimer();




    breathingInterval =
    setInterval(
        ()=>{


            breathingSeconds--;



            updateBreathingTimer();



            if(
                breathingSeconds <= 0
            ){


                stopBreathing();


                speak(
                    TEXTS[currentLanguage]
                    .breathingStop
                );


            }


        },

        1000

    );


}






function updateBreathingTimer(){



    let minutes =
    Math.floor(
        breathingSeconds / 60
    );



    let seconds =
    breathingSeconds % 60;



    document.getElementById(
        "breathingTimer"
    ).innerText =


    String(minutes)
    .padStart(2,"0")
    +
    ":"+
    String(seconds)
    .padStart(2,"0");



}






function stopBreathing(){



    if(
        breathingInterval
    ){


        clearInterval(
            breathingInterval
        );


    }



    breathingInterval =
    null;


    breathingActive =
    false;



}







// ==========================================================
// EJERCICIOS MENTALES
// ==========================================================


async function loadMentalExercises(){



    const response =
    await fetch(
        API_URL +
        "/mental-exercises"
    );



    const exercises =
    await response.json();




    const container =
    document.getElementById(
        "mentalExercises"
    );



    container.innerHTML = "";




    exercises.forEach(
        exercise => {



            let card =
            document.createElement(
                "div"
            );



            card.className =
            "mental-card";




            card.innerHTML = `

            <h3>

            ${
            currentLanguage==="es"
            ?
            exercise.name_es
            :
            exercise.name_en
            }

            </h3>


            <p>

            ${
            currentLanguage==="es"
            ?
            exercise.description_es
            :
            exercise.description_en
            }

            </p>

            `;



            container.appendChild(
                card
            );



        }

    );



}







// ==========================================================
// RETOS DIARIOS
// ==========================================================


async function loadChallenges(){



    const response =
    await fetch(
        API_URL +
        "/default-challenges"
    );



    const challenges =
    await response.json();




    const container =
    document.getElementById(
        "challengeList"
    );



    container.innerHTML = "";




    challenges.forEach(
        challenge => {



            let item =
            document.createElement(
                "div"
            );



            item.className =
            "challenge-item";



            item.innerText =

            currentLanguage==="es"
            ?
            challenge.es
            :
            challenge.en;




            container.appendChild(
                item
            );



        }

    );


}





// ==========================================================
// CREAR RUTINA PERSONALIZADA
// ==========================================================


async function saveRoutine(){



    if(!currentUserId){


        alert(
            "Primero crea tu perfil"
        );


        return;


    }



    const objective =
    document.getElementById(
        "routineObjective"
    ).value;




    await fetch(
        API_URL +
        "/routines",
        {


            method:
            "POST",


            headers:
            {


                "Content-Type":
                "application/json"


            },


            body:
            JSON.stringify(
                {


                    user_id:
                    currentUserId,


                    objective:
                    objective


                }
            )

        }

    );




    document.getElementById(
        "routineResult"
    ).innerText =


    "Rutina creada: "
    +
    objective;




    speak(
        "Tu rutina personalizada fue creada."
    );



}
/* ==========================================================
   RECORDATORIOS PERSONALES
========================================================== */


async function saveReminder(){


    if(!currentUserId){


        alert(
            "Primero crea tu perfil"
        );


        return;


    }




    const reminder =
    document.getElementById(
        "reminderText"
    ).value;




    const time =
    document.getElementById(
        "reminderTime"
    ).value;





    await fetch(

        API_URL +
        "/reminders",

        {


            method:
            "POST",


            headers:
            {


                "Content-Type":
                "application/json"


            },


            body:
            JSON.stringify(
                {


                    user_id:
                    currentUserId,


                    reminder:
                    reminder,


                    reminder_time:
                    time


                }
            )


        }

    );




    document.getElementById(
        "reminderResult"
    ).innerText =


    "Recordatorio guardado correctamente.";




    speak(
        "Recordatorio guardado."
    );



}








// ==========================================================
// BOTÓN DE AYUDA EXTERNA
// ==========================================================


async function openHelp(){



    const response =
    await fetch(
        API_URL +
        "/help"
    );



    const data =
    await response.json();




    let confirmCall =
    confirm(

        "Contactar servicio externo: "
        +
        data.number

    );



    if(confirmCall){


        window.location.href =
        "tel:" +
        data.number;


    }



}








// ==========================================================
// PANEL ADMINISTRATIVO
// ==========================================================


async function adminLogin(){



    const username =
    document.getElementById(
        "adminUser"
    ).value;



    const password =
    document.getElementById(
        "adminPassword"
    ).value;





    const response =
    await fetch(

        API_URL +
        "/admin/login",

        {


            method:
            "POST",


            headers:
            {


                "Content-Type":
                "application/json"


            },


            body:
            JSON.stringify(
                {


                    username:
                    username,


                    password:
                    password


                }
            )

        }

    );





    if(
        response.ok
    ){


        loadAdminStatistics();



    }

    else{


        alert(
            "Acceso no autorizado."
        );


    }



}






async function loadAdminStatistics(){



    const response =
    await fetch(

        API_URL +
        "/admin/statistics"

    );




    const data =
    await response.json();




    document.getElementById(
        "adminStatistics"
    ).innerHTML = `


    <h3>
    Estadísticas generales
    </h3>


    <p>
    Usuarios registrados:
    ${data.registered_users}
    </p>


    <p>
    Registros diarios:
    ${data.daily_status_entries}
    </p>


    <p>
    Actividades creadas:
    ${data.activities_created}
    </p>


    <p>
    Retos completados:
    ${data.completed_challenges}
    </p>


    `;



}








// ==========================================================
// INICIO AUTOMÁTICO
// ==========================================================


window.onload = function(){



    loadMentalExercises();



    loadChallenges();



    speak(
        TEXTS[currentLanguage]
        .welcome
    );



};


