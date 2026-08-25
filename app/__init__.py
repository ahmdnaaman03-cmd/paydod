import os
from flask import Flask
from config import Config
from app.extensions import db

def create_app(test_config=None):
    app = Flask(__name__, template_folder='templates', static_folder='static')

    if test_config is None:
        app.config.from_object(Config)
    elif isinstance(test_config, dict):
        app.config.from_mapping(test_config)
    else:
        app.config.from_object(test_config)

    db.init_app(app)

    with app.app_context():
        from app.routes import main_bp, payments_bp
        app.register_blueprint(main_bp)
        app.register_blueprint(payments_bp)
        db.create_all()

    return app
