import unittest
from datetime import datetime
import os
from dotenv import load_dotenv
import requests
import json
from main import app
from fastapi.testclient import TestClient

load_dotenv()

class TestEmailProcessing(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.NOTION_KEY = os.getenv("NOTION_KEY")
        self.NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

    def test_environment_variables(self):
        """Test if all required environment variables are set"""
        self.assertIsNotNone(os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY is not set")
        self.assertIsNotNone(self.NOTION_KEY, "NOTION_KEY is not set")
        self.assertIsNotNone(self.NOTION_DATABASE_ID, "NOTION_DATABASE_ID is not set")

    def test_newsletter_detection(self):
        """Test if the system correctly identifies newsletters"""
        # Test with obvious newsletter
        response = self.client.post("/", json={
            "from_email": "newsletter@test.com",
            "content": """
            Weekly Newsletter
            Here are this week's updates...
            """
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Check if we got an error response
        if "error" in data["status"]:
            # If it's a geographical restriction error, skip the test
            if "unsupported_country_region_territory" in str(data):
                self.skipTest("Skipping test due to geographical API restrictions")
            else:
                self.fail(f"Unexpected error: {data['message']}")
        else:
            self.assertIn("Newsletter", str(data))

        # Test with non-newsletter
        response = self.client.post("/", json={
            "from_email": "user@test.com",
            "content": "Can you review this PR?"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        if "error" not in data["status"]:
            self.assertNotIn("Newsletter", str(data))

    def test_notion_integration(self):
        """Test if Notion API integration is working"""
        headers = {
            "Authorization": f"Bearer {self.NOTION_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

        # Test database access
        response = requests.get(
            f"https://api.notion.com/v1/databases/{self.NOTION_DATABASE_ID}",
            headers=headers
        )
        self.assertEqual(response.status_code, 200)

    def test_long_content(self):
        """Test handling of long email content"""
        long_content = "Test content\n" * 1000
        response = self.client.post("/", json={
            "from_email": "test@test.com",
            "content": long_content
        })
        self.assertEqual(response.status_code, 200)

    def test_invalid_requests(self):
        """Test handling of invalid requests"""
        # Missing content
        response = self.client.post("/", json={
            "from_email": "test@test.com"
        })
        self.assertEqual(response.status_code, 422)

        # Missing email
        response = self.client.post("/", json={
            "content": "test content"
        })
        self.assertEqual(response.status_code, 422)

    def test_api_endpoint(self):
        """Test if the API endpoint is responsive"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"Hello": "World"})

if __name__ == '__main__':
    unittest.main()