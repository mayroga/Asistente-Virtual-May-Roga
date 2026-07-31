# ============================================================
# 4you&me
# Digital Wellbeing Companion
#
# Backend Principal
# FastAPI + SQLite
#
# NO ES UNA APLICACIÓN MÉDICA
# Sistema de acompañamiento, bienestar y hábitos saludables
# ============================================================

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List
import sqlite3
import hashlib
import os


# ============================================================
# CONFIGURACIÓN PRINCIPAL
# ============================================================

APP_NAME = "4you&me"

DATABASE = "fouryoume.db"

HELP_NUMBER = os.getenv(
    "HELP_NUMBER",
    "911"
)


app = FastAPI(
    title=APP_NAME,
    description=(
        "Asistente digital de bienestar, "
        "acompañamiento y hábitos saludables."
    ),
    version="1.0.0"
)


# Permitir conexión con frontend

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# ============================================================
# BASE DE DATOS
# ============================================================


def get_connection():

    connection = sqlite3.connect(
        DATABASE,
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    return connection



def init_database():

    db = get_connection()

    cursor = db.cursor()


    # Usuarios

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT NOT NULL,

        language TEXT DEFAULT 'es',

        created_at TEXT

    )
    """)



    # Estado diario

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_status (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        feeling TEXT,

        notes TEXT,

        created_at TEXT

    )
    """)



    # Actividades realizadas

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activities (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        activity TEXT,

        completed INTEGER DEFAULT 0,

        created_at TEXT

    )
    """)



    # Retos

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS challenges (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        challenge TEXT,

        completed INTEGER DEFAULT 0,

        created_at TEXT

    )
    """)



    # Rutinas

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS routines (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        objective TEXT,

        created_at TEXT

    )
    """)



    # Recordatorios

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminders (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        reminder TEXT,

        reminder_time TEXT,

        created_at TEXT

    )
    """)



    db.commit()

    db.close()



init_database()



# ============================================================
# MODELOS DE DATOS
# ============================================================


class UserCreate(BaseModel):

    name: str

    language: Optional[str] = "es"



class DailyStatusCreate(BaseModel):

    user_id: int

    feeling: str

    notes: Optional[str] = ""



class ActivityCreate(BaseModel):

    user_id: int

    activity: str



class ChallengeCreate(BaseModel):

    user_id: int

    challenge: str



class RoutineCreate(BaseModel):

    user_id: int

    objective: str



class ReminderCreate(BaseModel):

    user_id: int

    reminder: str

    reminder_time: str



class LoginRequest(BaseModel):

    username: str

    password: str



# ============================================================
# SEGURIDAD BÁSICA
# ============================================================


def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()



ADMIN_USER = os.getenv(
    "ADMIN_USERNAME",
    "admin"
)


ADMIN_PASSWORD = hash_password(
    os.getenv(
        "ADMIN_PASSWORD",
        "change_this_password"
    )
)
# ============================================================
# EVENTOS DEL SISTEMA
# ============================================================


@app.get("/")
def home():

    return {
        "app": APP_NAME,
        "message": (
            "Bienvenido a 4you&me. "
            "Un espacio digital de bienestar y acompañamiento."
        ),
        "status": "active"
    }



@app.get("/health")
def health_check():

    return {
        "status": "online",
        "service": APP_NAME,
        "time": datetime.now().isoformat()
    }



# ============================================================
# USUARIOS
# ============================================================


@app.post("/users")
def create_user(
    user: UserCreate
):

    db = get_connection()

    cursor = db.cursor()


    cursor.execute(
        """
        INSERT INTO users
        (
            name,
            language,
            created_at
        )
        VALUES
        (?, ?, ?)
        """,
        (
            user.name,
            user.language,
            datetime.now().isoformat()
        )
    )


    user_id = cursor.lastrowid


    db.commit()

    db.close()


    return {

        "success": True,

        "user_id": user_id,

        "message":
        "Usuario creado correctamente."

    }



@app.get("/users/{user_id}")
def get_user(
    user_id: int
):

    db = get_connection()

    cursor = db.cursor()


    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    )


    user = cursor.fetchone()


    db.close()


    if not user:

        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )


    return dict(user)



# ============================================================
# ESTADO DIARIO DE BIENESTAR
# ============================================================


