from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
import stripe

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    stripe.api_key = app.config['STRIPE_SECRET_KEY']

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "version": "1.0.0"}), 200

    from app.routes.main import bp_main
    from app.routes.payments import bp_payments
    from app.routes.auth import bp_auth
    from app.routes.gdpr import bp_gdpr
    
    app.register_blueprint(bp_main)
    app.register_blueprint(bp_payments)
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_gdpr)

    return app
