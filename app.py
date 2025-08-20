import os
import logging
from flask import Flask
from markupsafe import Markup

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "civil-ai-default-secret-key")

# Add custom template filter for newline to br conversion
@app.template_filter('nl2br')
def nl2br_filter(text):
    """Convert newlines to HTML line breaks"""
    if text is None:
        return ''
    return Markup(str(text).replace('\n', '<br>\n'))

# Import routes after app creation to avoid circular imports
from routes import *

# Log startup information
logging.info("CivilAI Assistant application started successfully")
