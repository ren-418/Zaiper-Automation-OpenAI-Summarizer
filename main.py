from openai import OpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import CharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import requests
from datetime import datetime, timezone
from notion_client import Client
import openai

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

NOTION_KEY = os.getenv("NOTION_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

headers = {
    "Authorization": "Bearer " + NOTION_KEY,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

models = ["gpt-3.5-turbo"]

app = FastAPI(
    title="Email Processor API",
    description="API for processing emails and checking OpenAI status",
    version="1.0.0"
)

function_descriptions = [
    {
        "name": "categorise_email",
        "description": "Based on the contents of the email, the function categorizes the email as either a newsletter or not",
        "parameters": {
            "type": "object",
            "properties": {
                "is_newsletter": {
                    "type": "boolean",
                    "description": "Accepts a true value if the contents of the email is a newsletter"
                }
            },
            "required": ["is_newsletter"]
        }
    },
    {
        "name": "summary_title",
        "description": "Based on the summary given in the query, the function creates a title for the summary",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Generated title for the summary containing less than 100 characters"
                }
            },
            "required": ["title"]
        }
    }
]

# Test mode flag
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

def doc_creator(content):
    """
    Create documents from text content.

    Args:
        content (str): The input text content.

    Returns:
        list: The list of created documents.
    """
    # Initialize the text splitter
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=150)

    # Split the content into chunks
    split_content = text_splitter.split_text(content)

    # Split the first chunk by newline character
    split_content = split_content[0].split("\n")

    # Create documents from the split content
    docs = text_splitter.create_documents(split_content)

    return docs


def generate_summary(content):
    """
    Generate a summary of the given content.

    Args:
        content (str): The content to generate a summary from.

    Returns:
        str: The generated summary.
    """
    # Create documents from content
    documents = doc_creator(content)

    # Initialize the ChatOpenAI model
    model = ChatOpenAI(model=models[-1], temperature=0.5)

    # Load and initialize the summarization chain
    chain = load_summarize_chain(model, chain_type="map_reduce")

    # Generate the summary using the chain
    summary = chain.run(documents)

    return summary


def generate_short_summary(content):
    """
    Generate a short summary of the given content.

    Args:
        content (str): The content to summarize.

    Returns:
        str: The generated short summary.
    """

    # Define the prompt template
    prompt_template = """Write a concise summary in less than 500 characters of the text given below. If it is a
    newsletter, refer to it as a newsletter. If it isn't a newsletter, simply make summary say "This isn't a newsletter".
    If it is a newsletter, the summary should be less than 500 characters long and refer to the original text as a
    newsletter, otherwise simply output the summary as "This isn't a newsletter".

    TEXT:
    {text}

    SUMMARY OF NEWSLETTER IN LESS THAN 500 CHARACTERS:"""

    # Generate the summary using the load_summarize_chain function
    summary = load_summarize_chain(
        ChatOpenAI(model=models[-1], temperature=0.5),
        chain_type="stuff",
        prompt=PromptTemplate(template=prompt_template, input_variables=["text"])
    ).run(doc_creator(content)[:3])

    return summary


def summarise_newsletter(content):
    # Generate a short summary of the newsletter content
    short_summary = generate_short_summary(content)
    print(short_summary)

    # Prompt the user to generate a title for the summary content
    query_title = f"Please generate a title in less than 100 characters for the following newsletter summary content: {short_summary}"
    messages_title = [{"role": "user", "content": query_title}]

    # Generate the title using an AI model
    title_response = client.chat.completions.create(
        model=models[-1],
        messages=messages_title,
        functions=function_descriptions,
        function_call={"name": "summary_title"}
    )

    # Extract the generated title from the AI response
    title_json = json.loads(title_response.choices[0].message.function_call.arguments)
    title = title_json["title"]

    # Generate the final summary of the newsletter content
    final_summary = generate_summary(content)

    # Create a summary object with the title and final summary
    summary_object = {
        "title": title,
        "summary": final_summary
    }

    return summary_object


def create_notion_page(data: dict) -> requests.Response:
    """
    Creates a new page in Notion using the provided data.

    Args:
        data (dict): The data to be sent in the request body.

    Returns:
        requests.Response: The response object containing the server's response to the request.
    """
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {NOTION_KEY}",
        "Notion-Version": "2022-06-28"
    }
    response = requests.post(url, headers=headers, json=data)
    return response


def send_to_notion(summary_obj: dict):
    """
    Sends the given summary object to Notion.

    Args:
        summary_obj (dict): The summary object to send.

    """
    # Check if the summary object is not empty
    if summary_obj:
        # Extract the required values from the summary object
        title = summary_obj["title"]
        summary = summary_obj["summary"]
        published_date = datetime.now().astimezone(timezone.utc).isoformat()

        # Create the data payload to send to Notion
        data = {
            "parent": {"database_id": NOTION_DATABASE_ID},
            "properties": {
                "Name": {"title": [{"text": {"content": title}}]},
                "Published": {"date": {"start": published_date, "end": None}}
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": summary
                                }
                            }
                        ]
                    }
                }
            ]
        }

        # Call the create_notion_page function with the data payload
        create_notion_page(data)


