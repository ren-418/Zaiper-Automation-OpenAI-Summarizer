from datetime import datetime
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

NOTION_KEY = os.getenv("NOTION_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

def mock_process_email(content, from_email):
    """Mock email processing without OpenAI API"""

    # Simple rule-based newsletter detection
    newsletter_keywords = ['newsletter', 'weekly', 'highlights', 'updates']
    is_newsletter = any(keyword in content.lower() for keyword in newsletter_keywords)

    if is_newsletter:
        # Create a Notion task for the newsletter
        url = "https://api.notion.com/v1/pages"

        headers = {
            "Authorization": f"Bearer {NOTION_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

        # Extract first line as title
        title = content.strip().split('\n')[0]
        if len(title) > 100:
            title = title[:97] + "..."

        data = {
            "parent": {"database_id": NOTION_DATABASE_ID},
            "properties": {
                "Task name": {
                    "title": [
                        {
                            "text": {
                                "content": f"Newsletter Summary: {title}"
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
                            "name": "Newsletter"
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
                                "content": content[:2000] if len(content) > 2000 else content
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

        response = requests.post(url, headers=headers, json=data)
        return response.json()

    return {"message": "Not a newsletter, skipping Notion update"}

# Test newsletter content
newsletter_content = """
Weekly Tech Newsletter

Hello everyone!

This week's highlights:
1. New AI Features Released
2. Cloud Computing Updates
3. Developer Tools Overview

Stay tuned for more updates next week!

Best regards,
Tech Team
"""

# Test regular email content
regular_email_content = """
Hi team,

Please review the latest pull request for the authentication module.
We need to merge this by end of day.

Thanks,
Dev Team
"""

print("Testing with newsletter content...")
result = mock_process_email(newsletter_content, "newsletter@tech.com")
print(json.dumps(result, indent=2))

print("\nTesting with regular email content...")
result = mock_process_email(regular_email_content, "dev@team.com")
print(json.dumps(result, indent=2))