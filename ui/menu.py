"""
User interface module for Finance Tracker
"""

from typing import Dict, Callable
from colorama import Fore, Style
from tabulate import tabulate

from config.settings import MENU_OPTIONS
from services.currency_service import get_currency_service
from services.settings_service import get_settings_service


class FinanceTrackerUI:
    """Handles user interface and menu interactions"""
    
    def __init__(self, finance_tracker):
        self.tracker = finance_tracker
        self.running = True
        self.currency_service = get_currency_service()
        self.settings_service = get_settings_service()
        
        # Menu action mapping
        self.menu_actions: Dict[str, Callable] = {
            '1': self.add_expense,
            '2': self.add_income,
            '3': self.view_transactions,
            '4': self.category_summary,
            '5': self.check_balance,
            '6': self.create_charts,
            '8': self.show_settings,
            '7': self.exit_app
        }
    
    def display_header(self):
        """Display application header"""
        currency_info = self.currency_service.get_currency_info()
        print(f"{Fore.CYAN}💰 Personal Finance Tracker with Charts")
        print(f"{Fore.CYAN}=" * 45)
        print(f"{Fore.YELLOW}💱 Current Currency: {currency_info['name']} ({currency_info['symbol']})")
    
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
            '4': '📈', '5': '💳', '6': '📊', 
            '8': '⚙️', '7': '🚪'
        }
        return emojis.get(option, '•')
    
    def get_user_choice(self) -> str:
        """Get user's menu choice"""
        return input(f"\n{Fore.WHITE}Enter your choice (1-8): ").strip()
    
    def handle_choice(self, choice: str) -> bool:
        """Handle user's menu choice"""
        if choice in self.menu_actions:
            self.menu_actions[choice]()
            return self.running
        else:
            print(f"{Fore.RED}❌ Invalid choice! Please enter 1-8.")
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
        formatted_balance = self.currency_service.format_balance(balance)
        print(f"\n{Fore.CYAN}💳 Current Balance: {balance_color}{formatted_balance}")
    
    def create_charts(self):
        """Handle creating charts"""
        success = self.tracker.create_charts()
        if success:
            print(f"{Fore.CYAN}🔗 Open your Google Sheets to view the charts!")
    
    def show_settings(self):
        """Show settings menu"""
        while True:
            print(f"\n{Fore.CYAN}⚙️  Settings Menu")
            print(f"{Fore.CYAN}=" * 20)
            print("1. 💱 Change Currency")
            print("2. 📊 Display Settings")
            print("3. 🔄 Reset to Defaults")
            print("4. 📋 View All Settings")
            print("5. 🔙 Back to Main Menu")
            
            choice = input(f"\n{Fore.WHITE}Enter your choice (1-5): ").strip()
            
            if choice == '1':
                self._change_currency()
            elif choice == '2':
                self._display_settings()
            elif choice == '3':
                self._reset_settings()
            elif choice == '4':
                self._view_all_settings()
            elif choice == '5':
                break
            else:
                print(f"{Fore.RED}❌ Invalid choice! Please enter 1-5.")
    
    def _change_currency(self):
        """Handle currency change"""
        print(f"\n{Fore.CYAN}💱 Currency Selection")
        currencies = self.settings_service.get_available_currencies()
        
        print(f"\n{Fore.YELLOW}Available currencies:")
        for i, (code, info) in enumerate(currencies.items(), 1):
            current = " (Current)" if code == self.settings_service.get_currency() else ""
            print(f"{i}. {info['symbol']} {info['name']} ({code}){current}")
        
        try:
            choice = input(f"\n{Fore.WHITE}Enter your choice (1-{len(currencies)}): ").strip()
            choice_idx = int(choice) - 1
            
            if 0 <= choice_idx < len(currencies):
                currency_code = list(currencies.keys())[choice_idx]
                self.settings_service.set_currency(currency_code)
                self.currency_service = get_currency_service()  # Refresh service
                
                currency_info = currencies[currency_code]
                print(f"{Fore.GREEN}✅ Currency changed to {currency_info['name']} ({currency_info['symbol']})")
            else:
                print(f"{Fore.RED}❌ Invalid choice!")
                
        except ValueError:
            print(f"{Fore.RED}❌ Please enter a valid number!")
    
    def _display_settings(self):
        """Handle display settings"""
        print(f"\n{Fore.CYAN}📊 Display Settings")
        print("1. Show/Hide Currency Symbol")
        print("2. Change Decimal Places")
        print("3. Max Recent Transactions")
        print("4. Auto-update Charts")
        
        choice = input(f"\n{Fore.WHITE}Enter your choice (1-4): ").strip()
        
        if choice == '1':
            current = self.settings_service.get_show_currency_symbol()
            new_value = not current
            self.settings_service.set_show_currency_symbol(new_value)
            status = "enabled" if new_value else "disabled"
            print(f"{Fore.GREEN}✅ Currency symbol display {status}")
            
        elif choice == '2':
            try:
                decimal_places = int(input("Enter decimal places (0-4): "))
                self.settings_service.set_decimal_places(decimal_places)
                print(f"{Fore.GREEN}✅ Decimal places set to {decimal_places}")
            except (ValueError, Exception) as e:
                print(f"{Fore.RED}❌ Invalid input: {e}")
                
        elif choice == '3':
            try:
                max_transactions = int(input("Enter max recent transactions to show: "))
                self.settings_service.set_max_recent_transactions(max_transactions)
                print(f"{Fore.GREEN}✅ Max recent transactions set to {max_transactions}")
            except (ValueError, Exception) as e:
                print(f"{Fore.RED}❌ Invalid input: {e}")
                
        elif choice == '4':
            current = self.settings_service.get_auto_update_charts()
            new_value = not current
            self.settings_service.set_auto_update_charts(new_value)
            status = "enabled" if new_value else "disabled"
            print(f"{Fore.GREEN}✅ Auto-update charts {status}")
    
    def _reset_settings(self):
        """Reset settings to defaults"""
        confirm = input(f"\n{Fore.YELLOW}⚠️  Reset all settings to defaults? (y/N): ").strip().lower()
        if confirm in ['y', 'yes']:
            self.settings_service.reset_to_defaults()
            self.currency_service = get_currency_service()  # Refresh service
            print(f"{Fore.GREEN}✅ Settings reset to defaults")
        else:
            print(f"{Fore.YELLOW}Operation cancelled")
    
    def _view_all_settings(self):
        """View all current settings"""
        print(f"\n{Fore.CYAN}📋 Current Settings")
        settings = self.settings_service.get_all_settings()
        
        headers = ["Setting", "Value"]
        table_data = []
        
        for key, value in settings.items():
            if key == 'currency':
                currency_info = self.settings_service.get_current_currency_info()
                value = f"{currency_info['name']} ({currency_info['symbol']})"
            
            table_data.append([key.replace('_', ' ').title(), str(value)])
        
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
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
        symbol = self.currency_service.get_currency_symbol()
        while True:
            try:
                amount_input = input(f"Amount ({symbol}): ").strip()
                amount = self.currency_service.parse_amount(amount_input)
                if amount <= 0:
                    print(f"{Fore.RED}❌ Amount must be positive!")
                    continue
                return amount
            except ValueError as e:
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
    
    def run(self):
        """Main application loop"""
        # Check for first run
        if self.settings_service.is_first_run():
            self._first_run_setup()
        
        self.display_header()
        
        # Check if tracker is connected
        if not self.tracker.is_connected():
            print(f"{Fore.RED}❌ Could not connect to Google Sheets. Please check your setup.")
            return
        
        while self.running:
            self.display_menu()
            choice = self.get_user_choice()
            self.handle_choice(choice)
    
    def _first_run_setup(self):
        """Handle first run setup"""
        print(f"{Fore.CYAN}🎉 Welcome to Finance Tracker!")
        print(f"{Fore.CYAN}=" * 30)
        print(f"{Fore.YELLOW}Let's set up your preferences...")
        
        # Currency selection
        print(f"\n{Fore.CYAN}💱 Currency Selection")
        currencies = self.settings_service.get_available_currencies()
        
        print(f"\n{Fore.YELLOW}Please choose your preferred currency:")
        for i, (code, info) in enumerate(currencies.items(), 1):
            print(f"{i}. {info['symbol']} {info['name']} ({code})")
        
        while True:
            try:
                choice = input(f"\n{Fore.WHITE}Enter your choice (1-{len(currencies)}): ").strip()
                choice_idx = int(choice) - 1
                
                if 0 <= choice_idx < len(currencies):
                    currency_code = list(currencies.keys())[choice_idx]
                    self.settings_service.set_currency(currency_code)
                    self.currency_service = get_currency_service()  # Refresh service
                    
                    currency_info = currencies[currency_code]
                    print(f"{Fore.GREEN}✅ Currency set to {currency_info['name']} ({currency_info['symbol']})")
                    break
                else:
                    print(f"{Fore.RED}❌ Invalid choice! Please enter 1-{len(currencies)}.")
                    
            except ValueError:
                print(f"{Fore.RED}❌ Please enter a valid number!")
        
        self.settings_service.set_first_run_complete()
        print(f"\n{Fore.GREEN}🎯 Setup complete! Let's start tracking your finances.")
        input(f"\n{Fore.CYAN}Press Enter to continue...")
        print()  # Add space 