@app.post("/daily-status")
def create_daily_status(
    status: DailyStatusCreate
):

    db = get_connection()

    cursor = db.cursor()


    cursor.execute(
        """
        INSERT INTO daily_status
        (
            user_id,
            feeling,
            notes,
            created_at
        )
        VALUES
        (?, ?, ?, ?)
        """,
        (
            status.user_id,
            status.feeling,
            status.notes,
            datetime.now().isoformat()
        )
    )


    db.commit()

    db.close()


    return {

        "success": True,

        "message":
        "Estado diario guardado."

    }



@app.get("/daily-status/{user_id}")
def get_daily_status(
    user_id: int
):

    db = get_connection()

    cursor = db.cursor()


    cursor.execute(
        """
        SELECT *
        FROM daily_status
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,)
    )


    data = cursor.fetchall()


    db.close()


    return [

        dict(item)

        for item in data

    ]



# ============================================================
# ACTIVIDADES DE BIENESTAR
# ============================================================


@app.post("/activities")
def create_activity(
    activity: ActivityCreate
):

    db = get_connection()

    cursor = db.cursor()


    cursor.execute(
        """
        INSERT INTO activities
        (
            user_id,
            activity,
            completed,
            created_at
        )
        VALUES
        (?, ?, ?, ?)
        """,
        (
            activity.user_id,
            activity.activity,
            0,
            datetime.now().isoformat()
        )
    )


    db.commit()

    db.close()


    return {

        "success": True,

        "message":
        "Actividad agregada."

    }



@app.get("/activities/{user_id}")
def get_activities(
    user_id: int
):

    db = get_connection()

    cursor = db.cursor()


    cursor.execute(
        """
        SELECT *
        FROM activities
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,)
    )


    activities = cursor.fetchall()


    db.close()


    return [

        dict(item)

        for item in activities

    ]



# ============================================================
# RETOS DIARIOS
# ============================================================


@app.post("/challenges")
def create_challenge(
    challenge: ChallengeCreate
):

    db = get_connection()

    cursor = db.cursor()


    cursor.execute(
        """
        INSERT INTO challenges
        (
            user_id,
            challenge,
            completed,
            created_at
        )
        VALUES
        (?, ?, ?, ?)
        """,
        (
            challenge.user_id,
            challenge.challenge,
            0,
            datetime.now().isoformat()
        )
    )


    db.commit()

    db.close()


    return {

        "success": True,

        "message":
        "Reto creado."

    }


@app.get("/challenges/{user_id}")
def get_challenges(
    user_id: int
):

    db = get_connection()

    cursor = db.cursor()


    cursor.execute(
        """
        SELECT *
        FROM challenges
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,)
    )


    challenges = cursor.fetchall()


    db.close()


    return [

        dict(item)

        for item in challenges

    ]
# ============================================================
# RUTINAS PERSONALIZADAS
# ============================================================


@app.post("/routines")
def create_routine(
    routine: RoutineCreate
):

    db = get_connection()

    cursor = db.cursor()


    cursor.execute(
        """
        INSERT INTO routines
        (
            user_id,
            objective,
            created_at
        )
        VALUES
        (?, ?, ?)
        """,
        (
            routine.user_id,
            routine.objective,
            datetime.now().isoformat()
        )
    )


    db.commit()

    db.close()


    return {

        "success": True,

        "message":
        "Rutina personalizada creada."

    }



@app.get("/routines/{user_id}")
def get_routines(
    user_id: int
):

    db = get_connection()

    cursor = db.cursor()


    cursor.execute(
        """
        SELECT *
        FROM routines
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,)
    )


    routines = cursor.fetchall()


    db.close()


    return [

        dict(item)

        for item in routines

    ]



# ============================================================
# RECORDATORIOS PERSONALES
# ============================================================


@app.post("/reminders")
def create_reminder(
    reminder: ReminderCreate
):

    db = get_connection()

    cursor = db.cursor()


    cursor.execute(
        """
        INSERT INTO reminders
        (
            user_id,
            reminder,
            reminder_time,
            created_at
        )
        VALUES
        (?, ?, ?, ?)
        """,
        (
            reminder.user_id,
            reminder.reminder,
            reminder.reminder_time,
            datetime.now().isoformat()
        )
    )


    db.commit()

    db.close()


    return {

        "success": True,

        "message":
        "Recordatorio guardado."

    }



