"""
Configuration settings for Finance Tracker
"""

import os
from pathlib import Path

# Secure credential handling - use environment variables or secure defaults
DEFAULT_CREDENTIALS_FILE = os.getenv('FINANCE_TRACKER_CREDENTIALS', 'credentials.json')
DEFAULT_SPREADSHEET_NAME = os.getenv('FINANCE_TRACKER_SPREADSHEET', 'Finance Tracker Automated')
DEFAULT_USER_EMAIL = os.getenv('FINANCE_TRACKER_EMAIL', 'kodibompat2@gmail.com')

# Validate credentials file exists and warn if using defaults
def validate_credentials():
    """Validate credentials setup"""
    warnings = []
    
    if not os.path.exists(DEFAULT_CREDENTIALS_FILE):
        warnings.append(f"Credentials file '{DEFAULT_CREDENTIALS_FILE}' not found!")
    
    # Check if using potentially insecure defaults
    if DEFAULT_USER_EMAIL == 'kodibompat2@gmail.com' and not os.getenv('FINANCE_TRACKER_EMAIL'):
        warnings.append("Using default email - consider setting FINANCE_TRACKER_EMAIL environment variable")
    
    return warnings

# Security settings
MAX_TRANSACTION_AMOUNT = float(os.getenv('MAX_TRANSACTION_AMOUNT', '1000000'))
MAX_DESCRIPTION_LENGTH = int(os.getenv('MAX_DESCRIPTION_LENGTH', '200'))
MAX_CATEGORY_LENGTH = int(os.getenv('MAX_CATEGORY_LENGTH', '50'))

# API Rate limiting
MAX_API_RETRIES = int(os.getenv('MAX_API_RETRIES', '3'))
API_RETRY_DELAY = float(os.getenv('API_RETRY_DELAY', '1.0'))

# Currency settings
DEFAULT_CURRENCY = 'USD'  # USD or PHP
SUPPORTED_CURRENCIES = {
    'USD': {'symbol': '$', 'name': 'US Dollar'},
    'PHP': {'symbol': '₱', 'name': 'Philippine Peso'}
}

# Google Sheets API settings
GOOGLE_SHEETS_SCOPES = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

# Worksheet settings
TRANSACTIONS_WORKSHEET_NAME = 'Transactions'
CHARTS_WORKSHEET_NAME = 'Charts & Analysis'
TRANSACTION_HEADERS = ["Date", "Description", "Category", "Amount", "Type", "Balance"]

# Chart settings
MAX_BALANCE_TREND_ENTRIES = 30
CHARTS_WORKSHEET_ROWS = 50
CHARTS_WORKSHEET_COLS = 10

# UI settings
MENU_OPTIONS = {
    '1': 'Add Expense',
    '2': 'Add Income', 
    '3': 'View Recent Transactions',
    '4': 'Category Summary',
    '5': 'Check Balance',
    '6': 'Create/Update Charts',
    '8': 'Settings',
    '7': 'Exit'
} 