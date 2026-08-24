import stripe
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Payment

webhooks_bp = Blueprint('webhooks', __name__, url_prefix='/webhooks')

@webhooks_bp.route('/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')

    try:
        if endpoint_secret:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        else:
            event = stripe.Event.construct_from(request.get_json(), stripe.api_key)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session.get('id')
        
        payment = Payment.query.filter_by(stripe_checkout_session_id=session_id).first()
        if payment:
            payment.payment_status = 'paid'
            db.session.commit()

    return jsonify({'status': 'success'}), 200
