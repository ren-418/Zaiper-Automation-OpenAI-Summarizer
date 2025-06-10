import unittest
from app import app
import json

class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page(self):
        """Test home page endpoint"""
        print("\n=== Testing Home Page ===")
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        print("✅ Home page test passed")

    def test_process_email(self):
        """Test email processing endpoint"""
        print("\n=== Testing Email Processing Endpoint ===")

        # Test data
        test_data = {
            "subject": "Test Email",
            "body": "This is a test email body.",
            "sender": "test@example.com"
        }

        # Test with valid data
        print("Testing with valid data...")
        response = self.app.post('/process_email',
                               data=json.dumps(test_data),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('summary', data)
        print("✅ Valid data test passed")

        # Test with invalid data
        print("\nTesting with invalid data...")
        response = self.app.post('/process_email',
                               data=json.dumps({}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)
        print("✅ Invalid data test passed")

    def test_webhook(self):
        """Test webhook endpoint"""
        print("\n=== Testing Webhook Endpoint ===")

        # Test data
        test_data = {
            "type": "email",
            "data": {
                "subject": "Webhook Test",
                "body": "Testing webhook functionality",
                "sender": "webhook@example.com"
            }
        }

        # Test with valid data
        print("Testing with valid data...")
        response = self.app.post('/webhook',
                               data=json.dumps(test_data),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        print("✅ Valid webhook test passed")

        # Test with invalid data
        print("\nTesting with invalid data...")
        response = self.app.post('/webhook',
                               data=json.dumps({}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)
        print("✅ Invalid webhook test passed")

if __name__ == '__main__':
    print("Starting Flask Application Tests...")
    unittest.main(verbosity=2)
