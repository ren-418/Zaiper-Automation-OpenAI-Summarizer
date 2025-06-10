from email_auth import EmailAuth

def main():
    print("Starting email authentication test...")

    # Initialize the email client
    email_client = EmailAuth()

    try:
        # This will open a browser window for authentication
        print("Please log in to your Google account in the browser window that opens...")
        emails = email_client.get_emails(max_results=5)

        print("\nSuccessfully connected! Here are your 5 most recent emails:")
        print("-" * 50)

        for email in emails:
            print(f"Subject: {email['subject']}")
            print(f"From: {email['sender']}")
            print(f"Body: {email['body'][:100]}...")  # Show first 100 chars of body
            if email['attachments']:
                print("Attachments:")
                for attachment in email['attachments']:
                    print(f"- {attachment['filename']} ({attachment['mimeType']})")
            print("-" * 50)

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure credentials.json is in the same directory as this script")
        print("2. Check that you have an active internet connection")
        print("3. Verify that you granted the necessary permissions in the browser")
        print("4. Ensure you're using a valid Google account")

if __name__ == "__main__":
    main()