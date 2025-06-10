import os
from email_processor import EmailProcessor
from dotenv import load_dotenv

def test_email_processor():
    """Test email processing functionality"""
    print("\n=== Testing Email Processing ===")

    # Load environment variables
    load_dotenv()

    # Initialize email processor
    processor = EmailProcessor()

    # Test cases
    test_cases = [
        {
            "name": "Basic Email",
            "email": {
                "subject": "Test Meeting",
                "body": "Hello team, we have a meeting tomorrow at 2 PM.",
                "sender": "john@example.com"
            }
        },
        {
            "name": "Email with Attachments",
            "email": {
                "subject": "Project Report",
                "body": "Please find attached the project report.",
                "sender": "sarah@example.com",
                "attachments": ["report.pdf", "data.xlsx"]
            }
        },
        {
            "name": "Empty Email",
            "email": {
                "subject": "",
                "body": "",
                "sender": "unknown@example.com"
            }
        }
    ]

    results = []

    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        try:
            # Process email
            result = processor.process_email(test_case['email'])

            # Print results
            print("\nProcessing Results:")
            print(f"Subject: {result.get('subject', 'N/A')}")
            print(f"Summary: {result.get('summary', 'N/A')}")
            print(f"Action Items: {result.get('action_items', [])}")
            print(f"Priority: {result.get('priority', 'N/A')}")

            results.append(True)
            print("✅ Test passed")

        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            results.append(False)

    # Print final results
    print("\n=== Test Results ===")
    for i, test_case in enumerate(test_cases):
        print(f"{test_case['name']}: {'✅ Passed' if results[i] else '❌ Failed'}")

    return all(results)

if __name__ == "__main__":
    print("Starting Email Processing Tests...")
    success = test_email_processor()
    print(f"\nOverall Test Result: {'✅ All tests passed' if success else '❌ Some tests failed'}")