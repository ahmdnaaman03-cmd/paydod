import pusher
from flask import current_app

class PusherService:
    @staticmethod
    def get_client():
        return pusher.Pusher(
            app_id=current_app.config['PUSHER_APP_ID'],
            key=current_app.config['PUSHER_KEY'],
            secret=current_app.config['PUSHER_SECRET'],
            cluster=current_app.config['PUSHER_CLUSTER'],
            ssl=True
        )

    @staticmethod
    def notify_payment_status(payment_public_id, status):
        try:
            client = PusherService.get_client()
            channel_name = f'payment-{payment_public_id}'
            client.trigger(channel_name, 'status_update', {'status': status})
        except Exception as e:
            # يتم تسجيل الخطأ دون إيقاف الويب هوك
            print(f"Pusher notification failed: {str(e)}")
