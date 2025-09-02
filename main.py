import os
import stripe
import json
from flask import Flask, jsonify, request
from firebase_admin import credentials, firestore
import firebase_admin

# Carga las variables de entorno para Firebase y Stripe
# Las variables globales __firebase_config__ y __app_id__ se inyectan en el entorno de Render
firebase_config = json.loads(os.environ.get('__firebase_config__'))
app_id = os.environ.get('__app_id__')

# La clave secreta de Stripe debe estar en las variables de entorno
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Inicializa la aplicación Flask
app = Flask(__name__)

# Inicializa Firebase Admin SDK con la configuración de servicio
cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    """
    Crea una sesión de pago en Stripe para un servicio.
    """
    data = request.json
    service_id = data.get("service")
    user_id = data.get("userId")

    # Define el precio del servicio
    price_map = {
        "rapida": 200,
        "risoterapia": 1200,
        "horoscopo": 500
    }
    price_in_cents = price_map.get(service_id)

    if not price_in_cents:
        return jsonify({"error": "Invalid service"}), 400

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "unit_amount": price_in_cents,
                    "product_data": {
                        "name": f"Servicio de {service_id}",
                    },
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=request.url_root + "?success=true",
            cancel_url=request.url_root + "?canceled=true",
            # Aquí se guarda el userId en los metadatos de la sesión
            metadata={"user_id": user_id, "service_id": service_id}
        )
        return jsonify({"sessionId": checkout_session.id})
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    """
    Maneja eventos de Stripe, como la confirmación de pagos.
    """
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature")
    event = None

    try:
        # Aquí debes usar tu clave de webhook, no la clave secreta de la API
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET')
        )
    except ValueError as e:
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError as e:
        return jsonify({"error": "Invalid signature"}), 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        # Obtiene los metadatos que guardamos anteriormente
        user_id = session.get("metadata", {}).get("user_id")
        service_id = session.get("metadata", {}).get("service_id")

        if user_id and service_id:
            try:
                # La ruta de la base de datos se basa en el ID de la aplicación y el ID de usuario
                user_doc_ref = db.collection("artifacts").document(app_id).collection("users").document(user_id)
                
                # Desbloquea el servicio en Firestore
                user_doc_ref.set({
                    "paid_services": {
                        service_id: { "status": "unlocked", "timestamp": firestore.SERVER_TIMESTAMP }
                    }
                }, merge=True)
                print(f"Servicio {service_id} desbloqueado para el usuario {user_id}")
            except Exception as e:
                print(f"Error al actualizar Firestore: {e}")

    return jsonify({"success": True}), 200
