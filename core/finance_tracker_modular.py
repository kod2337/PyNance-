"""
Finance Tracker - Modular Version
Clean, modular personal finance tracker with Google Sheets integration
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from colorama import Fore, Style

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from models.transaction import Transaction
from services.sheets_service import SheetsService
from services.chart_service import ChartService
from services.currency_service import get_currency_service
from services.settings_service import get_settings_service


class FinanceTracker:
    """Main Finance Tracker class with modular architecture"""
    
    def __init__(self):
        self.sheets_service = SheetsService()
        self.chart_service = ChartService(self.sheets_service)  # Pass sheets_service to chart_service
        self.currency_service = get_currency_service()
        self.settings_service = get_settings_service()
        
        # Initialize Google Sheets connection
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize connection to Google Sheets"""
        try:
            success = self.sheets_service.connect()
            if success:
                print(f"{Fore.GREEN}✅ Connected to Google Sheets successfully!")
            else:
                print(f"{Fore.RED}❌ Failed to connect to Google Sheets.")
        except Exception as e:
            print(f"{Fore.RED}❌ Error connecting to Google Sheets: {str(e)}")
    
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
                    formatted_balance = self.currency_service.format_balance(new_balance)
                    print(f"   💰 New Balance: {formatted_balance}")
                    
                    # Automatically update charts after adding transaction
                    if self.settings_service.get_auto_update_charts():
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
            records = self.sheets_service.get_all_records()
            if records:
                # Use settings for max transactions if available
                max_transactions = self.settings_service.get_max_recent_transactions()
                effective_limit = min(limit, max_transactions) if limit else max_transactions
                self._display_transactions(records, effective_limit)
            else:
                print(f"{Fore.YELLOW}📝 No transactions found.")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error viewing transactions: {str(e)}")
    
    def get_category_summary(self):
        """Get spending summary by category"""
        try:
            records = self.sheets_service.get_all_records()
            if records:
                category_totals = self._calculate_category_totals(records)
                self._display_category_summary(category_totals)
            else:
                print(f"{Fore.YELLOW}📝 No transactions found.")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error generating category summary: {str(e)}")
    
    def create_charts(self) -> bool:
        """Create/update charts in Google Sheets"""
        try:
            records = self.sheets_service.get_all_records()
            if not records:
                print(f"{Fore.YELLOW}📊 No data available for charts.")
                return False
            
            print(f"{Fore.CYAN}📊 Creating charts...")
            success = self.chart_service.create_all_charts(records)
            
            if success:
                print(f"{Fore.GREEN}✅ Charts created successfully!")
                print(f"{Fore.CYAN}🔗 Open your Google Sheets to view the charts!")
                return True
            else:
                print(f"{Fore.RED}❌ Failed to create charts.")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error creating charts: {str(e)}")
            return False
    
    def _update_charts_silently(self):
        """Update charts without user feedback"""
        try:
            records = self.sheets_service.get_all_records()
            if records:
                self.chart_service.create_all_charts(records)
        except Exception:
            pass  # Silent update, don't show errors
    
    def is_connected(self) -> bool:
        """Check if connected to Google Sheets"""
        return self.sheets_service.is_connected()
    
    def _calculate_category_totals(self, records: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """Calculate category totals for income and expenses"""
        category_totals = {}
        
        for record in records:
            category = record.get('Category', 'Unknown')
            amount = float(record.get('Amount', 0))
            
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
            
            # Color code amounts using currency service
            amount_str = self.currency_service.format_amount_with_color(
                amount, 
                positive_color=Fore.GREEN, 
                negative_color=Fore.RED, 
                reset_color=Style.RESET_ALL
            )
            
            balance_str = self.currency_service.format_balance(balance)
            
            table_data.append([
                record['Date'],
                self._truncate_text(record['Description'], 30),
                record['Category'],
                amount_str,
                record['Type'],
                balance_str
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
            
            # Format amounts using currency service
            income_str = self.currency_service.format_amount_with_color(
                income, positive_color=Fore.GREEN, reset_color=Style.RESET_ALL
            )
            expense_str = self.currency_service.format_amount_with_color(
                expense, negative_color=Fore.RED, reset_color=Style.RESET_ALL
            )
            net_color = Fore.GREEN if net >= 0 else Fore.RED
            net_str = f"{net_color}{self.currency_service.format_balance(net)}{Style.RESET_ALL}"
            
            table_data.append([
                category,
                income_str,
                expense_str,
                net_str
            ])
        
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to maximum length"""
        return text[:max_length] + "..." if len(text) > max_length else text 