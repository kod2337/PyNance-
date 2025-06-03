"""
Configuration settings for Finance Tracker
"""

# Default settings
DEFAULT_CREDENTIALS_FILE = 'credentials.json'
DEFAULT_SPREADSHEET_NAME = 'Finance Tracker Automated'
DEFAULT_USER_EMAIL = 'kodibompat2@gmail.com'

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
    '7': 'Exit'
} 