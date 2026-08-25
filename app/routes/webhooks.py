import os
import stripe
from flask import Blueprint, request, jsonify
from app import db
from app.models import Payment

webhooks_bp = Blueprint('webhooks', __name__)

@webhooks_bp.route('/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

    event = None
    try:
        if endpoint_secret:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        else:
            event = request.get_json(force=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    # معالجة إشعار اكتدال الدفع
    event_type = event.get('type') if isinstance(event, dict) else event.type
    if event_type in ['checkout.session.completed', 'payment_intent.succeeded']:
        data_obj = event['data']['object'] if isinstance(event, dict) else event.data.object
        
        # استخراج public_id المرفق في metadata
        metadata = data_obj.get('metadata', {})
        public_id = metadata.get('payment_public_id')
        
        payment = None
        if public_id:
            payment = Payment.query.filter_by(public_id=public_id).first()
        
        if not payment and 'id' in data_obj:
            payment = Payment.query.filter_by(stripe_session_id=data_obj['id']).first()

        if payment:
            payment.payment_status = 'COMPLETED'
            db.session.commit()
            print(f"✅ SUCCESS: Payment {payment.public_id} updated to COMPLETED")

    return jsonify({'status': 'success'}), 200
