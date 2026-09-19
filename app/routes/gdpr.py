import hmac
import hashlib
import base64
from flask import Blueprint, request, jsonify, current_app

bp_gdpr = Blueprint('gdpr', __name__, url_prefix='/webhooks/gdpr')

def verify_shopify_webhook(data, hmac_header):
    secret = current_app.config['SHOPIFY_API_SECRET'].encode('utf-8')
    digest = hmac.new(secret, data, hashlib.sha256).digest()
    computed_hmac = base64.b64encode(digest).decode('utf-8')
    return hmac.compare_digest(computed_hmac, hmac_header)

@bp_gdpr.route('/customers/data_request', methods=['POST'])
def customers_data_request():
    # الاستجابة الإلزامية لطلب Shopify بعرض بيانات العميل
    return jsonify({"message": "Data request processed"}), 200

@bp_gdpr.route('/customers/redact', methods=['POST'])
def customers_redact():
    # الاستجابة الإلزامية لطلب Shopify بمسح بيانات العميل
    return jsonify({"message": "Customer redacted"}), 200

@bp_gdpr.route('/shop/redact', methods=['POST'])
def shop_redact():
    # الاستجابة الإلزامية لطلب Shopify بمسح بيانات المتجر
    return jsonify({"message": "Shop redacted"}), 200
