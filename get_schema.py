import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

NOTION_KEY = os.getenv("NOTION_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# API endpoint for retrieving database
url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}"

# Headers
headers = {
    "Authorization": f"Bearer {NOTION_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

try:
    # Make the request
    response = requests.get(url, headers=headers)

    # Print results
    print(f"\nStatus Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("\nDatabase Properties:")
        for prop_name, prop_data in data['properties'].items():
            print(f"\n{prop_name}:")
            print(f"  Type: {prop_data['type']}")
            if 'select' in prop_data:
                print("  Options:", [option['name'] for option in prop_data['select']['options']])
    else:
        print(f"Error: {json.dumps(response.json(), indent=2)}")

except Exception as e:
    print(f"Error occurred: {str(e)}")