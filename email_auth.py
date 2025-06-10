import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv

class EmailAuth:
    def __init__(self):
        """Initialize email authentication"""
        load_dotenv()
        # Only request read-only access to emails
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        self.creds = None
        self.service = None

    def authenticate(self):
        """Authenticate with Gmail using OAuth2"""
        try:
            # Check if we have stored credentials
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    self.creds = pickle.load(token)

            # If credentials are not valid or don't exist, get new ones
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    # Create the flow using the client secrets file
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', self.SCOPES)

                    # Run the OAuth2 flow
                    self.creds = flow.run_local_server(port=0)

                # Save credentials for future use
                with open('token.pickle', 'wb') as token:
                    pickle.dump(self.creds, token)

            # Build the Gmail service
            self.service = build('gmail', 'v1', credentials=self.creds)
            return self.service

        except Exception as e:
            print(f"Authentication error: {str(e)}")
            print("Please make sure you have credentials.json file in your project directory.")
            raise

    def get_emails(self, max_results=10):
        """Get recent emails"""
        if not self.service:
            self.authenticate()

        try:
            # Get list of messages
            results = self.service.users().messages().list(
                userId='me', maxResults=max_results).execute()
            messages = results.get('messages', [])

            emails = []
            for message in messages:
                # Get full message details
                msg = self.service.users().messages().get(
                    userId='me', id=message['id']).execute()

                # Extract headers
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), '')

                # Get message body
                if 'parts' in msg['payload']:
                    body = msg['payload']['parts'][0]['body'].get('data', '')
                else:
                    body = msg['payload']['body'].get('data', '')

                emails.append({
                    'id': message['id'],
                    'subject': subject,
                    'sender': sender,
                    'body': body,
                    'attachments': self._get_attachments(msg)
                })

            return emails

        except Exception as e:
            print(f"Error fetching emails: {str(e)}")
            raise

    def _get_attachments(self, message):
        """Extract attachment information from message"""
        attachments = []
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part.get('filename'):
                    attachments.append({
                        'filename': part['filename'],
                        'mimeType': part['mimeType'],
                        'attachmentId': part['body'].get('attachmentId')
                    })
        return attachments
