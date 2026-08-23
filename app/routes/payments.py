from flask import Blueprint, request, jsonify, render_template
from app.extensions import db
from app.models.payment import Payment
from app.services.stripe_service import StripeService
from app.services.qr_service import QRService
from decimal import Decimal

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/api/payment-sessions', methods=['POST'])
def create_payment_session():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON payload'}), 400

        shopify_order_name = data.get('shopify_order_name')
        shipment_id = data.get('shipment_id')
        raw_amount = data.get('amount')

        if not shopify_order_name or not shipment_id or not raw_amount:
            return jsonify({'error': 'Missing required fields (shopify_order_name, shipment_id, amount)'}), 400

        # التحقق من دقة المبلغ باستخدام Decimal لمنع أخطاء float
        amount_decimal = Decimal(str(raw_amount))
        if amount_decimal <= 0:
            return jsonify({'error': 'Invalid amount'}), 400

        amount_minor = int(amount_decimal * 100)
        currency = 'EGP'

        # 1. إنشاء سجل مبدئي في قاعدة البيانات للحصول على معرف عام
        payment = Payment(
            shipment_id=shipment_id,
            shopify_order_id=shopify_order_name, # مؤقتاً لحين ربط شوبيفاي الكامل
            shopify_order_name=shopify_order_name,
            amount_minor=amount_minor,
            currency=currency,
            payment_status='PENDING'
        )
        db.session.add(payment)
        db.session.commit()

        # 2. إنشاء جلسة دفع Stripe باستخدام الـ public_id المعزول
        checkout_url, session_id = StripeService.create_checkout_session(
            payment_public_id=payment.public_id,
            amount_minor=amount_minor,
            currency=currency,
            shopify_order_name=shopify_order_name
        )

        # تحديث الجلسة برمز Stripe
        payment.stripe_checkout_session_id = session_id
        db.session.commit()

        # 3. توليد رمز الاستجابة السريعة (QR Code) لرابط الدفع
        qr_url = QRService.generate_qr_base64(checkout_url)

        return jsonify({
            'payment_id': payment.public_id,
            'checkout_url': checkout_url,
            'qr_url': qr_url,
            'amount': str(amount_decimal),
            'currency': currency,
            'status': payment.payment_status
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
