import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///paydod.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APP_BASE_URL = os.environ.get(
        'APP_BASE_URL',
        'https://Ahmdnoaman.pythonanywhere.com'
    )
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
    PUSHER_APP_ID = os.environ.get('PUSHER_APP_ID', '')
    PUSHER_KEY = os.environ.get('PUSHER_KEY', '')
    PUSHER_SECRET = os.environ.get('PUSHER_SECRET', '')
    PUSHER_CLUSTER = os.environ.get('PUSHER_CLUSTER', 'eu')
