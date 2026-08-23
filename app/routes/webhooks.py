from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models.payment import Payment
from app.models.webhook_event import WebhookEvent
from app.services.pusher_service import PusherService
from datetime import datetime
import stripe

webhooks_bp = Blueprint('webhooks', __name__)

@webhooks_bp.route('/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')

    # قاعدة صارمة: الفشل مغلقاً في الإنتاج إذا غاب السر
    if not endpoint_secret:
        return jsonify({'error': 'Webhook secret is not configured'}), 500

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400

    event_id = event.get('id')
    event_type = event.get('type')

    # منع تكرار معالجة نفس الحدث (Idempotency)
    existing_event = WebhookEvent.query.filter_by(stripe_event_id=event_id).first()
    if existing_event and existing_event.processing_status == 'PROCESSED':
        return jsonify({'status': 'already_processed'}), 200

    if not existing_event:
        webhook_event = WebhookEvent(
            stripe_event_id=event_id,
            event_type=event_type,
            processing_status='PENDING'
        )
        db.session.add(webhook_event)
        db.session.commit()

    # معالجة اكتمال الدفع بنجاح
    if event_type == 'checkout.session.completed':
        session = event.get('data', {}).get('object', {})
        payment_public_id = session.get('client_reference_id')
        payment_intent_id = session.get('payment_intent')

        if payment_public_id:
            payment = Payment.query.filter_by(public_id=payment_public_id).first()
            if payment and payment.payment_status != 'PAID':
                payment.payment_status = 'PAID'
                payment.stripe_payment_intent_id = payment_intent_id
                payment.paid_at = datetime.utcnow()
                db.session.commit()

                # إرسال إشعار لحظي عبر Pusher لشاشة المندوب
                PusherService.notify_payment_status(payment.public_id, 'PAID')

    # تحديث حالة سجل الويب هوك إلى معالج بنجاح
    if not existing_event:
        webhook_event.processing_status = 'PROCESSED'
        webhook_event.processed_at = datetime.utcnow()
        db.session.commit()
    else:
        existing_event.processing_status = 'PROCESSED'
        existing_event.processed_at = datetime.utcnow()
        db.session.commit()

    return jsonify({'status': 'success'}), 200
