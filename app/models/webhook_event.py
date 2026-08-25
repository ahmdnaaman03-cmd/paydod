from datetime import datetime
from app.extensions import db

class WebhookEvent(db.Model):
    __tablename__ = 'webhook_events'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.String(255), unique=True, nullable=False)
    event_type = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default='PROCESSED', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<WebhookEvent {self.event_id} - {self.event_type}>'
