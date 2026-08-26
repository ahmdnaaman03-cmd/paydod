import decimal
import stripe
from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models import Payment
from app.services.qr_service import QRService
from app.services.stripe_service import StripeService

bp_payments = Blueprint('payments', __name__, url_prefix='/api')

@bp_payments.route('/payments/create', methods=['POST'])
def create_payment():
    data = request.get_json() or {}
    amount_raw = data.get('amount')
    
    if not amount_raw:
        return jsonify({'error': 'Invalid amount'}), 400

    try:
        amount = decimal.Decimal(str(amount_raw))
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
    except (ValueError, TypeError, decimal.InvalidOperation):
        return jsonify({'error': 'Invalid amount format'}), 400

    currency = data.get('currency', 'EGP')
    id_reference_client = data.get('id_reference_client', 'REF-TEST')

    try:
        payment = Payment(
            amount=amount,
            currency=currency,
            id_reference_client=id_reference_client,
            status='PENDING'
        )
        db.session.add(payment)
        db.session.commit()

        checkout_data = StripeService.create_checkout_session(
            amount=amount,
            currency=currency,
            reference=id_reference_client
        )
        payment.id_session_stripe = checkout_data.get('session_id')
        db.session.commit()

        checkout_url = checkout_data.get('checkout_url')
        qr_url = QRService.generate_qr_data_url(checkout_url)

        return jsonify({
            'success': True,
            'id_payment': payment.id,
            'id_reference_client': id_reference_client,
            'url_checkout': checkout_url,
            'url_qr': qr_url,
            'amount': str(amount),
            'currency': payment.currency,
            'status': payment.status
        }), 201

    except Exception as e:
        current_app.logger.error(f"Stripe session creation error: {str(e)}")
        return jsonify({'error': 'Unable to initialize payment gateway'}), 500


@bp_payments.route('/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    sig_header = request.headers.get('Stripe-Signature')
    if not sig_header:
        return jsonify({'error': 'Missing signature'}), 400

    payload = request.get_data(as_text=True)
    webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET', '')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    except Exception:
        return jsonify({'error': 'Webhook verification failed'}), 400

    return jsonify({'status': 'success'}), 200
