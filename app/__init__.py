import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # تحديد مسار ملف .env بدقة (المجلد الأب)
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.env'))
    load_dotenv(env_path)
    
    # إعدادات قاعدة البيانات والبيئة
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///paydod.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY')
    
    # تهيئة قاعدة البيانات
    db.init_app(app)
    
    # تسجيل المسارات
    from app.routes.main import main_bp
    from app.routes.webhooks import webhooks_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(webhooks_bp)

    return app
