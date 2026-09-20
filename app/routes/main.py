from flask import Blueprint, render_template, request, redirect, url_for, current_app
import traceback
from app.models.payment import Payment
from app.models.store import Store

bp_main = Blueprint('main', __name__)

@bp_main.route('/')
def index():
    try:
        shop = request.args.get('shop')
        host = request.args.get('host')
        
        if shop and host:
            store = Store.query.filter_by(shop_url=shop).first()
            if store:
                return redirect(url_for('main.merchant_dashboard', store_id=store.id, host=host))
            else:
                return redirect(url_for('auth.install', shop=shop))
                
        return render_template('index.html')
    except Exception as e:
        return f"<pre>Index Error:\n{traceback.format_exc()}</pre>", 500

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

@bp_main.route('/merchant/dashboard/<int:store_id>')
def merchant_dashboard(store_id):
    try:
        payments = Payment.query.filter_by(store_id=store_id).all()
        api_key = current_app.config.get('SHOPIFY_API_KEY')
        return render_template('merchant_dashboard.html', store_id=store_id, payments=payments, api_key=api_key)
    except Exception as e:
        return f"<pre>Dashboard Error:\n{traceback.format_exc()}</pre>", 500
