#!/usr/bin/env python3
"""
Test script to diagnose Google Sheets data retrieval issues
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
    print("python-dotenv not installed, skipping .env loading")

# Initialize colorama
init(autoreset=True)

# Add project root to path
project_root = Path(__file__).parent.parent  # Go up one level since we're in tests/
sys.path.insert(0, str(project_root))

from services.sheets_service import SheetsService
from core.finance_tracker_modular import FinanceTracker


def test_direct_sheets_connection():
    """Test direct sheets service connection"""
    print(f"{Fore.CYAN}🔍 Testing Direct Sheets Service Connection{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─' * 45}{Style.RESET_ALL}")
    
    sheets_service = SheetsService()
    
    # Test connection
    if sheets_service.connect():
        print(f"{Fore.GREEN}✅ Sheets service connected successfully")
        
        # Test getting records
        print(f"\n📊 Testing record retrieval...")
        records = sheets_service.get_all_records()
        
        print(f"Records returned: {len(records)}")
        if records:
            print(f"Sample record: {records[0]}")
            print(f"Total records: {len(records)}")
            
            # Show some details about the data
            for i, record in enumerate(records[:3]):
                print(f"Record {i+1}: {record}")
        else:
            print(f"{Fore.YELLOW}⚠️  No records returned from sheets service")
            
            # Try to get raw data to debug
            try:
                if sheets_service.transactions_worksheet:
                    all_values = sheets_service.transactions_worksheet.get_all_values()
                    print(f"Raw worksheet values: {len(all_values)} rows")
                    if all_values:
                        print(f"Headers: {all_values[0]}")
                        if len(all_values) > 1:
                            print(f"Sample data row: {all_values[1]}")
                        else:
                            print(f"{Fore.YELLOW}⚠️  Only headers found, no data rows")
                    else:
                        print(f"{Fore.RED}❌ No values found in worksheet")
            except Exception as e:
                print(f"{Fore.RED}❌ Error getting raw data: {str(e)}")
        
        return True
    else:
        print(f"{Fore.RED}❌ Failed to connect to sheets service")
        return False


def test_finance_tracker_integration():
    """Test finance tracker's access to sheets data"""
    print(f"\n{Fore.CYAN}🔍 Testing Finance Tracker Integration{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─' * 40}{Style.RESET_ALL}")
    
    try:
        tracker = FinanceTracker()
        
        if tracker.is_connected():
            print(f"{Fore.GREEN}✅ Finance tracker connected to sheets")
            
            # Test getting transactions through tracker
            print(f"\n📊 Testing tracker transaction retrieval...")
            
            # Test balance
            balance = tracker.get_current_balance()
            print(f"Current balance: ${balance:.2f}")
            
            # Test getting records directly from sheets service
            records = tracker.sheets_service.get_all_records()
            print(f"Records from tracker.sheets_service: {len(records)}")
            
            if records:
                print(f"✅ Found {len(records)} transactions")
                for i, record in enumerate(records[:3]):
                    print(f"   Transaction {i+1}: {record.get('Description', 'N/A')} - ${record.get('Amount', 0)}")
            else:
                print(f"{Fore.YELLOW}⚠️  No transactions found through tracker")
            
            return True
        else:
            print(f"{Fore.RED}❌ Finance tracker not connected to sheets")
            return False
            
    except Exception as e:
        print(f"{Fore.RED}❌ Error testing finance tracker: {str(e)}")
        return False


def test_ai_integration():
    """Test AI service integration with actual data"""
    print(f"\n{Fore.CYAN}🔍 Testing AI Integration with Real Data{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─' * 38}{Style.RESET_ALL}")
    
    try:
        tracker = FinanceTracker()
        
        if not tracker.is_ai_available():
            print(f"{Fore.YELLOW}⚠️  AI service not available")
            return False
        
        # Get actual transaction data
        transactions = tracker.sheets_service.get_all_records()
        current_balance = tracker.get_current_balance()
        
        print(f"Transactions for AI: {len(transactions)}")
        print(f"Current balance for AI: ${current_balance:.2f}")
        
        if not transactions:
            print(f"{Fore.YELLOW}⚠️  No transaction data available for AI")
            return False
        
        # Test AI insights with real data
        print(f"\n🤖 Testing AI insights generation...")
        insights = tracker.ai_service.generate_financial_insights(transactions, current_balance)
        
        print(f"AI insights generated: {bool(insights)}")
        if insights:
            print(f"Insights keys: {list(insights.keys())}")
            print(f"Sample insight - spending patterns: {insights.get('spending_patterns', 'N/A')}")
        
        # Test AI report with real data
        print(f"\n📊 Testing AI report generation...")
        report = tracker.ai_service.generate_expense_report(transactions, "weekly")
        
        if report and "No transactions available" not in report:
            print(f"✅ AI report generated successfully with real data")
            print(f"Report preview: {report[:200]}...")
        else:
            print(f"{Fore.YELLOW}⚠️  AI report shows no data")
            print(f"Report content: {report[:500]}")
        
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error testing AI integration: {str(e)}")
        return False


def main():
    """Main diagnostic function"""
    print(f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════╗
║                                                       ║
║     {Fore.YELLOW}🔍 GOOGLE SHEETS DATA DIAGNOSTIC 📊{Fore.CYAN}              ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}
""")
    
    # Test 1: Direct sheets connection
    sheets_ok = test_direct_sheets_connection()
    
    # Test 2: Finance tracker integration
    tracker_ok = test_finance_tracker_integration()
    
    # Test 3: AI integration
    ai_ok = test_ai_integration()
    
    print(f"\n{Fore.CYAN}{'═' * 55}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}DIAGNOSTIC SUMMARY:{Style.RESET_ALL}")
    print(f"Sheets Connection: {'✅' if sheets_ok else '❌'}")
    print(f"Tracker Integration: {'✅' if tracker_ok else '❌'}")
    print(f"AI Integration: {'✅' if ai_ok else '❌'}")
    
    if not sheets_ok:
        print(f"\n{Fore.YELLOW}💡 Sheets connection issue - check credentials.json and spreadsheet name")
    elif not tracker_ok:
        print(f"\n{Fore.YELLOW}💡 Tracker issue - check finance tracker initialization")
    elif not ai_ok:
        print(f"\n{Fore.YELLOW}💡 AI integration issue - data not reaching AI service properly")
    else:
        print(f"\n{Fore.GREEN}🎉 All tests passed! The issue might be elsewhere.")


if __name__ == "__main__":
    main() 