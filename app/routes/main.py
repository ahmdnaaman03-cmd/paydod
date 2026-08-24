import stripe
from flask import Blueprint, jsonify, request, url_for
from app.db import get_db

main_bp = Blueprint('main', __name__)

@main_bp.route('/api/create-checkout-session', methods=['POST'])
def create_checkout_session():
    data = request.get_json() or {}
    public_id = data.get('public_id')
    amount = data.get('amount')
    
    if not public_id or not amount:
        return jsonify({'error': 'Missing public_id or amount'}), 400
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'egp',
                    'product_data': {'name': f'Order {public_id}'},
                    'unit_amount': int(float(amount) * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            client_reference_id=public_id,
            success_url=url_for('main.success', _external=True),
            cancel_url=url_for('main.cancel', _external=True),
        )
        
        db = get_db()
        db.execute(
            "UPDATE payments SET stripe_checkout_session_id = ? WHERE public_id = ?",
            (session.id, public_id)
        )
        db.commit()
        return jsonify({'checkout_url': session.url, 'session_id': session.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/payments/<public_id>/status', methods=['GET'])
def get_payment_status(public_id):
    db = get_db()
    row = db.execute(
        "SELECT payment_status FROM payments WHERE public_id = ?",
        (public_id,)
    ).fetchone()
    
    if not row:
        return jsonify({'error': 'Payment not found'}), 404
        
    return jsonify({'public_id': public_id, 'status': row['payment_status']})

@main_bp.route('/success')
def success():
    return jsonify({'status': 'success'})

@main_bp.route('/cancel')
def cancel():
    return jsonify({'status': 'cancelled'})
