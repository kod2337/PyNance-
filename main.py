#!/usr/bin/env python3
"""
Finance Tracker with AI Integration - Main CLI Interface
Enhanced personal finance tracker with Google Gemini AI features
"""

import sys
import os
from pathlib import Path
from colorama import Fore, Style, init

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass

# Initialize colorama for colored output
init(autoreset=True)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.finance_tracker_modular import FinanceTracker


def print_banner():
    """Print application banner"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════╗
║                                                      ║
║     {Fore.YELLOW}🤖 AI-POWERED FINANCE TRACKER 💰{Fore.CYAN}              ║
║                                                      ║
║        {Fore.GREEN}Smart • Automated • Insightful{Fore.CYAN}                ║
║                                                      ║
╚══════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def print_menu():
    """Print the main menu"""
    menu = f"""
{Fore.CYAN}┌─────────────── MAIN MENU ───────────────┐{Style.RESET_ALL}
{Fore.YELLOW}│  BASIC TRANSACTIONS                     │{Style.RESET_ALL}
{Fore.WHITE}│  1. Add Transaction (Manual)            │
│  2. View Recent Transactions            │
│  3. Category Summary                    │
│  4. Create Charts                       │{Style.RESET_ALL}
{Fore.YELLOW}│                                         │
│  🤖 AI-POWERED FEATURES                 │{Style.RESET_ALL}
{Fore.GREEN}│  5. Add Transaction (AI Categories)     │
│  6. Natural Language Transaction       │
│  7. Generate AI Insights               │
│  8. AI Financial Report                │{Style.RESET_ALL}
{Fore.YELLOW}│                                         │
│  UTILITIES                              │{Style.RESET_ALL}
{Fore.WHITE}│  9. Check Connection Status             │
│  10. Setup Instructions                 │
│  0. Exit                                │{Style.RESET_ALL}
{Fore.CYAN}└─────────────────────────────────────────┘{Style.RESET_ALL}
"""
    print(menu)


def get_user_input(prompt: str, input_type=str, required=True):
    """Get user input with validation"""
    while True:
        try:
            user_input = input(f"{Fore.CYAN}{prompt}{Style.RESET_ALL}").strip()
            
            if not user_input and required:
                print(f"{Fore.RED}❌ This field is required. Please try again.{Style.RESET_ALL}")
                continue
            
            if not user_input and not required:
                return None
            
            if input_type == float:
                return float(user_input)
            elif input_type == int:
                return int(user_input)
            else:
                return user_input
                
        except ValueError:
            print(f"{Fore.RED}❌ Invalid input. Please enter a valid {input_type.__name__}.{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Operation cancelled.{Style.RESET_ALL}")
            return None


def add_manual_transaction(tracker: FinanceTracker):
    """Add transaction manually with user input"""
    print(f"\n{Fore.CYAN}➕ ADD NEW TRANSACTION{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─' * 30}{Style.RESET_ALL}")
    
    # Get transaction details
    description = get_user_input("📝 Description: ")
    if not description:
        return
    
    category = get_user_input("📂 Category: ")
    if not category:
        return
    
    amount = get_user_input("💵 Amount: $", float)
    if amount is None:
        return
    
    print(f"\n{Fore.YELLOW}Transaction Type:{Style.RESET_ALL}")
    print("1. Income")
    print("2. Expense")
    
    type_choice = get_user_input("Choose type (1 or 2): ")
    if type_choice == "1":
        transaction_type = "Income"
    elif type_choice == "2":
        transaction_type = "Expense"
    else:
        print(f"{Fore.RED}❌ Invalid choice. Defaulting to Expense.{Style.RESET_ALL}")
        transaction_type = "Expense"
    
    # Add transaction
    success = tracker.add_transaction(description, category, amount, transaction_type)
    if success:
        print(f"{Fore.GREEN}✅ Transaction added successfully!{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ Failed to add transaction.{Style.RESET_ALL}")


def add_ai_categorized_transaction(tracker: FinanceTracker):
    """Add transaction with AI-powered categorization"""
    if not tracker.is_ai_available():
        print(f"{Fore.RED}❌ AI features are not available. Please check your GEMINI_API_KEY.{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.CYAN}🤖 ADD TRANSACTION WITH AI CATEGORIZATION{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─' * 45}{Style.RESET_ALL}")
    
    # Get transaction details
    description = get_user_input("📝 Description: ")
    if not description:
        return
    
    amount = get_user_input("💵 Amount: $", float)
    if amount is None:
        return
    
    print(f"\n{Fore.YELLOW}Transaction Type:{Style.RESET_ALL}")
    print("1. Income")
    print("2. Expense")
    
    type_choice = get_user_input("Choose type (1 or 2): ")
    if type_choice == "1":
        transaction_type = "Income"
    elif type_choice == "2":
        transaction_type = "Expense"
    else:
        print(f"{Fore.RED}❌ Invalid choice. Defaulting to Expense.{Style.RESET_ALL}")
        transaction_type = "Expense"
    
    # Add transaction with AI categorization
    success = tracker.add_transaction_with_ai_category(description, amount, transaction_type)
    if success:
        print(f"{Fore.GREEN}✅ Transaction added with AI categorization!{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ Failed to add transaction.{Style.RESET_ALL}")


def add_natural_language_transaction(tracker: FinanceTracker):
    """Add transaction using natural language"""
    if not tracker.is_ai_available():
        print(f"{Fore.RED}❌ AI features are not available. Please check your GEMINI_API_KEY.{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.CYAN}🗣️  NATURAL LANGUAGE TRANSACTION{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─' * 35}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Examples:{Style.RESET_ALL}")
    print("• 'I spent $25 on groceries at Walmart yesterday'")
    print("• 'Got paid $500 for freelance work'")
    print("• 'Bought coffee for $4.50 this morning'")
    print("• 'Received $1000 salary today'")
    print()
    
    natural_input = get_user_input("💬 Describe your transaction: ")
    if not natural_input:
        return
    
    # Process natural language transaction
    success = tracker.add_transaction_natural_language(natural_input)
    if success:
        print(f"{Fore.GREEN}✅ Natural language transaction processed successfully!{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ Failed to process transaction.{Style.RESET_ALL}")


def generate_ai_insights(tracker: FinanceTracker):
    """Generate AI-powered financial insights"""
    if not tracker.is_ai_available():
        print(f"{Fore.RED}❌ AI features are not available. Please check your GEMINI_API_KEY.{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.CYAN}🧠 GENERATING AI INSIGHTS...{Style.RESET_ALL}")
    success = tracker.generate_ai_insights()
    
    if not success:
        print(f"{Fore.YELLOW}⚠️  Could not generate insights. Make sure you have transaction data.{Style.RESET_ALL}")


def generate_ai_report(tracker: FinanceTracker):
    """Generate AI-powered financial report"""
    if not tracker.is_ai_available():
        print(f"{Fore.RED}❌ AI features are not available. Please check your GEMINI_API_KEY.{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.CYAN}📊 AI FINANCIAL REPORT{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─' * 25}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Report Period:{Style.RESET_ALL}")
    print("1. Weekly")
    print("2. Monthly")
    print("3. Yearly")
    
    period_choice = get_user_input("Choose period (1, 2, or 3): ")
    period_map = {"1": "weekly", "2": "monthly", "3": "yearly"}
    period = period_map.get(period_choice, "monthly")
    
    success = tracker.generate_ai_report(period)
    if not success:
        print(f"{Fore.YELLOW}⚠️  Could not generate report. Make sure you have transaction data.{Style.RESET_ALL}")


def check_status(tracker: FinanceTracker):
    """Check connection and feature status"""
    print(f"\n{Fore.CYAN}🔍 SYSTEM STATUS{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─' * 20}{Style.RESET_ALL}")
    
    # Google Sheets connection
    sheets_status = "✅ Connected" if tracker.is_connected() else "❌ Not Connected"
    print(f"Google Sheets: {sheets_status}")
    
    # AI features
    ai_status = "✅ Available" if tracker.is_ai_available() else "❌ Not Available"
    print(f"AI Features: {ai_status}")
    
    # Current balance
    try:
        balance = tracker.get_current_balance()
        balance_str = f"${balance:.2f}"
        balance_color = Fore.GREEN if balance >= 0 else Fore.RED
        print(f"Current Balance: {balance_color}{balance_str}{Style.RESET_ALL}")
    except:
        print("Current Balance: ❌ Could not retrieve")
    
    if not tracker.is_ai_available():
        print(f"\n{Fore.YELLOW}💡 To enable AI features:{Style.RESET_ALL}")
        print("1. Get a Google Gemini API key from https://makersuite.google.com/app/apikey")
        print("2. Set the GEMINI_API_KEY environment variable")
        print("3. Restart the application")


def show_setup_instructions():
    """Show setup instructions"""
    instructions = f"""
{Fore.CYAN}📚 SETUP INSTRUCTIONS{Style.RESET_ALL}
{Fore.CYAN}{'─' * 25}{Style.RESET_ALL}