@app.get("/reminders/{user_id}")
def get_reminders(
    user_id: int
):

    db = get_connection()

    cursor = db.cursor()


    cursor.execute(
        """
        SELECT *
        FROM reminders
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,)
    )


    reminders = cursor.fetchall()


    db.close()


    return [

        dict(item)

        for item in reminders

    ]



# ============================================================
# EJERCICIOS DE RESPIRACIÓN
# ============================================================


BREATHING_SESSIONS = [

    {
        "id": 3,
        "minutes": 3,
        "title_es":
        "Respiración tranquila de 3 minutos",
        "title_en":
        "3 minute calm breathing",

        "steps_es":[
            "Busca una posición cómoda.",
            "Inhala lentamente.",
            "Mantén unos segundos.",
            "Exhala suavemente."
        ],

        "steps_en":[
            "Find a comfortable position.",
            "Breathe in slowly.",
            "Hold for a few seconds.",
            "Exhale gently."
        ]
    },


    {
        "id":5,
        "minutes":5,

        "title_es":
        "Respiración consciente de 5 minutos",

        "title_en":
        "5 minute mindful breathing",

        "steps_es":[
            "Relaja los hombros.",
            "Siente el ritmo de tu respiración.",
            "Mantén una respiración constante.",
            "Disfruta este momento."
        ],

        "steps_en":[
            "Relax your shoulders.",
            "Feel your breathing rhythm.",
            "Keep a steady breathing pace.",
            "Enjoy this moment."
        ]
    },


    {
        "id":10,
        "minutes":10,

        "title_es":
        "Espacio personal de 10 minutos",

        "title_en":
        "10 minute personal space",

        "steps_es":[
            "Dedica este tiempo para ti.",
            "Respira lentamente.",
            "Observa tus pensamientos.",
            "Continúa con calma."
        ],

        "steps_en":[
            "Give this time to yourself.",
            "Breathe slowly.",
            "Observe your thoughts.",
            "Continue calmly."
        ]

    }

]



@app.get("/breathing")
def get_breathing():

    return BREATHING_SESSIONS



# ============================================================
# EJERCICIOS MENTALES
# ============================================================


MENTAL_EXERCISES = [

    {
        "id":1,
        "name_es":
        "Memoria visual",

        "name_en":
        "Visual memory",

        "description_es":
        "Observa elementos y recuerda su posición.",

        "description_en":
        "Observe elements and remember their position."
    },


    {
        "id":2,
        "name_es":
        "Secuencia diaria",

        "name_en":
        "Daily sequence",

        "description_es":
        "Ordena pequeños pasos de una actividad.",

        "description_en":
        "Arrange simple activity steps."
    },


    {
        "id":3,
        "name_es":
        "Concentración",

        "name_en":
        "Focus",

        "description_es":
        "Realiza una actividad breve de atención.",

        "description_en":
        "Complete a short attention activity."

    }

]



@app.get("/mental-exercises")
def get_mental_exercises():

    return MENTAL_EXERCISES



# ============================================================
# RETOS PREDEFINIDOS
# ============================================================


DEFAULT_CHALLENGES = [

    {
        "es":
        "Camina unos minutos y disfruta el entorno.",
        "en":
        "Walk for a few minutes and enjoy your surroundings."
    },


    {
        "es":
        "Escucha una canción que te guste.",
        "en":
        "Listen to a song you enjoy."
    },


    {
        "es":
        "Envía un mensaje positivo a alguien.",
        "en":
        "Send a positive message to someone."
    },


    {
        "es":
        "Dedica unos minutos a organizar algo personal.",
        "en":
        "Spend a few minutes organizing something personal."
    },


    {
        "es":
        "Escribe algo por lo que sientes gratitud.",
        "en":
        "Write something you appreciate."
    }

]


@app.get("/default-challenges")
def get_default_challenges():

    return DEFAULT_CHALLENGES



# ============================================================
# MENSAJES DE ACOMPAÑAMIENTO
# ============================================================


WELCOME_MESSAGES = {

    "es":[

        "Bienvenido a tu espacio de bienestar.",

        "Cada pequeño paso cuenta.",

        "Hoy puedes dedicar un momento para ti.",

        "Tu rutina diaria puede comenzar con tranquilidad."

    ],


    "en":[

        "Welcome to your wellbeing space.",

        "Every small step matters.",

        "Today you can take a moment for yourself.",

        "Your daily routine can begin with calm."

    ]

}


@app.get("/messages/{language}")
def get_messages(
    language:str="es"
):

    return WELCOME_MESSAGES.get(
        language,
        WELCOME_MESSAGES["es"]
    )



# ============================================================
# BOTÓN DE AYUDA EXTERNA
# ============================================================


@app.get("/help")
def help_button():

    return {

        "message":
        "Utiliza este botón para contactar servicios externos configurados.",

        "number":
        HELP_NUMBER

    }
# ============================================================
# PANEL ADMINISTRATIVO
# ============================================================


@app.post("/admin/login")
def admin_login(
    login: LoginRequest
):

    password_hash = hash_password(
        login.password
    )


    if (
        login.username == ADMIN_USER
        and password_hash == ADMIN_PASSWORD
    ):

        return {

            "success": True,

            "message":
            "Acceso administrativo autorizado."

        }


    raise HTTPException(

        status_code=401,

        detail=
        "Datos administrativos incorrectos."

    )



# ============================================================
# ESTADÍSTICAS GENERALES
# ============================================================


@app.get("/admin/statistics")
def admin_statistics():

    db = get_connection()

    cursor = db.cursor()



    # Usuarios registrados

    cursor.execute(
        """
        SELECT COUNT(*) 
        FROM users
        """
    )

    total_users = cursor.fetchone()[0]



    # Estados diarios

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM daily_status
        """
    )

    total_daily_status = cursor.fetchone()[0]



    # Actividades

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM activities
        """
    )

    total_activities = cursor.fetchone()[0]



    # Retos completados

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM challenges
        WHERE completed = 1
        """
    )

    completed_challenges = cursor.fetchone()[0]



    db.close()



    return {

        "registered_users":
        total_users,


        "daily_status_entries":
        total_daily_status,


        "activities_created":
        total_activities,


        "completed_challenges":
        completed_challenges,


        "generated_at":
        datetime.now().isoformat()

    }



