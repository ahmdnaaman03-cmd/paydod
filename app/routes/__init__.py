from app.routes.main import bp_main as main_bp
from app.routes.payments import bp_payments as payments_bp
from app.routes.webhooks import bp_webhooks as webhooks_bp

__all__ = ['main_bp', 'payments_bp', 'webhooks_bp']
