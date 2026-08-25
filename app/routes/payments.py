import uuid
from decimal import Decimal, InvalidOperation
from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models.payment import Payment
from app.services.stripe_service import StripeService
from app.services.qr_service import QRService

bp_payments = Blueprint('payments', __name__, url_prefix='/api/payments')

@bp_payments.route('/create', methods=['POST'])
def create_payment():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid or missing JSON'}), 400

    raw_amount = data.get('amount')
    currency = data.get('currency', 'USD')

    if raw_amount is None:
        return jsonify({'error': 'Amount is required'}), 400

    try:
        amount = Decimal(str(raw_amount))
    except (InvalidOperation, TypeError, ValueError):
        return jsonify({'error': 'Invalid amount format'}), 400

    if amount <= 0:
        return jsonify({'error': 'Amount must be greater than zero'}), 400

    id_reference_client = f"PAYDOD-{uuid.uuid4().hex[:12].upper()}"

    # Create payment record as PENDING
    payment = Payment(
        id_reference_client=id_reference_client,
        amount=amount,
        currency=currency.upper(),
        status='PENDING'
    )
    db.session.add(payment)
    db.session.commit()

    # Create Stripe Checkout Session
    try:
        checkout_data = StripeService.create_checkout_session(
            amount=amount,
            currency=currency.lower(),
            reference_id=id_reference_client
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
