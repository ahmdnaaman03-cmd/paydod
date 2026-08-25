from datetime import datetime
from app.extensions import db

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    id_reference_client = db.Column(db.String(100), unique=True, nullable=False)
    id_session_stripe = db.Column(db.String(255), unique=True, nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(10), default='USD', nullable=False)
    status = db.Column(db.String(50), default='PENDING', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime, nullable=True)
    stripe_payment_intent_id = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Payment {self.id_reference_client} - {self.status}>'
