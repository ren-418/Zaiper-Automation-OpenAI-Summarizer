import os
from dotenv import load_dotenv
import requests
import json
from datetime import datetime

load_dotenv()

NOTION_KEY = os.getenv("NOTION_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Print values for verification (without showing full key)
print(f"Using Notion Key: {NOTION_KEY[:6]}...{NOTION_KEY[-4:] if NOTION_KEY else 'NOT_SET'}")
print(f"Using Database ID: {NOTION_DATABASE_ID}")

# API endpoint
url = "https://api.notion.com/v1/pages"

# Headers
headers = {
    "Authorization": f"Bearer {NOTION_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Data payload matching your exact database structure
data = {
    "parent": {"database_id": NOTION_DATABASE_ID},
    "properties": {
        "Task name": {
            "title": [
                {
                    "text": {
                        "content": "Test Task from API"
                    }
                }
            ]
        },
        "Status": {
            "status": {
                "name": "Not started"
            }
        },
        "Priority": {
            "select": {
                "name": "Medium"
            }
        },
        "Task type": {
            "multi_select": [
                {
                    "name": "Feature request"
                }
            ]
        },
        "Due date": {
            "date": {
                "start": datetime.now().strftime("%Y-%m-%d")
            }
        },
        "Description": {
            "rich_text": [
                {
                    "text": {
                        "content": "This is a test task created via API"
                    }
                }
            ]
        },
        "Effort level": {
            "select": {
                "name": "Small"
            }
        }
    }
}

try:
    # Make the request
    response = requests.post(url, headers=headers, json=data)

    # Print results
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    if response.status_code == 201:
        print("\nSuccess! Task created in Notion database.")
    elif response.status_code == 404:
        print("\nTROUBLESHOOTING TIPS:")
        print("1. Verify your integration is connected to the database:")
        print("   - Open your database in Notion")
        print("   - Click '...' in top right")
        print("   - Click 'Add connections'")
        print("   - Add your integration")
    elif response.status_code == 401:
        print("\nTROUBLESHOOTING TIPS:")
        print("1. Check your NOTION_KEY in .env file")
        print("2. Make sure it starts with 'secret_'")

except Exception as e:
    print(f"Error occurred: {str(e)}")