# Newsletter Summarizer

This project is a FastAPI application that automatically processes incoming emails, identifies newsletters, and summarizes them using OpenAI's GPT-3.5. The summaries are then stored in a Notion database.

## Features

- Automatic newsletter detection
- AI-powered content summarization
- Notion integration for storage
- Zapier integration for email triggers
- Health check endpoint for monitoring

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix/MacOS:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys:
```env
OPENAI_API_KEY=your_openai_api_key
NOTION_KEY=your_notion_key
NOTION_DATABASE_ID=your_notion_database_id
```

5. Run the application:
```bash
uvicorn main:app --reload
```

## API Endpoints

- `POST /process-email`: Process incoming emails
  - Input: Email content (subject, body, sender)
  - Output: Processing status and summary (if applicable)

- `GET /health`: Health check endpoint
  - Output: Application status

## Zapier Integration

1. Create a new Zap in Zapier
2. Set up an email trigger for new incoming emails
3. Add a webhook action that POSTs to your `/process-email` endpoint
4. Configure the webhook with the email content

## Notion Setup

1. Create a new database in Notion
2. Get your Notion API key from https://www.notion.so/my-integrations
3. Share your database with the integration
4. Copy the database ID from the URL

## Development

- The application uses FastAPI for the web framework
- OpenAI's GPT-3.5 for content analysis and summarization
- Notion's API for data storage
- Python 3.8+ is required

## Testing

Run the test suite:
```bash
pytest
```

# Python Flask Application

This is a basic Python Flask web application.

## Setup Instructions

1. Create a virtual environment (recommended):
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Make sure your virtual environment is activated
2. Run the application:
```bash
python app.py
```
3. Open your browser and navigate to `http://localhost:5000`

## Project Structure

- `app.py`: Main application file
- `requirements.txt`: Project dependencies
- `templates/`: HTML templates
  - `index.html`: Main page template