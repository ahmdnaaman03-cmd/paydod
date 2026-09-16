import sqlite3
try:
    conn = sqlite3.connect('paydod.db')
    conn.execute("ALTER TABLE payments ADD COLUMN store_id VARCHAR(255);")
    conn.commit()
    print("تمت الاضافة بنجاح!")
except Exception as e:
    print("ملاحظة:", e)
finally:
    conn.close()
