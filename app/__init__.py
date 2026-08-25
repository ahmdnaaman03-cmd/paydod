from flask import Flask
from app.extensions import db
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from app.routes.main import bp_main
    from app.routes.payments import bp_payments
    from app.routes.webhooks import bp_webhooks

    app.register_blueprint(bp_main)
    app.register_blueprint(bp_payments)
    app.register_blueprint(bp_webhooks)

    return app
