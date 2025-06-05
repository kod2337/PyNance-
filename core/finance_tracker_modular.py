"""
Finance Tracker - Modular Version with AI Integration
Clean, modular personal finance tracker with Google Sheets integration and Gemini AI
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
from services.ai_service import get_ai_service


class FinanceTracker:
    """Main Finance Tracker class with modular architecture and AI features"""
    
    def __init__(self):
        self.sheets_service = SheetsService()
        self.chart_service = ChartService(self.sheets_service)  # Pass sheets_service to chart_service
        self.currency_service = get_currency_service()
        self.settings_service = get_settings_service()
        self.ai_service = get_ai_service()
        
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
        """Add a new transaction with optional AI categorization"""
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
    
    def add_transaction_with_ai_category(self, description: str, amount: float, transaction_type: str) -> bool:
        """Add transaction with AI-powered smart categorization"""
        try:
            # Get user transaction history for pattern learning
            user_history = self.sheets_service.get_all_records()
            
            # Use AI to suggest category
            suggested_category = self.ai_service.categorize_transaction(
                description, amount, user_history
            )
            
            print(f"{Fore.CYAN}🤖 AI suggested category: {suggested_category}")
            
            # Add transaction with AI-suggested category
            return self.add_transaction(description, suggested_category, amount, transaction_type)
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error adding AI-categorized transaction: {str(e)}")
            return False
    
    def add_transaction_natural_language(self, natural_input: str) -> bool:
        """Add transaction using natural language input"""
        try:
            print(f"{Fore.CYAN}🤖 Processing natural language input...")
            
            # Parse natural language using AI
            parsed_data = self.ai_service.parse_natural_language_transaction(natural_input)
            
            if not parsed_data or not parsed_data.get('description'):
                print(f"{Fore.RED}❌ Could not parse the transaction. Please try again.")
                return False
            
            # Display parsed information
            print(f"{Fore.GREEN}✅ Parsed transaction:")
            print(f"   📝 Description: {parsed_data['description']}")
            print(f"   💵 Amount: ${abs(parsed_data['amount']):.2f}")
            print(f"   📂 Category: {parsed_data['category']}")
            print(f"   📅 Date: {parsed_data['date']}")
            print(f"   🏷️  Type: {parsed_data['type']}")
            
            # Add the transaction
            return self.add_transaction(
                description=parsed_data['description'],
                category=parsed_data['category'],
                amount=abs(parsed_data['amount']),
                transaction_type=parsed_data['type']
            )
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error processing natural language transaction: {str(e)}")
            return False
    
    def generate_ai_insights(self) -> bool:
        """Generate AI-powered financial insights and recommendations"""
        try:
            print(f"{Fore.CYAN}🤖 Generating financial insights...")
            
            # Get transaction data
            transactions = self.sheets_service.get_all_records()
            current_balance = self.get_current_balance()
            
            if not transactions:
                print(f"{Fore.YELLOW}📝 No transactions found. Add some transactions first.")
                return False
            
            # Generate insights using AI
            insights = self.ai_service.generate_financial_insights(transactions, current_balance)
            
            # Display insights
            self._display_ai_insights(insights)
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error generating insights: {str(e)}")
            return False
    
    def generate_ai_report(self, period: str = "monthly") -> bool:
        """Generate AI-powered expense report"""
        try:
            print(f"{Fore.CYAN}🤖 Generating {period} AI report...")
            
            # Get transaction data
            transactions = self.sheets_service.get_all_records()
            
            if not transactions:
                print(f"{Fore.YELLOW}📝 No transactions found. Add some transactions first.")
                return False
            
            # Generate report using AI
            report = self.ai_service.generate_expense_report(transactions, period)
            
            # Display report
            print(report)
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error generating report: {str(e)}")
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
    
    def is_ai_available(self) -> bool:
        """Check if AI features are available"""
        return self.ai_service.is_available()
    
    def _display_ai_insights(self, insights: Dict[str, Any]):
        """Display AI-generated insights in a formatted way"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{'🤖 AI FINANCIAL INSIGHTS':^60}")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        # Spending Patterns
        print(f"{Fore.YELLOW}📊 SPENDING PATTERNS:")
        print(f"{Style.RESET_ALL}{insights.get('spending_patterns', 'No patterns detected')}\n")
        
        # Budget Recommendations
        print(f"{Fore.GREEN}💡 BUDGET RECOMMENDATIONS:")
        print(f"{Style.RESET_ALL}{insights.get('budget_recommendations', 'No recommendations available')}\n")
        
        # Savings Tips
        print(f"{Fore.BLUE}💰 SAVINGS TIPS:")
        print(f"{Style.RESET_ALL}{insights.get('savings_tips', 'No tips available')}\n")
        
        # Anomalies
        print(f"{Fore.RED}🚨 ANOMALIES DETECTED:")
        print(f"{Style.RESET_ALL}{insights.get('anomalies', 'No anomalies detected')}\n")
        
        # Monthly Trend
        print(f"{Fore.MAGENTA}📈 MONTHLY TREND:")
        print(f"{Style.RESET_ALL}{insights.get('monthly_trend', 'No trend analysis available')}\n")
        
        # Top Categories
        if insights.get('top_categories'):
            print(f"{Fore.CYAN}🏆 TOP SPENDING CATEGORIES:")
            top_cats = insights['top_categories']
            if isinstance(top_cats, list):
                for i, category in enumerate(top_cats[:3], 1):
                    print(f"{Style.RESET_ALL}{i}. {category}")
            else:
                print(f"{Style.RESET_ALL}{top_cats}")
        
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

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
                record['Date'][:10],  # Show only date part
                self._truncate_text(record['Description'], 25),
                self._truncate_text(record['Category'], 15),
                amount_str,
                record['Type'],
                balance_str
            ])
        
        print(f"\n{Fore.CYAN}📊 Recent Transactions (Last {len(recent_records)}):{Style.RESET_ALL}")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print()
    
    def _display_category_summary(self, category_totals: Dict[str, Dict[str, float]]):
        """Display category summary with AI enhancement suggestion"""
        from tabulate import tabulate
        
        # Prepare data for table
        table_data = []
        total_income = 0
        total_expenses = 0
        
        for category, totals in category_totals.items():
            income = totals['income']
            expense = totals['expense']
            net = income - expense
            
            total_income += income
            total_expenses += expense
            
            # Format amounts with colors
            income_str = self.currency_service.format_amount_with_color(
                income, Fore.GREEN, Fore.GREEN, Style.RESET_ALL
            ) if income > 0 else "$0.00"
            
            expense_str = self.currency_service.format_amount_with_color(
                -expense, Fore.RED, Fore.RED, Style.RESET_ALL
            ) if expense > 0 else "$0.00"
            
            net_color = Fore.GREEN if net >= 0 else Fore.RED
            net_str = f"{net_color}${abs(net):.2f}{Style.RESET_ALL}"
            
            table_data.append([
                self._truncate_text(category, 20),
                income_str,
                expense_str,
                net_str
            ])
        
        # Sort by total activity (income + expenses)
        table_data.sort(key=lambda x: float(x[1].replace('$', '').replace(',', '')) + 
                                     float(x[2].replace('$', '').replace(',', '')), reverse=True)
        
        # Add totals row
        total_net = total_income - total_expenses
        net_color = Fore.GREEN if total_net >= 0 else Fore.RED
        table_data.append([
            f"{Fore.CYAN}TOTAL{Style.RESET_ALL}",
            f"{Fore.GREEN}${total_income:.2f}{Style.RESET_ALL}",
            f"{Fore.RED}${total_expenses:.2f}{Style.RESET_ALL}",
            f"{net_color}${abs(total_net):.2f}{Style.RESET_ALL}"
        ])
        
        headers = ["Category", "Income", "Expenses", "Net"]
        print(f"\n{Fore.CYAN}📈 Category Summary:{Style.RESET_ALL}")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print()
        
        # AI Enhancement suggestion
        if self.ai_service.is_available():
            print(f"{Fore.CYAN}💡 Tip: Use 'insights' command for AI-powered financial analysis!{Style.RESET_ALL}")

    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to specified length"""
        return text[:max_length-3] + "..." if len(text) > max_length else text 