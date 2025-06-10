import imaplib
import os
from dotenv import load_dotenv
import socket
import ssl

# Load environment variables
load_dotenv()

def test_email_connection():
    try:
        # Get credentials from environment variables
        email = os.getenv("EMAIL_ADDRESS")
        password = os.getenv("EMAIL_PASSWORD")

        print(f"Attempting to connect to Outlook with account: {email}")

        # Create an IMAP4 class with SSL and longer timeout
        imap = imaplib.IMAP4_SSL("outlook.office365.com", timeout=30)

        try:
            # Authenticate
            imap.login(email, password)
            print("Successfully connected to Outlook!")

            # Test basic operations
            print("\nTesting mailbox operations:")

            # List all mailboxes
            print("\nAvailable mailboxes:")
            status, mailboxes = imap.list()
            if status == 'OK':
                for mailbox in mailboxes:
                    print(mailbox.decode())

            # Select INBOX
            print("\nAccessing INBOX...")
            status, messages = imap.select('INBOX')
            if status == 'OK':
                # Get message count
                message_count = int(messages[0])
                print(f"Total messages in INBOX: {message_count}")

                # Try to fetch the latest message (if any exist)
                if message_count > 0:
                    print("\nFetching latest message header...")
                    status, messages = imap.fetch(str(message_count), '(BODY[HEADER.FIELDS (FROM SUBJECT DATE)])')
                    if status == 'OK':
                        print("Successfully fetched message header")

            print("\nAll operations completed successfully!")
            return True

        except imaplib.IMAP4.error as e:
            if "LOGIN failed" in str(e):
                print("\nAuthentication failed. Please check your credentials.")
                print("Note: If you're using your regular password, you might need to:")
                print("1. Enable 'Allow less secure app access' in your Microsoft Account")
                print("2. Or use your regular Outlook password")
            else:
                print(f"\nIMAP error: {str(e)}")
            return False

        finally:
            try:
                imap.logout()
            except:
                pass

    except socket.gaierror:
        print("Failed to connect to Outlook server. Please check your internet connection.")
        return False
    except socket.timeout:
        print("Connection timed out. Please check your internet connection.")
        return False
    except ssl.SSLError as e:
        print(f"SSL Error: {str(e)}")
        print("This might be due to network restrictions or security software.")
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    test_email_connection()