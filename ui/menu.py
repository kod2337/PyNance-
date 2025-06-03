"""
User interface module for Finance Tracker
"""

from typing import Dict, Callable
from colorama import Fore
from tabulate import tabulate

from config.settings import MENU_OPTIONS


class FinanceTrackerUI:
    """Handles user interface and menu interactions"""
    
    def __init__(self, finance_tracker):
        self.tracker = finance_tracker
        self.running = True
        
        # Menu action mapping
        self.menu_actions: Dict[str, Callable] = {
            '1': self.add_expense,
            '2': self.add_income,
            '3': self.view_transactions,
            '4': self.category_summary,
            '5': self.check_balance,
            '6': self.create_charts,
            '7': self.exit_app
        }
    
    def display_header(self):
        """Display application header"""
        print(f"{Fore.CYAN}💰 Personal Finance Tracker with Charts")
        print(f"{Fore.CYAN}=" * 45)
    
    def display_menu(self):
        """Display main menu options"""
        print(f"\n{Fore.YELLOW}Choose an option:")
        for key, value in MENU_OPTIONS.items():
            emoji = self._get_menu_emoji(key)
            print(f"{key}. {emoji} {value}")
    
    def _get_menu_emoji(self, option: str) -> str:
        """Get emoji for menu option"""
        emojis = {
            '1': '💸', '2': '💰', '3': '📊', 
            '4': '📈', '5': '💳', '6': '📊', '7': '🚪'
        }
        return emojis.get(option, '•')
    
    def get_user_choice(self) -> str:
        """Get user's menu choice"""
        return input(f"\n{Fore.WHITE}Enter your choice (1-7): ").strip()
    
    def handle_choice(self, choice: str) -> bool:
        """Handle user's menu choice"""
        if choice in self.menu_actions:
            self.menu_actions[choice]()
            return self.running
        else:
            print(f"{Fore.RED}❌ Invalid choice! Please enter 1-7.")
            return True
    
    def add_expense(self):
        """Handle adding an expense"""
        print(f"\n{Fore.RED}💸 Adding Expense")
        description = self._get_input("Description: ")
        category = self._get_input("Category (e.g., Food, Transport, Bills): ")
        amount = self._get_amount()
        
        if amount > 0:
            success = self.tracker.add_transaction(description, category, amount, "Expense")
            if success:
                print(f"{Fore.GREEN}✅ Expense added successfully!")
    
    def add_income(self):
        """Handle adding income"""
        print(f"\n{Fore.GREEN}💰 Adding Income")
        description = self._get_input("Description: ")
        category = self._get_input("Category (e.g., Salary, Freelance, Investment): ")
        amount = self._get_amount()
        
        if amount > 0:
            success = self.tracker.add_transaction(description, category, amount, "Income")
            if success:
                print(f"{Fore.GREEN}✅ Income added successfully!")
    
    def view_transactions(self):
        """Handle viewing recent transactions"""
        try:
            limit_input = input("How many recent transactions to show? (default 10): ").strip()
            limit = int(limit_input) if limit_input else 10
            self.tracker.view_transactions(limit)
        except ValueError:
            print(f"{Fore.YELLOW}⚠️  Using default limit of 10 transactions")
            self.tracker.view_transactions(10)
    
    def category_summary(self):
        """Handle displaying category summary"""
        self.tracker.get_category_summary()
    
    def check_balance(self):
        """Handle checking current balance"""
        balance = self.tracker.get_current_balance()
        balance_color = Fore.GREEN if balance >= 0 else Fore.RED
        print(f"\n{Fore.CYAN}💳 Current Balance: {balance_color}${balance:.2f}")
    
    def create_charts(self):
        """Handle creating charts"""
        success = self.tracker.create_charts()
        if success:
            print(f"{Fore.CYAN}🔗 Open your Google Sheets to view the charts!")
    
    def exit_app(self):
        """Handle application exit"""
        print(f"{Fore.GREEN}👋 Thank you for using Finance Tracker!")
        self.running = False
    
    def _get_input(self, prompt: str) -> str:
        """Get non-empty input from user"""
        while True:
            value = input(prompt).strip()
            if value:
                return value
            print(f"{Fore.RED}❌ This field cannot be empty. Please try again.")
    
    def _get_amount(self) -> float:
        """Get valid amount from user"""
        while True:
            try:
                amount = float(input("Amount: $"))
                if amount <= 0:
                    print(f"{Fore.RED}❌ Amount must be positive!")
                    continue
                return amount
            except ValueError:
                print(f"{Fore.RED}❌ Invalid amount! Please enter a number.")
    
    def display_transactions(self, records: list, limit: int):
        """Display transactions in a formatted table"""
        if not records:
            print(f"{Fore.YELLOW}📝 No transactions found.")
            return
        
        # Get recent records
        recent_records = records[-limit:] if len(records) > limit else records
        recent_records.reverse()  # Show most recent first
        
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
    
    def display_category_summary(self, category_totals: dict):
        """Display category summary in a formatted table"""
        if not category_totals:
            print(f"{Fore.YELLOW}📝 No transactions found.")
            return
        
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
    
    def run(self):
        """Main application loop"""
        self.display_header()
        
        # Check if tracker is connected
        if not self.tracker.is_connected():
            print(f"{Fore.RED}❌ Could not connect to Google Sheets. Please check your setup.")
            return
        
        while self.running:
            self.display_menu()
            choice = self.get_user_choice()
            self.handle_choice(choice) 