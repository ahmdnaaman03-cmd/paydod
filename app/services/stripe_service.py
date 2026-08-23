import stripe
from flask import current_app

class StripeService:
    @staticmethod
    def create_checkout_session(payment_public_id, amount_minor, currency, shopify_order_name):
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        
        # استخدام المتغير الثابت {CHECKOUT_SESSION_ID} كما تتطلب Stripe
        success_url = f"{current_app.config['APP_BASE_URL']}/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{current_app.config['APP_BASE_URL']}/cancel"

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': currency.lower(),
                    'product_data': {
                        'name': f'Pay DOD - Order {shopify_order_name}',
                    },
                    'unit_amount': amount_minor,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=payment_public_id,
            metadata={
                'payment_public_id': payment_public_id,
                'shopify_order_name': shopify_order_name
            }
        )
        return session.url, session.id
