import os
from app import create_app
from app.extensions import db

# 1. تحديد مسار قاعدة البيانات
db_path = os.path.join(os.path.dirname(__file__), 'paydod.db')

# 2. حذف القاعدة القديمة إن وجدت
if os.path.exists(db_path):
    os.remove(db_path)
    print("🗑️ Deleted old paydod.db")

# 3. إقلاع التطبيق وإنشاء الجداول الجديدة
app = create_app()
with app.app_context():
    db.create_all()
    print("✅ Successfully created new database schema (Stores, Payments, WebhookEvents).")
