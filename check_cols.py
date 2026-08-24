from app import create_app, db
from app.models import Payment
app = create_app()
with app.app_context():
    print("COLUMNS:", [c.name for c in Payment.__table__.columns])
