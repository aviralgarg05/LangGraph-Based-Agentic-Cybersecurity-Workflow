import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define the allowed scanning scope
ALLOWED_DOMAINS = os.getenv("TARGET_DOMAINS", "google.com,yahoo.com").split(",")
ALLOWED_IPS = os.getenv("TARGET_IPS", "192.168.0.0/24,10.0.0.0/24").split(",")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 5))