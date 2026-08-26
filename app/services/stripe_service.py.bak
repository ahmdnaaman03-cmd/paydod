import stripe
from flask import current_app

class StripeService:
    @staticmethod
    def create_checkout_session(amount, currency, reference_id):
        stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')
        
        # Convert amount to smallest currency unit (e.g., cents)
        unit_amount = int(amount * 100)

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': currency,
                    'product_data': {
                        'name': f'Order {reference_id}',
                    },
                    'unit_amount': unit_amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://localhost:5000/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:5000/cancel',
            metadata={
                'id_reference_client': reference_id
            }
        )

        return {
            'session_id': session.id,
            'checkout_url': session.url
        }
