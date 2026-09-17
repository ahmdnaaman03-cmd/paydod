from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        db.session.execute(text("ALTER TABLE payments ADD COLUMN store_id VARCHAR(255);"))
        db.session.commit()
        print("✅ تمت إضافة عمود store_id بنجاح لقاعدة البيانات!")
    except Exception as e:
        print("⚠️ ملاحظة (العمود قد يكون موجوداً أو حدث خطأ):", e)
