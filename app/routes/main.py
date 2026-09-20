from flask import Blueprint, render_template, request, redirect, url_for, current_app
from app.models.payment import Payment
from app.models.store import Store

bp_main = Blueprint('main', __name__)

@bp_main.route('/')
def index():
    shop = request.args.get('shop')
    host = request.args.get('host')
    
    # 1. إذا كان الزائر هو التاجر من داخل لوحة تحكم Shopify
    if shop and host:
        store = Store.query.filter_by(shop_url=shop).first()
        if store:
            # توجيه التاجر إلى لوحة المراقبة الخاصة به مع الحفاظ على إطار App Bridge
            return redirect(url_for('main.merchant_dashboard', store_id=store.id, host=host))
        else:
            # إذا لم يكن المتجر مسجلاً في قاعدة البيانات، نوجهه لمسار المصادقة
            return redirect(url_for('auth.install', shop=shop))
            
    # 2. إذا كان الزائر هو المندوب (لا يوجد متغيرات Shopify في الرابط)
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

@bp_main.route('/merchant/dashboard/<store_id>')
def merchant_dashboard(store_id):
    payments = Payment.query.filter_by(store_id=store_id).all()
    api_key = current_app.config.get('SHOPIFY_API_KEY')
    return render_template('merchant_dashboard.html', store_id=store_id, payments=payments, api_key=api_key)
