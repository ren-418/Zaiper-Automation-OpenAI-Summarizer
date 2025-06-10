import imaplib
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gmail_connection():
    try:
        # Get credentials from environment variables
        email = os.getenv("EMAIL_ADDRESS")
        password = os.getenv("EMAIL_PASSWORD")

        print(f"Attempting to connect to Gmail with account: {email}")

        # Create an IMAP4 class with SSL
        imap = imaplib.IMAP4_SSL("imap.gmail.com")

        # Authenticate
        imap.login(email, password)

        print("Successfully connected to Gmail!")

        # List all mailboxes
        print("\nAvailable mailboxes:")
        status, mailboxes = imap.list()
        for mailbox in mailboxes:
            print(mailbox.decode())

        # Select INBOX
        imap.select("INBOX")

        # Search for all emails
        status, messages = imap.search(None, "ALL")

        # Get the number of messages
        message_count = len(messages[0].split())
        print(f"\nTotal messages in INBOX: {message_count}")

        # Clean up
        imap.logout()
        return True

    except Exception as e:
        print(f"Error connecting to Gmail: {str(e)}")
        return False

if __name__ == "__main__":
    test_gmail_connection()