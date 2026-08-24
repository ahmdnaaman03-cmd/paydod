import requests
import stripe
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models import Payment

webhooks_bp = Blueprint('webhooks', __name__)

def update_shopify_order(shopify_order_id, shop_url, access_token):
    if not shopify_order_id or not shop_url or not access_token:
        return False
    url = f"https://{shop_url}/admin/api/2024-01/graphql.json"
    headers = {"Content-Type": "application/json", "X-Shopify-Access-Token": access_token}
    gid = f"gid://shopify/Order/{shopify_order_id}" if not str(shopify_order_id).startswith("gid://") else shopify_order_id
    mutation = """
    mutation orderMarkAsPaid($input: OrderMarkAsPaidInput!) {
        orderMarkAsPaid(input: $input) { order { id } }
    }
    """
    try:
        res = requests.post(url, json={'query': mutation, 'variables': {"input": {"id": gid}}}, headers=headers, timeout=10)
        return res.status_code == 200
    except:
        return False

@webhooks_bp.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']

    try:
        if endpoint_secret:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        else:
            event = stripe.Event.construct_from(request.get_json(), stripe.api_key)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        public_id = session.get('client_reference_id') or session.get('metadata', {}).get('public_id')
        session_id = session.get('id')

        payment = Payment.query.filter((Payment.public_id == public_id) | (Payment.stripe_checkout_session_id == session_id)).first()

        if payment:
            payment.payment_status = 'paid'
            if not payment.stripe_checkout_session_id and session_id:
                payment.stripe_checkout_session_id = session_id
            db.session.commit()

            shop_url = getattr(payment, 'shopify_domain', None) or current_app.config.get('SHOPIFY_SHOP_URL')
            access_token = getattr(payment, 'shopify_token', None) or current_app.config.get('SHOPIFY_ACCESS_TOKEN')
            update_shopify_order(getattr(payment, 'order_id', None), shop_url, access_token)

            return jsonify({'status': 'success'}), 200

    return jsonify({'status': 'ignored'}), 200
