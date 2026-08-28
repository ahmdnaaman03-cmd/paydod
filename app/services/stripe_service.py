import os
import stripe
from flask import current_app

class StripeService:
    @staticmethod
    def get_stripe_key():
        key = os.environ.get('STRIPE_SECRET_KEY') or current_app.config.get('STRIPE_SECRET_KEY')
        if not key:
            raise ValueError("STRIPE_SECRET_KEY is missing from environment/config")
        return key

    @classmethod
    def create_checkout_session(cls, amount, currency='EGP', reference=''):
        stripe.api_key = cls.get_stripe_key()
        base_url = os.environ.get('APP_BASE_URL', 'https://Ahmdnoaman.pythonanywhere.com')
        
        unit_amount = int(round(float(amount) * 100))
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': currency.lower(),
                    'product_data': {
                        'name': f'Payment Ref: {reference}',
                    },
                    'unit_amount': unit_amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            metadata={
                'id_reference_client': reference,
            },
            success_url=f"{base_url}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{base_url}/cancel?session_id={{CHECKOUT_SESSION_ID}}",
            client_reference_id=reference,
        )
        return {
            'session_id': session.id,
            'checkout_url': session.url
        }
