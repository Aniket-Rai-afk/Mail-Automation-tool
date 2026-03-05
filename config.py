"""
Configuration file for job mail automation system.
Load environment variables and define system constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).parent.absolute()

# Load environment variables from .env file
load_dotenv()

# Email Configuration
SENDER_EMAILS = os.getenv('SENDER_EMAILS', '').split(',')
SENDER_PASSWORDS = os.getenv('SENDER_PASSWORDS', '').split(',')

# Clean up whitespace
SENDER_EMAILS = [e.strip() for e in SENDER_EMAILS if e.strip()]
SENDER_PASSWORDS = [p.replace(' ', '').strip() for p in SENDER_PASSWORDS if p.strip()]

EMAIL_ACCOUNTS = []
for email, password in zip(SENDER_EMAILS, SENDER_PASSWORDS):
    EMAIL_ACCOUNTS.append({
        'address': email,
        'password': password
    })

# Fallback for old .env format or single account
if not EMAIL_ACCOUNTS:
    email = os.getenv('EMAIL_ADDRESS_1') or os.getenv('EMAIL_ADDRESS')
    password = os.getenv('EMAIL_PASSWORD_1') or os.getenv('EMAIL_PASSWORD')
    if email and password:
        EMAIL_ACCOUNTS.append({
            'address': email,
            'password': password
        })

# SMTP Configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '465'))

# IMAP Configuration
IMAP_SERVER = os.getenv('IMAP_SERVER', 'imap.gmail.com')
IMAP_PORT = int(os.getenv('IMAP_PORT', '993'))

# Rate Limiting Configuration
MAX_EMAILS_PER_DAY = 80
MIN_DELAY_SECONDS = 45
MAX_DELAY_SECONDS = 120
THROTTLE_PAUSE_MINUTES = 30

# Follow-up Configuration
FOLLOWUP_DAYS = 5

# Subject Templates
SUBJECT_TEMPLATES = [
    "Quick question regarding roles at {company}",
    "Exploring opportunities at {company}",
    "Opportunity inquiry at {company}",
    "Question about roles at {company}",
    "Checking openings at {company}"
]

# File Paths
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
TEMPLATES_DIR = BASE_DIR / "templates"
RESUME_DIR = BASE_DIR / "resume"

CONTACTS_CSV = DATA_DIR / "contacts.csv"
APPLICATION_LOG = LOGS_DIR / "application_log.csv"
DAILY_STATS_FILE = LOGS_DIR / "daily_stats.json"
EMAIL_TEMPLATE = TEMPLATES_DIR / "email_template.txt"
FOLLOWUP_TEMPLATE = TEMPLATES_DIR / "followup_template.txt"
RESUME_PATH = RESUME_DIR / "Aniket_Rai_Resume.pdf"

# Bounce Detection Keywords
BOUNCE_KEYWORDS = [
    'Delivery Status Notification',
    'Undelivered Mail Returned to Sender',
    'Mail Delivery Subsystem',
    'Delivery Failure',
    'Mail Delivery Failed',
    'returned to sender',
    'undeliverable'
]

# Status Values
STATUS_PENDING = 'pending'
STATUS_SENT = 'sent'
STATUS_FOLLOWUP_SENT = 'followup_sent'
STATUS_REPLIED = 'replied'
STATUS_BOUNCE = 'bounce'
STATUS_INVALID = 'invalid'
STATUS_NO_RESPONSE = 'no_response'
