from flask import Flask, jsonify
from app.config import Config
from app.extensions import db
import stripe

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    
    stripe_key = app.config.get('STRIPE_SECRET_KEY')
    if stripe_key:
        stripe.api_key = stripe_key

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
