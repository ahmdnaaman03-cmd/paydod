from flask import Flask
from config import Config
from app.extensions import db
from app.routes import payments_bp, webhooks_bp, main_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    app.register_blueprint(payments_bp)
    app.register_blueprint(webhooks_bp)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    return app
