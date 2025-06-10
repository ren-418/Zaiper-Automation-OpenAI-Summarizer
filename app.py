from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from email_processor import EmailProcessor

# Load environment variables
load_dotenv()

app = Flask(__name__)
email_processor = EmailProcessor()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/process_email', methods=['POST'])
def process_email():
    """Process an email and return analysis results"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        result = email_processor.process_email(data)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook requests"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Verify webhook type
        if data.get('type') != 'email':
            return jsonify({"error": "Invalid webhook type"}), 400

        # Process the email data
        result = email_processor.process_email(data.get('data', {}))
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/recent_emails', methods=['GET'])
def recent_emails():
    """Get and process recent emails"""
    try:
        max_results = request.args.get('max_results', default=10, type=int)
        emails = email_processor.get_recent_emails(max_results)
        return jsonify(emails)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)