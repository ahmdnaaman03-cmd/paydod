from app.extensions import db
from datetime import datetime

class WebhookEvent(db.Model):
    __tablename__ = 'webhook_events'
    
    id = db.Column(db.Integer, primary_key=True)
    stripe_event_id = db.Column(db.String(100), unique=True, nullable=False)
    event_type = db.Column(db.String(100), nullable=False)
    
    processing_status = db.Column(db.String(20), default='PENDING') # PENDING, PROCESSED, ERROR
    processed_at = db.Column(db.DateTime, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
