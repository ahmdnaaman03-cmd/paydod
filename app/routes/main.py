from flask import Blueprint, jsonify, render_template, request, current_app
from app.extensions import db
from app.models import Payment

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return jsonify({'status': 'online', 'service': 'PayDOD API'}), 200

@main_bp.route('/pay/<public_id>')
def pay_view(public_id):
    payment = Payment.query.filter_by(public_id=public_id).first_or_404()
    return jsonify({
        'public_id': payment.public_id,
        'amount': payment.amount,
        'currency': payment.currency,
        'status': payment.payment_status
    }), 200

@main_bp.route('/api/payment-status/<public_id>')
def payment_status(public_id):
    payment = Payment.query.filter_by(public_id=public_id).first()
    if not payment:
        return jsonify({'error': 'Not found'}), 404
    return jsonify({'status': payment.payment_status}), 200
