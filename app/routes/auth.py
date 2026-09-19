import requests
from flask import Blueprint, request, redirect, current_app
from app.extensions import db
from app.models.store import Store

bp_auth = Blueprint('auth', __name__, url_prefix='/auth')

@bp_auth.route('/install', methods=['GET'])
def install():
    shop = request.args.get('shop')
    if not shop:
        return "Missing shop parameter", 400
    
    # الصلاحيات المطلوبة للتطبيق
    scopes = "read_orders,write_orders"
    redirect_uri = f"{current_app.config['APP_BASE_URL']}/auth/callback"
    client_id = current_app.config['SHOPIFY_API_KEY']
    
    auth_url = f"https://{shop}/admin/oauth/authorize?client_id={client_id}&scope={scopes}&redirect_uri={redirect_uri}"
    return redirect(auth_url)

@bp_auth.route('/callback', methods=['GET'])
def callback():
    shop = request.args.get('shop')
    code = request.args.get('code')
    if not shop or not code:
        return "Missing parameters", 400
    
    client_id = current_app.config['SHOPIFY_API_KEY']
    client_secret = current_app.config['SHOPIFY_API_SECRET']
    
    token_url = f"https://{shop}/admin/oauth/access_token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code
    }
    
    response = requests.post(token_url, json=payload)
    if response.status_code == 200:
        access_token = response.json().get('access_token')
        
        # حفظ أو تحديث بيانات المتجر في قاعدة البيانات
        store = Store.query.filter_by(shop_url=shop).first()
        if not store:
            store = Store(shop_url=shop, access_token=access_token)
            db.session.add(store)
        else:
            store.access_token = access_token
        db.session.commit()
        
        # إشعار نجاح مؤقت (سيتم تحويله لاحقاً للوحة التحكم المدمجة)
        return f"✅ تم ربط تطبيق PayDOD بنجاح لمتجر {shop}. يمكنك العودة إلى لوحة تحكم Shopify."
    
    return "❌ فشل الحصول على رمز الدخول من Shopify", 500
