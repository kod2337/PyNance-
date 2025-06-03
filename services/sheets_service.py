"""
Google Sheets service for Finance Tracker
"""

import os
import time
import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any, Optional
from colorama import Fore

from config.settings import (
    GOOGLE_SHEETS_SCOPES, 
    TRANSACTIONS_WORKSHEET_NAME,
    CHARTS_WORKSHEET_NAME, 
    TRANSACTION_HEADERS,
    CHARTS_WORKSHEET_ROWS,
    CHARTS_WORKSHEET_COLS,
    DEFAULT_CREDENTIALS_FILE,
    DEFAULT_SPREADSHEET_NAME,
    DEFAULT_USER_EMAIL,
    MAX_API_RETRIES,
    API_RETRY_DELAY
)


class SheetsService:
    """Handles all Google Sheets operations"""
    
    def __init__(self, credentials_file: str = None, spreadsheet_name: str = None, user_email: str = None):
        self.credentials_file = credentials_file or DEFAULT_CREDENTIALS_FILE
        self.spreadsheet_name = spreadsheet_name or DEFAULT_SPREADSHEET_NAME
        self.user_email = user_email or DEFAULT_USER_EMAIL
        self.client = None
        self.spreadsheet = None
        self.transactions_worksheet = None
        
    def _retry_api_call(self, operation, *args, **kwargs):
        """Retry API calls with exponential backoff"""
        last_exception = None
        
        for attempt in range(MAX_API_RETRIES):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < MAX_API_RETRIES - 1:
                    wait_time = API_RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                    print(f"{Fore.YELLOW}⚠️  API call failed (attempt {attempt + 1}/{MAX_API_RETRIES}), retrying in {wait_time:.1f}s...")
                    time.sleep(wait_time)
                else:
                    print(f"{Fore.RED}❌ API call failed after {MAX_API_RETRIES} attempts")
        
        # If all retries failed, raise the last exception
        raise last_exception
    
    def connect(self) -> bool:
        """Connect to Google Sheets API"""
        try:
            if not os.path.exists(self.credentials_file):
                print(f"{Fore.RED}❌ Credentials file '{self.credentials_file}' not found!")
                return False
                
            # Load credentials
            creds = Credentials.from_service_account_file(self.credentials_file, scopes=GOOGLE_SHEETS_SCOPES)
            self.client = gspread.authorize(creds)
            
            # Open or create spreadsheet
            self._setup_spreadsheet()
            
            # Setup transactions worksheet
            self._setup_transactions_worksheet()
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error connecting to Google Sheets: {str(e)}")
            return False
    
    def _setup_spreadsheet(self):
        """Open existing or create new spreadsheet"""
        try:
            self.spreadsheet = self.client.open(self.spreadsheet_name)
            print(f"{Fore.GREEN}✅ Connected to existing spreadsheet: {self.spreadsheet_name}")
        except gspread.SpreadsheetNotFound:
            self.spreadsheet = self.client.create(self.spreadsheet_name)
            print(f"{Fore.GREEN}✅ Created new spreadsheet: {self.spreadsheet_name}")
            self._share_spreadsheet()
    
    def _share_spreadsheet(self):
        """Share spreadsheet with user email"""
        try:
            self.spreadsheet.share(self.user_email, perm_type='user', role='writer')
            print(f"{Fore.GREEN}✅ Shared spreadsheet with {self.user_email}")
            print(f"{Fore.CYAN}📧 Check your Google Drive - the spreadsheet should now be visible!")
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  Created spreadsheet but couldn't share: {str(e)}")
            print(f"{Fore.CYAN}💡 You can manually share it later if needed")
    
    def _setup_transactions_worksheet(self):
        """Setup transactions worksheet"""
        try:
            self.transactions_worksheet = self.spreadsheet.worksheet(TRANSACTIONS_WORKSHEET_NAME)
        except gspread.WorksheetNotFound:
            self.transactions_worksheet = self.spreadsheet.add_worksheet(
                title=TRANSACTIONS_WORKSHEET_NAME, 
                rows=1000, 
                cols=6
            )
            self.transactions_worksheet.append_row(TRANSACTION_HEADERS)
            print(f"{Fore.GREEN}✅ Created {TRANSACTIONS_WORKSHEET_NAME} worksheet with headers")
    
    def add_transaction_row(self, transaction_row: List[Any]) -> bool:
        """Add a transaction row to the spreadsheet"""
        try:
            if self.transactions_worksheet:
                self._retry_api_call(self.transactions_worksheet.append_row, transaction_row)
                return True
            return False
        except Exception as e:
            print(f"{Fore.RED}❌ Error adding transaction: {str(e)}")
            return False
    
    def get_all_records(self) -> List[Dict[str, Any]]:
        """Get all transactions from spreadsheet"""
        try:
            if self.transactions_worksheet:
                return self._retry_api_call(self.transactions_worksheet.get_all_records)
            return []
        except Exception as e:
            print(f"{Fore.RED}❌ Error fetching transactions: {str(e)}")
            return []
    
    def get_all_transactions(self) -> List[Dict[str, Any]]:
        """Get all transactions from spreadsheet (alias for backward compatibility)"""
        return self.get_all_records()
    
    def get_current_balance(self) -> float:
        """Get current balance from last transaction"""
        try:
            if not self.transactions_worksheet:
                print(f"{Fore.YELLOW}⚠️  No transactions worksheet available")
                return 0.0
                
            # Get all balance values from column F (Balance column) with retry
            balance_column = self._retry_api_call(self.transactions_worksheet.col_values, 6)  # Column F (Balance)
            
            if len(balance_column) <= 1:  # Only header or no data
                print(f"{Fore.YELLOW}⚠️  No transactions found")
                return 0.0
            
            # Get the last balance entry
            last_balance_str = balance_column[-1]
            
            # Handle empty or invalid balance entries
            if not last_balance_str or last_balance_str.strip() == '':
                print(f"{Fore.YELLOW}⚠️  Last balance entry is empty")
                return 0.0
            
            # Try to convert to float
            try:
                balance = float(last_balance_str)
                return balance
            except ValueError:
                print(f"{Fore.RED}❌ Invalid balance format: '{last_balance_str}' - trying to recalculate")
                # Fallback: calculate balance from transactions
                return self._calculate_balance_from_transactions()
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error getting current balance: {str(e)}")
            # Fallback: try to calculate from transaction records
            try:
                return self._calculate_balance_from_transactions()
            except:
                return 0.0
    
    def _calculate_balance_from_transactions(self) -> float:
        """Calculate balance by summing all transaction amounts (fallback method)"""
        try:
            records = self.get_all_records()
            if not records:
                return 0.0
            
            balance = 0.0
            for record in records:
                amount = float(record.get('Amount', 0))
                balance += amount
            
            print(f"{Fore.CYAN}✅ Balance recalculated from transactions: {balance}")
            return balance
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error calculating balance from transactions: {str(e)}")
            return 0.0
    
    def get_or_create_charts_worksheet(self):
        """Get or create charts worksheet"""
        try:
            return self.spreadsheet.worksheet(CHARTS_WORKSHEET_NAME)
        except gspread.WorksheetNotFound:
            return self.spreadsheet.add_worksheet(
                title=CHARTS_WORKSHEET_NAME, 
                rows=CHARTS_WORKSHEET_ROWS, 
                cols=CHARTS_WORKSHEET_COLS
            )
    
    def batch_update(self, requests: List[Dict[str, Any]]) -> bool:
        """Perform batch update on spreadsheet"""
        try:
            self.spreadsheet.batch_update({'requests': requests})
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Error in batch update: {str(e)}")
            return False
    
    def is_connected(self) -> bool:
        """Check if service is properly connected"""
        return self.client is not None and self.spreadsheet is not None and self.transactions_worksheet is not None 