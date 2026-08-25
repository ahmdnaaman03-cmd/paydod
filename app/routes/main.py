from flask import Blueprint, jsonify, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('create_payment.html')

@main_bp.route('/pay/<public_id>')
def pay_view(public_id):
    payment = Payment.query.filter_by(public_id=public_id).first_or_404()
    return render_template('pay.html', payment=payment)

@main_bp.route('/api/payment-status/<public_id>')
def payment_status(public_id):
    payment = Payment.query.filter_by(public_id=public_id).first()
    if not payment:
        return jsonify({'error': 'Not found'}), 404
    return jsonify({'status': payment.payment_status}), 200

@main_bp.route('/success')
def success():
    return '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تم الدفع بنجاح - PayDOD</title>
    <style>
        body { margin: 0; padding: 20px; font-family: system-ui, -apple-system, sans-serif; background: #070a14; color: #fff; min-height: 100vh; display: flex; align-items: center; justify-content: center; box-sizing: border-box; }
        .card { background: rgba(15, 23, 42, 0.9); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 40px 24px; text-align: center; max-width: 400px; width: 100%; box-shadow: 0 20px 40px rgba(0,0,0,0.5); }
        .icon { font-size: 64px; margin-bottom: 16px; display: inline-block; animation: pop 0.4s ease; }
        h2 { font-size: 24px; color: #22c55e; margin: 0 0 10px 0; }
        p { color: #94a3b8; font-size: 15px; margin: 0 0 24px 0; line-height: 1.5; }
        .btn { display: block; width: 100%; padding: 14px; background: rgba(255,255,255,0.08); color: #00d4ff; text-decoration: none; border-radius: 10px; font-weight: bold; font-size: 14px; box-sizing: border-box; border: 1px solid rgba(0,212,255,0.2); }
        @keyframes pop { 0% { transform: scale(0.5); } 100% { transform: scale(1); } }
    </style>
</head>
<body>
    <div class="card">
        <div class="icon">✅</div>
        <h2>تمت عملية الدفع بنجاح!</h2>
        <p>تم استلام مبلغ الطلب بنجاح. يمكنك إغلاق هذه الصفحة أو العودة للمندوب.</p>
    </div>
</body>
</html>'''

@main_bp.route('/cancel')
def cancel():
    return '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تم إلغاء الدفع - PayDOD</title>
    <style>
        body { margin: 0; padding: 20px; font-family: system-ui, -apple-system, sans-serif; background: #070a14; color: #fff; min-height: 100vh; display: flex; align-items: center; justify-content: center; box-sizing: border-box; }
        .card { background: rgba(15, 23, 42, 0.9); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 40px 24px; text-align: center; max-width: 400px; width: 100%; box-shadow: 0 20px 40px rgba(0,0,0,0.5); }
        .icon { font-size: 64px; margin-bottom: 16px; display: inline-block; }
        h2 { font-size: 24px; color: #ef4444; margin: 0 0 10px 0; }
        p { color: #94a3b8; font-size: 15px; margin: 0; line-height: 1.5; }
    </style>
</head>
<body>
    <div class="card">
        <div class="icon">❌</div>
        <h2>تم إلغاء العملية</h2>
        <p>لم يتم خصم أي مبالغ. يمكنك العودة للمندوب وإعادة المحاولة.</p>
    </div>
</body>
</html>'''
