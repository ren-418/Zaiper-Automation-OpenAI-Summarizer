import os
from openai import OpenAI
from dotenv import load_dotenv

def test_openai_connection():
    """Test OpenAI API connection and basic functionality"""
    print("\n=== Testing OpenAI Connection ===")

    # Load environment variables
    load_dotenv()

    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in .env file")
        return False

    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)

        # Test simple completion
        print("Testing basic completion...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello, this is a test!'"}
            ],
            max_tokens=50
        )

        # Print response
        print("\nResponse received:")
        print(response.choices[0].message.content)

        print("\n✅ OpenAI connection test successful!")
        return True

    except Exception as e:
        print(f"\n❌ Error testing OpenAI connection: {str(e)}")
        return False

def test_email_analysis():
    """Test email analysis functionality"""
    print("\n=== Testing Email Analysis ===")

    # Sample email content
    sample_email = """
    Subject: Meeting Tomorrow

    Hi Team,

    I wanted to remind everyone about our important meeting tomorrow at 2 PM.
    We'll be discussing the Q2 project timeline and resource allocation.

    Please bring your project status reports.

    Best regards,
    John
    """

    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        # Test email analysis
        print("Testing email analysis...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an email analysis assistant."},
                {"role": "user", "content": f"Analyze this email and extract key information:\n\n{sample_email}"}
            ],
            max_tokens=150
        )

        # Print analysis
        print("\nEmail Analysis:")
        print(response.choices[0].message.content)

        print("\n✅ Email analysis test successful!")
        return True

    except Exception as e:
        print(f"\n❌ Error testing email analysis: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting OpenAI API Tests...")

    # Run connection test
    connection_success = test_openai_connection()

    if connection_success:
        # Run email analysis test
        analysis_success = test_email_analysis()

        # Print final results
        print("\n=== Test Results ===")
        print(f"OpenAI Connection: {'✅ Passed' if connection_success else '❌ Failed'}")
        print(f"Email Analysis: {'✅ Passed' if analysis_success else '❌ Failed'}")
    else:
        print("\nSkipping email analysis test due to connection failure")