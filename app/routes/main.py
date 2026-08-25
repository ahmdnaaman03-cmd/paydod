from flask import Blueprint, render_template, request
from app.models.payment import Payment

bp_main = Blueprint('main', __name__)

@bp_main.route('/')
def index():
    return render_template('index.html')

@bp_main.route('/success')
def success():
    session_id = request.args.get('session_id')
    payment = None
    if session_id:
        payment = Payment.query.filter_by(id_session_stripe=session_id).first()
    return render_template('success.html', payment=payment)

@bp_main.route('/cancel')
def cancel():
    return render_template('cancel.html')
