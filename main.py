import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import os
import stripe

# Initialize the Flask application
app = Flask(__name__)
# Enable CORS for all domains, which is necessary for the frontend to communicate with the backend
CORS(app)

# IMPORTANT: SET YOUR STRIPE SECRET KEY HERE OR, BETTER, AS AN ENVIRONMENT VARIABLE
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "sk_test_tu_clave_secreta_aqui")

# IMPORTANT: SET YOUR STRIPE WEBHOOK SECRET HERE
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_tu_clave_de_webhook_aqui")

# Initialize Firebase Admin SDK
# The __firebase_config variable is provided by the canvas environment
# This allows the backend to securely access your Firestore database.
try:
    firebase_config = os.environ.get("__firebase_config")
    if firebase_config:
        cred = credentials.Certificate(firestore.config.json.loads(firebase_config))
        firebase_admin.initialize_app(cred)
    else:
        print("Error: __firebase_config environment variable not found.")
        exit(1)
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    exit(1)

db = firestore.client()

# Data for service pricing, defined in cents for Stripe compatibility
SERVICES = {
    "risoterapia": {"name": "Risoterapia y Bienestar", "price": 1200}, # $12.00 USD
    "horoscopo": {"name": "Horóscopo / Zodiaco", "price": 500}, # $5.00 USD
    "rapida": {"name": "Agente de Respuesta Rápida", "price": 200}, # $2.00 USD
}

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    """
    Handles the request to create a real Stripe checkout session.
    """
    try:
        data = request.get_json()
        service_id = data.get("service")
        user_id = data.get("userId") # We now receive the userId from the frontend
        
        if service_id not in SERVICES:
            return jsonify({"error": "Service not found"}), 404

        service_info = SERVICES[service_id]

        # Create a real Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": service_info["name"],
                    },
                    "unit_amount": service_info["price"],
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=request.host_url + 'success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.host_url,
            # Pass the user_id into the session metadata so we can use it in the webhook
            metadata={"user_id": user_id},
        )

        return jsonify({"sessionId": checkout_session.id})

    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    """
    Stripe calls this endpoint when a payment event occurs.
    This is where el sistema sabe que pagó.
    """
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    event = None

    try:
        # Verify that the webhook event is coming from Stripe.
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return "Invalid signature", 400

    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        
        # --- Lógica de Negocio: EL SISTEMA SABE QUE PAGÓ ---
        # 1. Get the userId from the session metadata
        user_id = session.get("metadata", {}).get("user_id")
        
        if not user_id:
            print("Error: user_id not found in session metadata.")
            return "Missing user_id", 400

        # 2. Get the name of the service from the session
        line_items = stripe.checkout.Session.list_line_items(session.id, limit=1)
        product_name = line_items["data"][0]["price"]["product_data"]["name"]
        
        print(f"✅ ¡Pago exitoso para el usuario {user_id}! El usuario compró: {product_name}")

        # 3. Update the user's document in Firestore with the payment details
        #    This is the core of the final step you asked for.
        try:
            doc_ref = db.collection("artifacts").document(os.environ.get("__app_id")).collection("users").document(user_id)
            doc_ref.set({
                "paid_services": {
                    product_name.lower().replace(" ", ""): {
                        "status": "unlocked",
                        "last_payment_timestamp": firestore.SERVER_TIMESTAMP
                    }
                }
            }, merge=True)
            print("✅ Firestore actualizado con éxito.")
        except Exception as e:
            print(f"Error updating Firestore: {e}")
            return "Firestore update failed", 500

    elif event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        print(f"✅ El PaymentIntent fue exitoso: {payment_intent['id']}")

    elif event["type"] == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        print(f"❌ El PaymentIntent falló: {payment_intent['id']}")

    else:
        print(f"Unhandled event type: {event['type']}")

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
