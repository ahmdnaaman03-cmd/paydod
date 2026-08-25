import unittest
from app import create_app
from app.extensions import db
from app.models.payment import Payment

class PayDODTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_app_initialization(self):
        self.assertIsNotNone(self.app)

    def test_index_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_create_payment_invalid_json(self):
        response = self.client.post('/api/payments/create', json={})
        self.assertEqual(response.status_code, 400)

    def test_create_payment_negative_amount(self):
        response = self.client.post('/api/payments/create', json={'amount': -10, 'currency': 'USD'})
        self.assertEqual(response.status_code, 400)

    def test_webhook_missing_signature(self):
        response = self.client.post('/api/webhooks/stripe', json={})
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
