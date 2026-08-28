from datetime import datetime
from decimal import Decimal
from flask import Blueprint, request, jsonify, current_app
import stripe
from app.extensions import db
from app.models.payment import Payment
from app.models.webhook_event import WebhookEvent
from app.services.pusher_service import PusherService

bp_webhooks = Blueprint('webhooks', __name__, url_prefix='/api/webhooks')

@bp_webhooks.route('/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')

    if not sig_header:
        return jsonify({'error': 'Missing Stripe-Signature header'}), 400

    if not webhook_secret:
        return jsonify({'error': 'Webhook secret is not configured'}), 500

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400

    event_id = event.get('id')
    event_type = event.get('type')

    # Idempotency check: ensure event hasn't been processed already
    existing_event = WebhookEvent.query.filter_by(event_id=event_id).first()
    if existing_event:
        return jsonify({'status': 'Event already processed'}), 200

    # Handle checkout session completed event
    if event_type == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session.get('id')
        metadata = session.get('metadata') or {}
        reference_id = metadata.get('id_reference_client')
        if not reference_id:
            reference_id = session.get('client_reference_id')
        payment_intent_id = session.get('payment_intent')

        payment = Payment.query.filter_by(id_reference_client=reference_id).first()
        if payment and payment.status != 'PAID':
            payment.status = 'PAID'
            payment.paid_at = datetime.utcnow()
            payment.stripe_payment_intent_id = payment_intent_id
            if not payment.id_session_stripe:
                payment.id_session_stripe = session_id
            db.session.commit()
            PusherService.notify_payment_status(payment.id, payment.status)

    # Record the processed event
    webhook_record = WebhookEvent(
        event_id=event_id,
        event_type=event_type,
        status='PROCESSED'
    )
    db.session.add(webhook_record)
    db.session.commit()

    return jsonify({'status': 'success'}), 200