# ============================================================
# COMPLETAR ACTIVIDADES
# ============================================================


@app.put("/activities/{activity_id}/complete")
def complete_activity(
    activity_id:int
):

    db = get_connection()

    cursor = db.cursor()



    cursor.execute(
        """
        UPDATE activities

        SET completed = 1

        WHERE id = ?

        """,
        (
            activity_id,
        )
    )



    db.commit()

    db.close()



    return {

        "success": True,

        "message":
        "Actividad completada."

    }




# ============================================================
# COMPLETAR RETOS
# ============================================================


@app.put("/challenges/{challenge_id}/complete")
def complete_challenge(
    challenge_id:int
):

    db = get_connection()

    cursor = db.cursor()



    cursor.execute(
        """
        UPDATE challenges

        SET completed = 1

        WHERE id = ?

        """,
        (
            challenge_id,
        )
    )



    db.commit()

    db.close()



    return {

        "success": True,

        "message":
        "Reto completado."

    }



# ============================================================
# RESUMEN PERSONAL DE BIENESTAR
# ============================================================


@app.get("/summary/{user_id}")
def user_summary(
    user_id:int
):

    db = get_connection()

    cursor = db.cursor()



    cursor.execute(
        """
        SELECT COUNT(*)
        FROM activities
        WHERE user_id = ?
        AND completed = 1

        """,
        (
            user_id,
        )
    )


    activities_completed = cursor.fetchone()[0]



    cursor.execute(
        """
        SELECT COUNT(*)
        FROM challenges
        WHERE user_id = ?
        AND completed = 1

        """,
        (
            user_id,
        )
    )


    challenges_completed = cursor.fetchone()[0]



    cursor.execute(
        """
        SELECT COUNT(*)
        FROM daily_status
        WHERE user_id = ?

        """,
        (
            user_id,
        )
    )


    daily_records = cursor.fetchone()[0]



    db.close()



    return {


        "user_id":
        user_id,


        "activities_completed":
        activities_completed,


        "challenges_completed":
        challenges_completed,


        "daily_records":
        daily_records,


        "message":
        "Continúa construyendo tu rutina de bienestar."

    }




# ============================================================
# MANEJO GLOBAL DE ERRORES
# ============================================================


@app.exception_handler(Exception)
async def global_exception_handler(
    request,
    exc
):

    return JSONResponse(

        status_code=500,

        content={

            "success":
            False,

            "message":
            "Ocurrió un problema interno.",

            "detail":
            str(exc)

        }

    )



# ============================================================
# CONFIGURACIÓN PARA RENDER CLOUD
# ============================================================


if __name__ == "__main__":

    import uvicorn


    port = int(
        os.getenv(
            "PORT",
            8000
        )
    )


    uvicorn.run(

        "main:app",

        host="0.0.0.0",

        port=port,

        reload=False

    )
