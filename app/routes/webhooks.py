import stripe
from flask import Blueprint, request, jsonify
from app.db import get_db

webhooks_bp = Blueprint('webhooks', __name__)

@webhooks_bp.route('/stripe/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe.webhook_secret
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        public_id = session.get('client_reference_id')
        if public_id:
            db = get_db()
            db.execute(
                "UPDATE payments SET payment_status = 'paid' WHERE public_id = ?",
                (public_id,)
            )
            db.commit()
            print(f"Payment success recorded for public_id: {public_id}")
        else:
            print("Error: client_reference_id not found in Stripe session")

    return jsonify({'status': 'success'}), 200
