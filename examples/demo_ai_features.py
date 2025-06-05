#!/usr/bin/env python3
"""
AI Features Demo for Finance Tracker
Demonstrates the AI capabilities without requiring full Google Sheets setup
"""

import os
import sys
from pathlib import Path
from colorama import Fore, Style, init

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass

# Initialize colorama
init(autoreset=True)

# Add project root to path
project_root = Path(__file__).parent.parent  # Go up one level since we're in examples/
sys.path.insert(0, str(project_root))

from services.ai_service import get_ai_service


def print_banner():
    """Print demo banner"""
    banner = f"""
{Fore.CYAN}╔════════════════════════════════════════════════════════╗
║                                                        ║
║     {Fore.YELLOW}🤖 AI FINANCE TRACKER - DEMO MODE 🚀{Fore.CYAN}           ║
║                                                        ║
║        {Fore.GREEN}Showcasing Gemini AI Integration{Fore.CYAN}               ║
║                                                        ║
╚════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def demo_natural_language_parsing():
    """Demonstrate natural language transaction parsing"""
    print(f"\n{Fore.CYAN}🗣️  NATURAL LANGUAGE PROCESSING DEMO{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─' * 45}{Style.RESET_ALL}")
    
    ai_service = get_ai_service()
    
    # Sample natural language inputs
    sample_inputs = [
        "I spent $25 on groceries at Walmart yesterday",
        "Got paid $1500 for freelance work today",
        "Bought coffee for $4.50 this morning",
        "Paid $50 for gas at Shell station",
        "Received $100 cash gift from grandma",
        "Spent 35 dollars on lunch at McDonald's"
    ]
    
    print(f"{Fore.YELLOW}Sample Inputs:{Style.RESET_ALL}")
    for i, input_text in enumerate(sample_inputs, 1):
        print(f"{i}. \"{input_text}\"")
    
    print(f"\n{Fore.GREEN}Processing with AI...{Style.RESET_ALL}\n")
    
    for i, input_text in enumerate(sample_inputs, 1):
        print(f"{Fore.CYAN}Input {i}: {Style.RESET_ALL}\"{input_text}\"")
        
        try:
            result = ai_service.parse_natural_language_transaction(input_text)
            
            if result:
                print(f"{Fore.GREEN}✅ Parsed Result:{Style.RESET_ALL}")
                print(f"   📝 Description: {result.get('description', 'N/A')}")
                print(f"   💵 Amount: ${abs(float(result.get('amount', 0))):.2f}")
                print(f"   📂 Category: {result.get('category', 'N/A')}")
                print(f"   📅 Date: {result.get('date', 'N/A')}")
                print(f"   🏷️  Type: {result.get('type', 'N/A')}")
            else:
                print(f"{Fore.RED}❌ Failed to parse{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
        
        print()


def demo_smart_categorization():
    """Demonstrate AI-powered transaction categorization"""
    print(f"\n{Fore.CYAN}🤖 SMART CATEGORIZATION DEMO{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─' * 35}{Style.RESET_ALL}")
    
    ai_service = get_ai_service()
    
    # Sample transactions for categorization
    sample_transactions = [
        ("Starbucks coffee", 4.50),
        ("Uber ride downtown", 15.75),
        ("Grocery shopping at Target", 67.89),
        ("Netflix subscription", 15.99),
        ("Rent payment", 1200.00),
        ("Freelance web design", -500.00),  # Negative for income
        ("Pharmacy prescription", 25.30),
        ("Amazon purchase", 45.67),
        ("Gas station fill-up", 55.00),
        ("Movie theater tickets", 24.00)
    ]
    
    print(f"{Fore.YELLOW}Testing AI categorization on various transactions:{Style.RESET_ALL}\n")
    
    for description, amount in sample_transactions:
        print(f"{Fore.WHITE}Transaction: {Style.RESET_ALL}\"{description}\" (${abs(amount):.2f})")
        
        try:
            category = ai_service.categorize_transaction(description, amount)
            print(f"{Fore.GREEN}🎯 AI Suggested Category: {Style.RESET_ALL}{category}")
        except Exception as e:
            print(f"{Fore.RED}❌ Categorization failed: {str(e)}{Style.RESET_ALL}")
        
        print()


def demo_financial_insights():
    """Demonstrate AI financial insights generation"""
    print(f"\n{Fore.CYAN}🧠 FINANCIAL INSIGHTS DEMO{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─' * 30}{Style.RESET_ALL}")
    
    ai_service = get_ai_service()
    
    # Sample transaction data for analysis
    sample_transactions = [
        {"description": "Grocery shopping", "amount": -125.50, "category": "Food & Dining", "date": "2024-01-15"},
        {"description": "Salary payment", "amount": 3500.00, "category": "Salary", "date": "2024-01-15"},
        {"description": "Coffee", "amount": -4.50, "category": "Food & Dining", "date": "2024-01-14"},
        {"description": "Gas station", "amount": -45.00, "category": "Transportation", "date": "2024-01-14"},
        {"description": "Netflix", "amount": -15.99, "category": "Entertainment", "date": "2024-01-13"},
        {"description": "Rent", "amount": -1200.00, "category": "Bills & Utilities", "date": "2024-01-01"},
        {"description": "Freelance work", "amount": 750.00, "category": "Freelance", "date": "2024-01-12"},
        {"description": "Restaurant dinner", "amount": -85.75, "category": "Food & Dining", "date": "2024-01-10"},
        {"description": "Pharmacy", "amount": -25.30, "category": "Healthcare", "date": "2024-01-09"},
        {"description": "Amazon purchase", "amount": -67.89, "category": "Shopping", "date": "2024-01-08"}
    ]
    
    current_balance = 2500.00
    
    print(f"{Fore.YELLOW}Sample Data:{Style.RESET_ALL}")
    print(f"Transactions: {len(sample_transactions)}")
    print(f"Current Balance: ${current_balance:.2f}")
    print(f"\n{Fore.GREEN}Generating AI insights...{Style.RESET_ALL}\n")
    
    try:
        insights = ai_service.generate_financial_insights(sample_transactions, current_balance)
        
        # Display insights in a formatted way
        print(f"{Fore.CYAN}{'='*50}")
        print(f"{'🤖 AI FINANCIAL INSIGHTS':^50}")
        print(f"{'='*50}{Style.RESET_ALL}\n")
        
        sections = [
            ("📊 SPENDING PATTERNS", "spending_patterns"),
            ("💡 BUDGET RECOMMENDATIONS", "budget_recommendations"),
            ("💰 SAVINGS TIPS", "savings_tips"),
            ("🚨 ANOMALIES DETECTED", "anomalies"),
            ("📈 MONTHLY TREND", "monthly_trend"),
            ("🏆 TOP CATEGORIES", "top_categories")
        ]
        
        for title, key in sections:
            print(f"{Fore.YELLOW}{title}:{Style.RESET_ALL}")
            insight = insights.get(key, f"No {key.replace('_', ' ')} available")
            print(f"{insight}\n")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Failed to generate insights: {str(e)}{Style.RESET_ALL}")


def demo_expense_report():
    """Demonstrate AI expense report generation"""
    print(f"\n{Fore.CYAN}📊 AI EXPENSE REPORT DEMO{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─' * 30}{Style.RESET_ALL}")
    
    ai_service = get_ai_service()
    
    # Sample data for report generation
    sample_transactions = [
        {"description": "Grocery shopping", "amount": -125.50, "category": "Food & Dining", "date": "2024-01-15"},
        {"description": "Salary payment", "amount": 3500.00, "category": "Salary", "date": "2024-01-15"},
        {"description": "Coffee purchases", "amount": -67.50, "category": "Food & Dining", "date": "2024-01-14"},
        {"description": "Gas and transportation", "amount": -145.00, "category": "Transportation", "date": "2024-01-14"},
        {"description": "Entertainment", "amount": -115.99, "category": "Entertainment", "date": "2024-01-13"},
        {"description": "Rent payment", "amount": -1200.00, "category": "Bills & Utilities", "date": "2024-01-01"},
        {"description": "Freelance income", "amount": 750.00, "category": "Freelance", "date": "2024-01-12"},
        {"description": "Shopping", "amount": -245.75, "category": "Shopping", "date": "2024-01-10"},
        {"description": "Healthcare", "amount": -125.30, "category": "Healthcare", "date": "2024-01-09"},
        {"description": "Miscellaneous", "amount": -167.89, "category": "Other", "date": "2024-01-08"}
    ]
    
    print(f"{Fore.YELLOW}Generating monthly expense report...{Style.RESET_ALL}\n")
    
    try:
        report = ai_service.generate_expense_report(sample_transactions, "monthly")
        print(report)
    except Exception as e:
        print(f"{Fore.RED}❌ Failed to generate report: {str(e)}{Style.RESET_ALL}")


def check_ai_availability():
    """Check if AI features are available"""
    print(f"\n{Fore.CYAN}🔍 AI AVAILABILITY CHECK{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─' * 25}{Style.RESET_ALL}")
    
    ai_service = get_ai_service()
    
    if ai_service.is_available():
        print(f"{Fore.GREEN}✅ AI features are available and ready!{Style.RESET_ALL}")
        print(f"   🤖 Model: Gemini Pro")
        print(f"   🔑 API Key: Configured")
        return True
    else:
        print(f"{Fore.RED}❌ AI features are not available{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}💡 To enable AI features:{Style.RESET_ALL}")
        print("1. Get a Google Gemini API key from: https://makersuite.google.com/app/apikey")
        print("2. Set the GEMINI_API_KEY environment variable")
        print("3. Restart the demo")
        print(f"\n{Fore.CYAN}Example:{Style.RESET_ALL}")
        print("export GEMINI_API_KEY='your_api_key_here'")
        print("python demo_ai_features.py")
        return False


def main():
    """Main demo function"""
    print_banner()
    
    # Check AI availability first
    if not check_ai_availability():
        print(f"\n{Fore.YELLOW}Demo will show fallback behavior without AI{Style.RESET_ALL}")
        input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    # Run all demos
    try:
        demo_smart_categorization()
        input(f"{Fore.CYAN}Press Enter to continue to next demo...{Style.RESET_ALL}")
        
        demo_natural_language_parsing()
        input(f"{Fore.CYAN}Press Enter to continue to next demo...{Style.RESET_ALL}")
        
        demo_financial_insights()
        input(f"{Fore.CYAN}Press Enter to continue to next demo...{Style.RESET_ALL}")
        
        demo_expense_report()
        
        print(f"\n{Fore.GREEN}🎉 Demo completed!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Ready to try the full Finance Tracker? Run: python main.py{Style.RESET_ALL}")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Demo interrupted. Goodbye!{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Demo error: {str(e)}{Style.RESET_ALL}")


if __name__ == "__main__":
    main() 