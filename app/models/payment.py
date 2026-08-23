from app.extensions import db
from datetime import datetime
import uuid

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    shipment_id = db.Column(db.String(100), nullable=False)
    shopify_order_id = db.Column(db.String(100), nullable=False)
    shopify_order_name = db.Column(db.String(100), nullable=False)
    amount_minor = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(3), default='EGP')
    
    stripe_checkout_session_id = db.Column(db.String(100), unique=True, nullable=True)
    stripe_payment_intent_id = db.Column(db.String(100), unique=True, nullable=True)
    
    # States
    payment_status = db.Column(db.String(20), default='PENDING') # PENDING, PAID, FAILED, EXPIRED
    shopify_sync_status = db.Column(db.String(20), default='NOT_STARTED') # NOT_STARTED, SYNCED, ERROR
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_error = db.Column(db.Text, nullable=True)
