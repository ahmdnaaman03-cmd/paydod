import os
import stripe
from flask import Blueprint, render_template, request, jsonify

main_bp = Blueprint('main', __name__)
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/api/payment-sessions', methods=['POST'])
def create_payment_session():
    try:
        data = request.get_json() or {}
        amount = data.get('amount')
        order_id = data.get('order_id')

        if not amount or not order_id:
            return jsonify({'error': 'المبلغ ورقم الطلب مطلوبين'}), 400

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'egp',
                    'product_data': {'name': f'طلب رقم {order_id}'},
                    'unit_amount': int(float(amount) * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            metadata={'order_id': order_id},
            success_url=request.host_url + 'success',
            cancel_url=request.host_url + 'cancel',
        )

        return jsonify({'checkout_url': session.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
