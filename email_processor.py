import os
from openai import OpenAI
from dotenv import load_dotenv
from email_auth import EmailAuth

class EmailProcessor:
    def __init__(self):
        """Initialize the email processor"""
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.test_mode = os.getenv('TEST_MODE', 'False').lower() == 'true'
        self.email_auth = EmailAuth()

    def process_email(self, email_data):
        """Process an email and return analysis results"""
        if not email_data:
            raise ValueError("Email data cannot be empty")

        # Extract email components
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')
        sender = email_data.get('sender', '')
        attachments = email_data.get('attachments', [])

        print(f"DEBUG: Test mode is: {self.test_mode}")

        if self.test_mode:
            # Return mock data in test mode
            return {
                'subject': subject,
                'summary': 'This is a test summary',
                'action_items': ['Test action item 1', 'Test action item 2'],
                'priority': 'Medium',
                'sender': sender,
                'has_attachments': len(attachments) > 0
            }

        try:
            # Use OpenAI to analyze the email
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an email analysis assistant. Analyze the email and provide a summary, action items, and priority level."},
                    {"role": "user", "content": f"Subject: {subject}\n\nBody: {body}\n\nSender: {sender}\n\nAttachments: {', '.join([att['filename'] for att in attachments]) if attachments else 'None'}"}
                ],
                max_tokens=200
            )

            # Parse the response
            analysis = response.choices[0].message.content

            # Return structured results
            return {
                'subject': subject,
                'summary': analysis,
                'action_items': self._extract_action_items(analysis),
                'priority': self._determine_priority(analysis),
                'sender': sender,
                'has_attachments': len(attachments) > 0,
                'attachments': [att['filename'] for att in attachments]
            }

        except Exception as e:
            print(f"Error processing email: {str(e)}")
            # Check if the error is due to insufficient quota
            if "insufficient_quota" in str(e):
                print("OpenAI quota exceeded. Falling back to basic processing.")
                # Return basic email info without OpenAI analysis
                return {
                    'subject': subject,
                    'summary': 'Analysis skipped due to OpenAI quota limits.',
                    'action_items': [],
                    'priority': 'Unknown',
                    'sender': sender,
                    'has_attachments': len(attachments) > 0,
                    'attachments': [att['filename'] for att in attachments] if attachments else []
                }
            else:
                # Re-raise other exceptions
                raise

    def get_recent_emails(self, max_results=10):
        """Get and process recent emails"""
        try:
            # Get emails using Gmail API
            emails = self.email_auth.get_emails(max_results)

            # Process each email
            processed_emails = []
            for email in emails:
                try:
                    processed = self.process_email(email)
                    processed_emails.append(processed)
                except Exception as e:
                    print(f"Error processing email {email.get('id', 'unknown')}: {str(e)}")
                    continue

            return processed_emails

        except Exception as e:
            print(f"Error getting recent emails: {str(e)}")
            raise

    def _extract_action_items(self, analysis):
        """Extract action items from the analysis"""
        # Simple implementation - can be enhanced
        return [item.strip() for item in analysis.split('\n') if 'action' in item.lower() or 'todo' in item.lower()]

    def _determine_priority(self, analysis):
        """Determine email priority based on analysis"""
        # Simple implementation - can be enhanced
        if 'urgent' in analysis.lower() or 'asap' in analysis.lower():
            return 'High'
        elif 'important' in analysis.lower():
            return 'Medium'
        return 'Low'

def main():
    """Main function to demonstrate the email processor"""
    processor = EmailProcessor()

    try:
        print("Fetching and processing recent emails...")
        processed_emails = processor.get_recent_emails(max_results=5)

        print("\nProcessed Emails:")
        print("-" * 50)

        for email in processed_emails:
            print(f"Subject: {email['subject']}")
            print(f"From: {email['sender']}")
            print(f"Priority: {email['priority']}")
            print(f"Summary: {email['summary']}")
            if email['action_items']:
                print("Action Items:")
                for item in email['action_items']:
                    print(f"- {item}")
            if email['has_attachments']:
                print("Attachments:")
                for attachment in email['attachments']:
                    print(f"- {attachment}")
            print("-" * 50)

    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Check your OpenAI API key in .env file")
        print("2. Ensure you have granted Gmail API permissions")
        print("3. Verify your internet connection")
        print("4. Check if you're in test mode (TEST_MODE=true in .env)")

if __name__ == "__main__":
    main()