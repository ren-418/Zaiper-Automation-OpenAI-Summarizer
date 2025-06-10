import unittest
import asyncio
from unittest.mock import MagicMock, patch
from email_handler import EmailHandler
import email
from io import BytesIO

class TestEmailHandler(unittest.TestCase):
    def setUp(self):
        self.handler = EmailHandler()

    def create_mock_email(self, content, from_email):
        """Create a mock email message"""
        msg = email.message.EmailMessage()
        msg.set_content(content)
        msg["From"] = from_email
        msg["Subject"] = "Test Subject"
        return msg

    @patch('imaplib.IMAP4_SSL')
    @patch('aiohttp.ClientSession.post')
    async def test_check_emails(self, mock_post, mock_imap):
        # Mock IMAP server response
        mock_imap.return_value.search.return_value = (None, [b'1'])
        mock_imap.return_value.fetch.return_value = (None, [(b'', self.create_mock_email(
            "Test Newsletter Content",
            "test@example.com"
        ).as_bytes())])

        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value.__aenter__.return_value = mock_response

        # Run the check_emails method
        result = await self.handler.check_emails()
        self.assertTrue(result)

    def test_extract_email_content(self):
        # Test simple email
        content = "Test content"
        msg = self.create_mock_email(content, "test@example.com")
        extracted = self.handler.extract_email_content(msg)
        self.assertEqual(extracted.strip(), content)

        # Test multipart email
        msg = email.message.EmailMessage()
        msg.add_alternative("HTML content", subtype='html')
        msg.add_alternative("Plain text content", subtype='plain')
        extracted = self.handler.extract_email_content(msg)
        self.assertEqual(extracted.strip(), "Plain text content")

def run_async_test(coro):
    return asyncio.run(coro)

if __name__ == '__main__':
    unittest.main()