{Fore.YELLOW}🔐 GOOGLE SHEETS SETUP:{Style.RESET_ALL}
1. Go to Google Cloud Console (console.cloud.google.com)
2. Create a new project or select existing one
3. Enable Google Sheets API and Google Drive API
4. Create Service Account credentials
5. Download credentials.json file to project root
6. Share your Google Sheet with the service account email

{Fore.YELLOW}🤖 AI FEATURES SETUP:{Style.RESET_ALL}
1. Visit https://makersuite.google.com/app/apikey
2. Create a new API key for Gemini
3. Set environment variable: GEMINI_API_KEY=your_api_key
4. Restart the application

{Fore.YELLOW}📦 DEPENDENCIES:{Style.RESET_ALL}
Run: pip install -r requirements.txt

{Fore.GREEN}✅ Once setup is complete, you'll have access to:{Style.RESET_ALL}
• Smart transaction categorization
• Natural language transaction entry
• AI-powered financial insights
• Intelligent expense reporting
• Automated chart generation
"""
    print(instructions)


def main():
    """Main application loop"""
    print_banner()
    
    # Initialize the finance tracker
    try:
        tracker = FinanceTracker()
    except Exception as e:
        print(f"{Fore.RED}❌ Error initializing Finance Tracker: {str(e)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Run option 10 for setup instructions.{Style.RESET_ALL}")
        return
    
    # Check if basic connection is available
    if not tracker.is_connected():
        print(f"{Fore.YELLOW}⚠️  Google Sheets connection failed. Some features may not work.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}💡 Run option 10 for setup instructions.{Style.RESET_ALL}")
    
    # Show AI availability
    if tracker.is_ai_available():
        print(f"{Fore.GREEN}🤖 AI features are enabled!{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠️  AI features are disabled. Set GEMINI_API_KEY to enable.{Style.RESET_ALL}")
    
    # Main menu loop
    while True:
        try:
            print_menu()
            choice = get_user_input("Enter your choice (0-10): ")
            
            if choice == "0":
                print(f"{Fore.GREEN}👋 Thank you for using AI Finance Tracker!{Style.RESET_ALL}")
                break
            elif choice == "1":
                add_manual_transaction(tracker)
            elif choice == "2":
                tracker.view_transactions()
            elif choice == "3":
                tracker.get_category_summary()
            elif choice == "4":
                tracker.create_charts()
            elif choice == "5":
                add_ai_categorized_transaction(tracker)
            elif choice == "6":
                add_natural_language_transaction(tracker)
            elif choice == "7":
                generate_ai_insights(tracker)
            elif choice == "8":
                generate_ai_report(tracker)
            elif choice == "9":
                check_status(tracker)
            elif choice == "10":
                show_setup_instructions()
            else:
                print(f"{Fore.RED}❌ Invalid choice. Please try again.{Style.RESET_ALL}")
            
            # Pause before showing menu again
            if choice != "0":
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                print("\n" * 2)  # Clear screen spacing
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}❌ An error occurred: {str(e)}{Style.RESET_ALL}")
            input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")


if __name__ == "__main__":
    main() 