from flask import Blueprint, request, jsonify, current_app
import stripe
from app.extensions import db
from app.models.payment import Payment
from app.services.pusher_service import PusherService
from app.services.shopify_service import ShopifyService

bp_webhooks = Blueprint('webhooks', __name__, url_prefix='/api/webhooks')

@bp_webhooks.route('/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        reference_id = session.get('client_reference_id')

        if reference_id:
            payment = Payment.query.filter_by(id_reference_client=reference_id).first()
            if payment and payment.status != 'SUCCESS':
                # 1. تحديث قاعدة البيانات
                payment.status = 'SUCCESS'
                payment.id_session_stripe = session.get('id')
                db.session.commit()

                # 2. إطلاق إشعار لحظي لشاشة المندوب للتحول للأخضر
                PusherService.notify_payment_status(reference_id, 'SUCCESS')

                # 3. تحديث حالة الطلب في Shopify آلياً
                if payment.store_id:
                    ShopifyService.sync_order_status(reference_id, 'paid')

    return jsonify({'status': 'success'}), 200
