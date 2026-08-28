import decimal
from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models import Payment
from app.services.qr_service import QRService
from app.services.stripe_service import StripeService

bp_payments = Blueprint('payments', __name__, url_prefix='/api')

@bp_payments.route('/payments/<int:payment_id>/status', methods=['GET'])
def payment_status(payment_id):
    payment = Payment.query.get(payment_id)
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    return jsonify({
        'success': True,
        'id_payment': payment.id,
        'id_reference_client': payment.id_reference_client,
        'status': payment.status,
        'paid_at': payment.paid_at.isoformat() if payment.paid_at else None
    }), 200


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

    existing_payment = Payment.query.filter_by(
        id_reference_client=id_reference_client
    ).first()
    if existing_payment:
        return jsonify({
            'error': 'Payment reference already exists',
            'message': 'Use a new shipment reference or continue the existing payment.',
            'id_payment': existing_payment.id,
            'id_reference_client': existing_payment.id_reference_client,
            'status': existing_payment.status
        }), 409

    payment = None
    try:
        payment = Payment(
            amount=amount,
            currency=currency,
            id_reference_client=id_reference_client,
            status='PENDING'
        )
        db.session.add(payment)
        db.session.flush()

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
        db.session.rollback()
        current_app.logger.error(f"Stripe session creation error: {str(e)}")
        return jsonify({'error': 'Stripe Gateway Error'}), 500
