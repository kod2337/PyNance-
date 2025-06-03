"""
Modular Finance Tracker - Main Application Class
"""

from typing import List, Dict, Any
from colorama import Fore, init

from models.transaction import Transaction
from services.sheets_service import SheetsService
from services.chart_service import ChartService
from config.settings import (
    DEFAULT_CREDENTIALS_FILE,
    DEFAULT_SPREADSHEET_NAME,
    DEFAULT_USER_EMAIL
)

# Initialize colorama
init(autoreset=True)


class FinanceTracker:
    """
    Main Finance Tracker application class
    Orchestrates all services and provides clean API
    """
    
    def __init__(
        self,
        credentials_file: str = DEFAULT_CREDENTIALS_FILE,
        spreadsheet_name: str = DEFAULT_SPREADSHEET_NAME,
        user_email: str = DEFAULT_USER_EMAIL
    ):
        self.credentials_file = credentials_file
        self.spreadsheet_name = spreadsheet_name
        self.user_email = user_email
        
        # Initialize services
        self.sheets_service = SheetsService(credentials_file, spreadsheet_name, user_email)
        self.chart_service = ChartService(self.sheets_service)
        
        # Connect to Google Sheets
        self.connected = self.sheets_service.connect()
    
    def add_transaction(self, description: str, category: str, amount: float, transaction_type: str) -> bool:
        """Add a new transaction"""
        try:
            # Create transaction object
            transaction = Transaction(description, category, amount, transaction_type)
            
            # Calculate balance
            current_balance = self.get_current_balance()
            if transaction_type.lower() == 'expense':
                new_balance = current_balance - abs(amount)
                transaction.amount = -abs(amount)  # Ensure expenses are negative
            else:
                new_balance = current_balance + abs(amount)
                transaction.amount = abs(amount)   # Ensure income is positive
            
            transaction.balance = new_balance
            
            # Save to Google Sheets
            if self.sheets_service.is_connected():
                success = self.sheets_service.add_transaction_row(transaction.to_row())
                if success:
                    print(f"   💰 New Balance: ${new_balance:.2f}")
                    
                    # Automatically update charts after adding transaction
                    print(f"{Fore.CYAN}   📊 Updating charts...")
                    self._update_charts_silently()
                    
                    return True
            else:
                print(f"{Fore.YELLOW}⚠️  Google Sheets not connected.")
                
            return False
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error adding transaction: {str(e)}")
            return False
    
    def get_current_balance(self) -> float:
        """Get current balance from Google Sheets"""
        return self.sheets_service.get_current_balance()
    
    def view_transactions(self, limit: int = 10):
        """View recent transactions"""
        try:
            records = self.sheets_service.get_all_transactions()
            self._display_transactions(records, limit)
        except Exception as e:
            print(f"{Fore.RED}❌ Error viewing transactions: {str(e)}")
    
    def get_category_summary(self):
        """Get and display category summary"""
        try:
            records = self.sheets_service.get_all_transactions()
            category_totals = self._calculate_category_totals(records)
            self._display_category_summary(category_totals)
        except Exception as e:
            print(f"{Fore.RED}❌ Error generating category summary: {str(e)}")
    
    def create_charts(self) -> bool:
        """Create charts in Google Sheets"""
        try:
            records = self.sheets_service.get_all_transactions()
            return self.chart_service.create_all_charts(records)
        except Exception as e:
            print(f"{Fore.RED}❌ Error creating charts: {str(e)}")
            return False
    
    def _update_charts_silently(self) -> bool:
        """Update charts without verbose output"""
        try:
            records = self.sheets_service.get_all_transactions()
            if records:
                # Temporarily suppress chart service output by redirecting
                import sys
                from io import StringIO
                
                old_stdout = sys.stdout
                sys.stdout = StringIO()
                
                success = self.chart_service.create_all_charts(records)
                
                # Restore stdout
                sys.stdout = old_stdout
                
                if success:
                    print(f"{Fore.GREEN}   ✅ Charts updated!")
                
                return success
            return False
        except Exception as e:
            # Restore stdout in case of error
            sys.stdout = old_stdout if 'old_stdout' in locals() else sys.stdout
            return False
    
    def is_connected(self) -> bool:
        """Check if the tracker is connected to Google Sheets"""
        return self.connected and self.sheets_service.is_connected()
    
    def _calculate_category_totals(self, records: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """Calculate category totals for summary"""
        category_totals = {}
        
        for record in records:
            category = record['Category']
            amount = float(record['Amount'])
            
            if category not in category_totals:
                category_totals[category] = {'income': 0, 'expense': 0}
            
            if amount < 0:
                category_totals[category]['expense'] += abs(amount)
            else:
                category_totals[category]['income'] += amount
        
        return category_totals
    
    def _display_transactions(self, records: List[Dict[str, Any]], limit: int):
        """Display transactions in formatted table"""
        if not records:
            print(f"{Fore.YELLOW}📝 No transactions found.")
            return
        
        # Get recent records
        recent_records = records[-limit:] if len(records) > limit else records
        recent_records.reverse()  # Show most recent first
        
        # Import here to avoid circular imports
        from tabulate import tabulate
        
        # Format data for display
        headers = ["Date", "Description", "Category", "Amount", "Type", "Balance"]
        table_data = []
        
        for record in recent_records:
            amount = float(record['Amount'])
            balance = float(record['Balance'])
            
            # Color code amounts
            if amount < 0:
                amount_str = f"{Fore.RED}-${abs(amount):.2f}"
            else:
                amount_str = f"{Fore.GREEN}+${amount:.2f}"
            
            table_data.append([
                record['Date'],
                self._truncate_text(record['Description'], 30),
                record['Category'],
                amount_str,
                record['Type'],
                f"${balance:.2f}"
            ])
        
        print(f"\n{Fore.CYAN}📊 Recent Transactions (Last {len(recent_records)}):")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    def _display_category_summary(self, category_totals: Dict[str, Dict[str, float]]):
        """Display category summary in formatted table"""
        if not category_totals:
            print(f"{Fore.YELLOW}📝 No transactions found.")
            return
        
        # Import here to avoid circular imports
        from tabulate import tabulate
        
        print(f"\n{Fore.CYAN}📈 Category Summary:")
        headers = ["Category", "Income", "Expenses", "Net"]
        table_data = []
        
        for category, totals in category_totals.items():
            income = totals['income']
            expense = totals['expense']
            net = income - expense
            
            net_color = Fore.GREEN if net >= 0 else Fore.RED
            
            table_data.append([
                category,
                f"{Fore.GREEN}${income:.2f}",
                f"{Fore.RED}${expense:.2f}",
                f"{net_color}${net:.2f}"
            ])
        
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to maximum length"""
        return text[:max_length] + "..." if len(text) > max_length else text
    
    def get_stats(self) -> Dict[str, Any]:
        """Get financial statistics"""
        records = self.sheets_service.get_all_transactions()
        
        if not records:
            return {
                'total_transactions': 0,
                'total_income': 0,
                'total_expenses': 0,
                'current_balance': 0,
                'categories_count': 0
            }
        
        total_income = sum(float(r['Amount']) for r in records if float(r['Amount']) > 0)
        total_expenses = sum(abs(float(r['Amount'])) for r in records if float(r['Amount']) < 0)
        categories = set(r['Category'] for r in records)
        
        return {
            'total_transactions': len(records),
            'total_income': total_income,
            'total_expenses': total_expenses,
            'current_balance': self.get_current_balance(),
            'categories_count': len(categories),
            'categories': list(categories)
        } 