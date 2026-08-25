import requests
from flask import current_app

class ShopifyService:
    @staticmethod
    def sync_order_status(order_id, status):
        shop_url = current_app.config.get('SHOPIFY_SHOP_URL')
        access_token = current_app.config.get('SHOPIFY_ACCESS_TOKEN')

        if not shop_url or not access_token:
            current_app.logger.info(f"[Shopify Mock] Order {order_id} status updated to {status} (Credentials not provided)")
            return {'status': 'mocked', 'order_id': order_id, 'payment_status': status}

        # Real API sync implementation (limited for MVP)
        api_version = '2023-10'
        url = f"https://{shop_url}/admin/api/{api_version}/orders/{order_id}.json"
        headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }
        
        payload = {
            "order": {
                "id": order_id,
                "financial_status": "paid" if status == 'PAID' else "pending"
            }
        }

        try:
            response = requests.put(url, json=payload, headers=headers, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Shopify sync failed: {str(e)}")
            return {'error': str(e)}
