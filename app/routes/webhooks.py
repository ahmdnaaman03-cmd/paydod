from flask import Blueprint, request, jsonify, current_app
import stripe
from app.extensions import db
from app.models.payment import Payment
from app.services.shopify_service import ShopifyService

webhooks_bp = Blueprint('webhooks', __name__, url_prefix='/webhooks')

@webhooks_bp.route('/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')
    webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')

    try:
        if webhook_secret:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        else:
            data = request.get_json()
            event = data
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    if event.get('type') == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session)

    return jsonify({'status': 'success'}), 200


def handle_checkout_session(session):
    client_reference_id = session.get('client_reference_id')
    payment_intent_id = session.get('payment_intent')
    
    payment = None
    if client_reference_id:
        payment = Payment.query.get(client_reference_id)
    
    if not payment and session.get('id'):
        payment = Payment.query.filter_by(stripe_session_id=session.get('id')).first()
        
    if payment:
        payment.status = 'paid'
        payment.stripe_payment_intent_id = payment_intent_id
        
        # مزامنة شوبيفاي
        if payment.shopify_order_id:
            try:
                shopify_service = ShopifyService()
                success = shopify_service.mark_order_as_paid(payment.shopify_order_id)
                if success:
                    payment.shopify_sync_status = 'SYNCED'
                else:
                    payment.shopify_sync_status = 'FAILED'
            except Exception as e:
                current_app.logger.error(f"Shopify Sync Error: {e}")
                payment.shopify_sync_status = 'FAILED'
                
        db.session.commit()
