import os
from dotenv import load_dotenv

load_dotenv()
# تحديد المسار الجذري للمشروع بدقة
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-fallback-secret-key'
    APP_ENV = os.environ.get('APP_ENV', 'development')
    APP_BASE_URL = os.environ.get('APP_BASE_URL', 'https://Ahmdnoaman.pythonanywhere.com')

    # فرض إنشاء وقراءة قاعدة البيانات من المسار الجذري فقط
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'paydod.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    STRIPE_CURRENCY = os.environ.get('STRIPE_CURRENCY', 'egp')

    SHOPIFY_API_KEY = os.environ.get('SHOPIFY_API_KEY')
    SHOPIFY_API_SECRET = os.environ.get('SHOPIFY_API_SECRET')
    SHOPIFY_API_VERSION = os.environ.get('SHOPIFY_API_VERSION', '2024-01')

    PUSHER_APP_ID = os.environ.get('PUSHER_APP_ID')
    PUSHER_KEY = os.environ.get('PUSHER_KEY')
    PUSHER_SECRET = os.environ.get('PUSHER_SECRET')
    PUSHER_CLUSTER = os.environ.get('PUSHER_CLUSTER', 'eu')
