import decimal
import traceback
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.payment import Payment
from app.services.qr_service import QRService
from app.services.stripe_service import StripeService

bp_payments = Blueprint('payments', __name__, url_prefix='/api')

@bp_payments.route('/payments/create', methods=['POST'])
def create_payment():
    try:
        data = request.get_json() or {}
        amount_raw = data.get('amount')
        id_reference_client = data.get('id_reference_client')
        store_id = data.get('store_id')

        if not amount_raw or not id_reference_client:
            return jsonify({'error': 'Missing amount or reference'}), 400

        if not store_id:
            return jsonify({'error': 'عذراً، يجب إرسال معرف المتجر'}), 400

        amount = decimal.Decimal(str(amount_raw))
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400

        payment = Payment.query.filter_by(id_reference_client=id_reference_client).first()
        if not payment:
            payment = Payment(
                amount=amount,
                currency=data.get('currency', 'EGP'),
                id_reference_client=id_reference_client,
                status='PENDING',
                store_id=store_id
            )
            db.session.add(payment)
            db.session.commit()
        elif payment.status == 'SUCCESS':
            return jsonify({'error': 'Order already paid'}), 400
        else:
            payment.amount = amount
            db.session.commit()

        checkout_data = StripeService.create_checkout_session(
            amount=amount,
            currency='EGP',
            reference=id_reference_client
        )
        
        qr_code_data = QRService.generate_qr_data_url(checkout_data['checkout_url'])

        return jsonify({
            'checkout_url': checkout_data['checkout_url'],
            'qr_code': qr_code_data
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Payment Error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500
