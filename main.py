@app.route("/assistant-stream", methods=["GET", "POST"])
def assistant_stream():
    try:
        # Obtener datos
        if request.method == "POST":
            data = request.get_json()
        else:
            data = request.args

        user_message = data.get("message", "")
        service = data.get("service", "general")
        secret = data.get("secret", "")

        # Verificar código secreto
        access_code = os.getenv("MAYROGA_ACCESS_CODE")
        if service == "all":
            if secret != access_code:
                return jsonify({"error": "Código incorrecto"}), 403
            # Aquí puedes agregar lógica para desbloquear todos los servicios
            return jsonify({"success": True, "message": "Servicios desbloqueados ✅"})

        # Guardar chat en Firebase
        db.collection("chats").add({
            "user_message": user_message,
            "service": service,
            "secret": secret
        })

        # 1️⃣ Intentar con Gemini
        try:
            response = gemini_model.generate_content(user_message)
            respuesta = response.text
        except Exception:
            # 2️⃣ Fallback a OpenAI
            completion = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres Asistente May Roga, experto en risoterapia y bienestar natural."},
                    {"role": "user", "content": user_message},
                ],
            )
            respuesta = completion.choices[0].message.content

        return jsonify({"reply": respuesta})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
