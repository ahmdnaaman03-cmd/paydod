import os
from flask import Flask
from dotenv import load_dotenv

# تحميل ملف .env صراحة من مسار المشروع
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '../.env'))

def create_app():
    app = Flask(__name__)
    
    # ربط المفتاح بالـ Config
    app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY')
    
    from app.routes.main import main_bp
    from app.routes.webhooks import webhooks_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(webhooks_bp)

    return app
