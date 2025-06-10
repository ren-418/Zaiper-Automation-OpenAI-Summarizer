import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv
from datetime import datetime
import asyncio
import aiohttp
import json

load_dotenv()

class EmailHandler:
    def __init__(self):
        self.email_address = os.getenv("EMAIL_ADDRESS")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")
        self.api_endpoint = "http://localhost:8000"  # Our FastAPI endpoint

    async def process_email_content(self, email_content, from_email):
        """Process email content through our API"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_endpoint}/",
                json={
                    "from_email": from_email,
                    "content": email_content
                }
            ) as response:
                return await response.json()

    def extract_email_content(self, email_message):
        """Extract content from email message"""
        content = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    content += part.get_payload(decode=True).decode()
        else:
            content = email_message.get_payload(decode=True).decode()
        return content

    async def check_emails(self):
        """Check for new emails and process them"""
        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.email_address, self.email_password)
            mail.select("inbox")

            # Search for unread emails
            _, messages = mail.search(None, "UNSEEN")

            for message_number in messages[0].split():
                try:
                    # Fetch email message
                    _, msg = mail.fetch(message_number, "(RFC822)")
                    email_body = msg[0][1]
                    email_message = email.message_from_bytes(email_body)

                    # Get sender
                    from_header = decode_header(email_message["From"])[0]
                    from_email = from_header[0].decode() if isinstance(from_header[0], bytes) else from_header[0]
                    if "<" in from_email:
                        from_email = from_email.split("<")[1].strip(">")

                    # Extract content
                    content = self.extract_email_content(email_message)

                    # Process through our API
                    result = await self.process_email_content(content, from_email)
                    print(f"Processed email from {from_email}: {result}")

                except Exception as e:
                    print(f"Error processing message {message_number}: {str(e)}")
                    continue

            mail.logout()
            return True

        except Exception as e:
            print(f"Error checking emails: {str(e)}")
            return False

async def run_email_checker():
    """Run the email checker periodically"""
    handler = EmailHandler()
    while True:
        await handler.check_emails()
        # Wait for 5 minutes before checking again
        await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(run_email_checker())