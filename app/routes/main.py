from flask import Blueprint, render_template, request, jsonify
from app import db
from app.models.payment import Payment

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/success')
def success():
    session_id = request.args.get('session_id')
    if session_id:
        payment = Payment.query.filter_by(stripe_checkout_session_id=session_id).first()
        if payment:
            payment.payment_status = 'paid'
            db.session.commit()
            
    return render_template('success.html', session_id=session_id)

@main_bp.route('/cancel')
def cancel():
    return render_template('cancel.html')

@main_bp.route('/api/payments/<public_id>/status', methods=['GET'])
def get_payment_status(public_id):
    payment = Payment.query.filter_by(public_id=public_id).first()
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    
    return jsonify({
        'payment_id': payment.public_id,
        'status': payment.payment_status,
        'shopify_sync_status': payment.shopify_sync_status,
        'amount': str(payment.amount_minor / 100),
        'currency': payment.currency
    }), 200
