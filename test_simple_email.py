import imaplib
import os
from dotenv import load_dotenv

def test_outlook_connection():
    # Load environment variables
    load_dotenv()

    # Get credentials
    email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")

    try:
        print(f"\nTesting connection to Outlook with email: {email}")

        # Connect to Outlook's IMAP server
        imap_server = "outlook.office365.com"
        imap = imaplib.IMAP4_SSL(imap_server)

        # Try to login
        imap.login(email, password)
        print("✓ Successfully connected to Outlook!")

        # List available mailboxes
        print("\nAvailable mailboxes:")
        status, mailboxes = imap.list()
        for mailbox in mailboxes:
            print(f"  - {mailbox.decode()}")

        # Select inbox
        imap.select("INBOX")
        print("\n✓ Successfully accessed INBOX")

        # Clean up
        imap.logout()
        print("\n✓ Test completed successfully!")
        return True

    except imaplib.IMAP4.error as e:
        print(f"\n✗ IMAP Error: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Check if your email and password are correct")
        print("2. Make sure IMAP is enabled in your Outlook settings")
        print("3. Try using your regular Outlook password")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    test_outlook_connection()