class EmailContent(BaseModel):
    subject: str
    body: str
    sender: str


def handle_openai_error(e):
    """Handle OpenAI API errors with user-friendly messages."""
    error_message = str(e)
    if "insufficient_quota" in error_message:
        return "OpenAI API quota exceeded. Please check your API key and billing status at https://platform.openai.com/account/billing"
    elif "invalid_api_key" in error_message:
        return "Invalid OpenAI API key. Please check your API key in the .env file"
    else:
        return f"OpenAI API error: {error_message}"


def is_newsletter(subject: str, body: str) -> bool:
    """Determine if the email is a newsletter."""
    if TEST_MODE:
        # In test mode, consider it a newsletter if the subject contains "newsletter" or "digest"
        return "newsletter" in subject.lower() or "digest" in subject.lower()

    try:
        prompt = f"""
        Analyze if this email is a newsletter:
        Subject: {subject}
        Content: {body[:500]}...

        Respond with only 'true' or 'false'.
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=10
        )

        return response.choices[0].message.content.strip().lower() == 'true'
    except Exception as e:
        raise HTTPException(status_code=500, detail=handle_openai_error(e))


def summarize_content(subject: str, body: str) -> str:
    """Summarize the newsletter content."""
    if TEST_MODE:
        # In test mode, return a simple summary
        return f"Test Summary of {subject}:\n\nKey points from the content:\n{body[:200]}..."

    try:
        prompt = f"""
        Summarize this newsletter in a concise way:
        Subject: {subject}
        Content: {body}

        Include:
        1. Main topics
        2. Key points
        3. Any important links or resources
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=handle_openai_error(e))


def add_to_notion(summary: str, subject: str, sender: str):
    """Add the summary to Notion database."""
    if TEST_MODE:
        # In test mode, just print the summary
        print(f"Test Mode - Would add to Notion:\nSubject: {subject}\nSender: {sender}\nSummary: {summary}")
        return

    try:
        database_id = os.getenv("NOTION_DATABASE_ID")
        if not database_id:
            raise HTTPException(status_code=500, detail="Notion database ID not found in environment variables")

        new_page = {
            "parent": {"database_id": database_id},
            "properties": {
                "Title": {"title": [{"text": {"content": subject}}]},
                "Source": {"rich_text": [{"text": {"content": sender}}]},
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": summary}}]
                    }
                }
            ]
        }

        notion = Client(auth=NOTION_KEY)
        notion.pages.create(**new_page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Notion API error: {str(e)}")


def check_openai_connection():
    """Check if OpenAI API is accessible and working."""
    try:
        # Try a simple API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        return {
            "status": "connected",
            "model": "gpt-3.5-turbo",
            "message": "OpenAI API is working correctly"
        }
    except Exception as e:
        error_message = str(e)
        if "insufficient_quota" in error_message:
            return {
                "status": "error",
                "message": "OpenAI API quota exceeded. Please check your billing status at https://platform.openai.com/account/billing"
            }
        elif "invalid_api_key" in error_message:
            return {
                "status": "error",
                "message": "Invalid OpenAI API key. Please check your API key in the .env file"
            }
        else:
            return {
                "status": "error",
                "message": f"OpenAI API error: {error_message}"
            }


def process_email_content(subject: str, body: str) -> str:
    """Process email content and return a summary."""
    if TEST_MODE:
        return f"Test Summary of {subject}:\n\nKey points from the content:\n{body[:200]}..."

    try:
        prompt = f"""
        Summarize this email content in a concise way:
        Subject: {subject}
        Content: {body}

        Include:
        1. Main topics
        2. Key points
        3. Any important links or resources
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content
    except Exception as e:
        error_message = str(e)
        if "insufficient_quota" in error_message:
            raise HTTPException(
                status_code=402,
                detail="OpenAI API quota exceeded. Please check your billing status at https://platform.openai.com/account/billing"
            )
        elif "invalid_api_key" in error_message:
            raise HTTPException(
                status_code=401,
                detail="Invalid OpenAI API key. Please check your API key in the .env file"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"OpenAI API error: {error_message}"
            )


@app.get("/")
async def root():
    """Root endpoint that returns API information."""
    return {
        "name": "Email Processor API",
        "version": "1.0.0",
        "endpoints": {
            "check_openai": "/api/check-openai",
            "process_email": "/api/process-email",
            "health": "/api/health"
        }
    }


@app.get("/api/check-openai")
async def check_openai():
    """Check OpenAI API connection status."""
    return check_openai_connection()


@app.post("/api/process-email")
async def process_email(email: EmailContent):
    """Process incoming email and return a summary."""
    try:
        # Process the email content
        summary = process_email_content(email.subject, email.body)

        return {
            "status": "success",
            "message": "Email processed successfully",
            "summary": summary,
            "metadata": {
                "subject": email.subject,
                "sender": email.sender,
                "processed_at": datetime.now().isoformat()
            }
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing email: {str(e)}"
        )


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    openai_status = check_openai_connection()
    return {
        "status": "healthy",
        "test_mode": TEST_MODE,
        "openai_status": openai_status["status"],
        "openai_message": openai_status["message"]
    }
