import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime, date
import json
import os
from tabulate import tabulate
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

class FinanceTracker:
    def __init__(self, credentials_file='credentials.json', spreadsheet_name='Finance Tracker Automated', user_email='kodibompat2@gmail.com'):
        self.credentials_file = credentials_file
        self.spreadsheet_name = spreadsheet_name
        self.user_email = user_email
        self.client = None
        self.worksheet = None
        self.spreadsheet = None
        self.transactions = []
        
        # Initialize Google Sheets connection
        self.connect_to_sheets()
        
    def connect_to_sheets(self):
        """Connect to Google Sheets using service account credentials"""
        try:
            if not os.path.exists(self.credentials_file):
                print(f"{Fore.RED}❌ Credentials file '{self.credentials_file}' not found!")
                print(f"{Fore.YELLOW}Please follow the setup instructions in README.md")
                return False
                
            # Define the scope
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Load credentials
            creds = Credentials.from_service_account_file(self.credentials_file, scopes=scope)
            self.client = gspread.authorize(creds)
            
            # Try to open existing spreadsheet or create new one
            try:
                self.spreadsheet = self.client.open(self.spreadsheet_name)
                print(f"{Fore.GREEN}✅ Connected to existing spreadsheet: {self.spreadsheet_name}")
            except gspread.SpreadsheetNotFound:
                self.spreadsheet = self.client.create(self.spreadsheet_name)
                print(f"{Fore.GREEN}✅ Created new spreadsheet: {self.spreadsheet_name}")
                
                # Share the spreadsheet with the user's personal email
                try:
                    self.spreadsheet.share(self.user_email, perm_type='user', role='writer')
                    print(f"{Fore.GREEN}✅ Shared spreadsheet with {self.user_email}")
                    print(f"{Fore.CYAN}📧 Check your Google Drive - the spreadsheet should now be visible!")
                except Exception as e:
                    print(f"{Fore.YELLOW}⚠️  Created spreadsheet but couldn't share: {str(e)}")
                    print(f"{Fore.CYAN}💡 You can manually share it later if needed")
                
            # Get or create the main worksheet
            try:
                self.worksheet = self.spreadsheet.worksheet("Transactions")
            except gspread.WorksheetNotFound:
                self.worksheet = self.spreadsheet.add_worksheet(title="Transactions", rows="1000", cols="6")
                # Add headers
                headers = ["Date", "Description", "Category", "Amount", "Type", "Balance"]
                self.worksheet.append_row(headers)
                print(f"{Fore.GREEN}✅ Created Transactions worksheet with headers")
                
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error connecting to Google Sheets: {str(e)}")
            return False
    
    def add_transaction(self, description, category, amount, transaction_type):
        """Add a new transaction"""
        try:
            # Create transaction data
            transaction_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Calculate new balance
            current_balance = self.get_current_balance()
            if transaction_type.lower() == 'expense':
                new_balance = current_balance - float(amount)
                amount = -float(amount)  # Make expenses negative
            else:
                new_balance = current_balance + float(amount)
                amount = float(amount)
            
            # Create transaction row
            transaction_row = [
                transaction_date,
                description,
                category,
                amount,
                transaction_type.capitalize(),
                new_balance
            ]
            
            # Add to Google Sheets
            if self.worksheet:
                self.worksheet.append_row(transaction_row)
                print(f"{Fore.GREEN}✅ Transaction added successfully!")
                print(f"   💰 New Balance: ${new_balance:.2f}")
            else:
                print(f"{Fore.YELLOW}⚠️  Google Sheets not connected. Transaction saved locally only.")
                
            # Add to local list
            self.transactions.append({
                'date': transaction_date,
                'description': description,
                'category': category,
                'amount': amount,
                'type': transaction_type,
                'balance': new_balance
            })
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error adding transaction: {str(e)}")
            return False
    
    def get_current_balance(self):
        """Get the current balance from the last transaction"""
        try:
            if self.worksheet:
                # Get all values from the Balance column (column F)
                balance_column = self.worksheet.col_values(6)  # Column F (Balance)
                if len(balance_column) > 1:  # Skip header
                    last_balance = balance_column[-1]
                    return float(last_balance) if last_balance else 0.0
            return 0.0
        except:
            return 0.0
    
    def view_transactions(self, limit=10):
        """View recent transactions"""
        try:
            if self.worksheet:
                # Get all records from the worksheet
                records = self.worksheet.get_all_records()
                
                if not records:
                    print(f"{Fore.YELLOW}📝 No transactions found.")
                    return
                
                # Get the most recent transactions
                recent_records = records[-limit:] if len(records) > limit else records
                recent_records.reverse()  # Show most recent first
                
                # Create table for display
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
                        record['Description'][:30] + "..." if len(record['Description']) > 30 else record['Description'],
                        record['Category'],
                        amount_str,
                        record['Type'],
                        f"${balance:.2f}"
                    ])
                
                print(f"\n{Fore.CYAN}📊 Recent Transactions (Last {len(recent_records)}):")
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
                
            else:
                print(f"{Fore.YELLOW}⚠️  Not connected to Google Sheets.")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error viewing transactions: {str(e)}")
    
    def get_category_summary(self):
        """Get spending summary by category"""
        try:
            if self.worksheet:
                records = self.worksheet.get_all_records()
                
                if not records:
                    print(f"{Fore.YELLOW}📝 No transactions found.")
                    return
                
                # Calculate category totals
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
                
                # Display summary
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
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error generating category summary: {str(e)}")

    def create_charts(self):
        """Create charts in the spreadsheet"""
        try:
            if not self.worksheet:
                print(f"{Fore.RED}❌ Not connected to spreadsheet")
                return False
                
            records = self.worksheet.get_all_records()
            if not records:
                print(f"{Fore.YELLOW}📝 No data available for charts")
                return False
            
            print(f"{Fore.CYAN}📊 Creating charts...")
            
            # Create or get Charts worksheet
            try:
                charts_worksheet = self.spreadsheet.worksheet("Charts & Analysis")
            except gspread.WorksheetNotFound:
                charts_worksheet = self.spreadsheet.add_worksheet(title="Charts & Analysis", rows="50", cols="10")
            
            # Prepare data for charts
            self._create_category_summary_chart(charts_worksheet, records)
            self._create_balance_trend_chart(charts_worksheet, records)
            self._create_monthly_summary_chart(charts_worksheet, records)
            
            print(f"{Fore.GREEN}✅ Charts created successfully!")
            print(f"{Fore.CYAN}📈 Check the 'Charts & Analysis' tab in your spreadsheet")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error creating charts: {str(e)}")
            return False
    
    def _create_category_summary_chart(self, worksheet, records):
        """Create pie chart for expense categories"""
        try:
            # Calculate category expenses
            category_expenses = {}
            for record in records:
                if float(record['Amount']) < 0:  # Only expenses
                    category = record['Category']
                    amount = abs(float(record['Amount']))
                    category_expenses[category] = category_expenses.get(category, 0) + amount
            
            if not category_expenses:
                return
            
            # Clear existing data and add new data
            worksheet.clear()
            worksheet.update('A1', 'Category Expense Analysis')
            worksheet.update('A3', 'Category')
            worksheet.update('B3', 'Amount')
            
            row = 4
            for category, amount in category_expenses.items():
                worksheet.update(f'A{row}', category)
                worksheet.update(f'B{row}', amount)
                row += 1
                
            # Create pie chart using Google Sheets API
            requests = [{
                'addChart': {
                    'chart': {
                        'spec': {
                            'title': 'Expenses by Category',
                            'pieChart': {
                                'legendPosition': 'RIGHT_LEGEND',
                                'domain': {
                                    'sourceRange': {
                                        'sources': [{
                                            'sheetId': worksheet.id,
                                            'startRowIndex': 3,
                                            'endRowIndex': row,
                                            'startColumnIndex': 0,
                                            'endColumnIndex': 1
                                        }]
                                    }
                                },
                                'series': {
                                    'sourceRange': {
                                        'sources': [{
                                            'sheetId': worksheet.id,
                                            'startRowIndex': 3,
                                            'endRowIndex': row,
                                            'startColumnIndex': 1,
                                            'endColumnIndex': 2
                                        }]
                                    }
                                }
                            }
                        },
                        'position': {
                            'overlayPosition': {
                                'anchorCell': {
                                    'sheetId': worksheet.id,
                                    'rowIndex': 2,
                                    'columnIndex': 3
                                }
                            }
                        }
                    }
                }
            }]
            
            self.spreadsheet.batch_update({'requests': requests})
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  Could not create category chart: {str(e)}")
    
    def _create_balance_trend_chart(self, worksheet, records):
        """Create line chart for balance over time"""
        try:
            # Prepare balance trend data (last 30 entries or all if less)
            balance_data = []
            for i, record in enumerate(records[-30:], 1):
                date_str = record['Date'][:10]  # Just the date part
                balance = float(record['Balance'])
                balance_data.append([date_str, balance])
            
            if len(balance_data) < 2:
                return
                
            # Add balance trend data starting from row 15
            start_row = 15
            worksheet.update(f'A{start_row}', 'Balance Trend Analysis')
            worksheet.update(f'A{start_row + 2}', 'Date')
            worksheet.update(f'B{start_row + 2}', 'Balance')
            
            for i, (date_str, balance) in enumerate(balance_data):
                row = start_row + 3 + i
                worksheet.update(f'A{row}', date_str)
                worksheet.update(f'B{row}', balance)
            
            end_row = start_row + 3 + len(balance_data)
            
            # Create line chart
            requests = [{
                'addChart': {
                    'chart': {
                        'spec': {
                            'title': 'Balance Over Time',
                            'basicChart': {
                                'chartType': 'LINE',
                                'legendPosition': 'RIGHT_LEGEND',
                                'axis': [
                                    {
                                        'position': 'BOTTOM_AXIS',
                                        'title': 'Date'
                                    },
                                    {
                                        'position': 'LEFT_AXIS',
                                        'title': 'Balance ($)'
                                    }
                                ],
                                'domains': [{
                                    'domain': {
                                        'sourceRange': {
                                            'sources': [{
                                                'sheetId': worksheet.id,
                                                'startRowIndex': start_row + 2,
                                                'endRowIndex': end_row,
                                                'startColumnIndex': 0,
                                                'endColumnIndex': 1
                                            }]
                                        }
                                    }
                                }],
                                'series': [{
                                    'series': {
                                        'sourceRange': {
                                            'sources': [{
                                                'sheetId': worksheet.id,
                                                'startRowIndex': start_row + 2,
                                                'endRowIndex': end_row,
                                                'startColumnIndex': 1,
                                                'endColumnIndex': 2
                                            }]
                                        }
                                    },
                                    'targetAxis': 'LEFT_AXIS'
                                }]
                            }
                        },
                        'position': {
                            'overlayPosition': {
                                'anchorCell': {
                                    'sheetId': worksheet.id,
                                    'rowIndex': start_row + 1,
                                    'columnIndex': 3
                                }
                            }
                        }
                    }
                }
            }]
            
            self.spreadsheet.batch_update({'requests': requests})
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  Could not create balance trend chart: {str(e)}")
    
    def _create_monthly_summary_chart(self, worksheet, records):
        """Create bar chart for monthly income vs expenses"""
        try:
            # Calculate monthly data
            monthly_data = {}
            for record in records:
                date_str = record['Date'][:7]  # YYYY-MM format
                amount = float(record['Amount'])
                
                if date_str not in monthly_data:
                    monthly_data[date_str] = {'income': 0, 'expenses': 0}
                
                if amount < 0:
                    monthly_data[date_str]['expenses'] += abs(amount)
                else:
                    monthly_data[date_str]['income'] += amount
            
            if not monthly_data:
                return
                
            # Add monthly summary starting from row 30
            start_row = 30
            worksheet.update(f'A{start_row}', 'Monthly Income vs Expenses')
            worksheet.update(f'A{start_row + 2}', 'Month')
            worksheet.update(f'B{start_row + 2}', 'Income')
            worksheet.update(f'C{start_row + 2}', 'Expenses')
            
            row = start_row + 3
            for month, data in sorted(monthly_data.items()):
                worksheet.update(f'A{row}', month)
                worksheet.update(f'B{row}', data['income'])
                worksheet.update(f'C{row}', data['expenses'])
                row += 1
            
            # Create column chart
            requests = [{
                'addChart': {
                    'chart': {
                        'spec': {
                            'title': 'Monthly Income vs Expenses',
                            'basicChart': {
                                'chartType': 'COLUMN',
                                'legendPosition': 'RIGHT_LEGEND',
                                'axis': [
                                    {
                                        'position': 'BOTTOM_AXIS',
                                        'title': 'Month'
                                    },
                                    {
                                        'position': 'LEFT_AXIS',
                                        'title': 'Amount ($)'
                                    }
                                ],
                                'domains': [{
                                    'domain': {
                                        'sourceRange': {
                                            'sources': [{
                                                'sheetId': worksheet.id,
                                                'startRowIndex': start_row + 2,
                                                'endRowIndex': row,
                                                'startColumnIndex': 0,
                                                'endColumnIndex': 1
                                            }]
                                        }
                                    }
                                }],
                                'series': [
                                    {
                                        'series': {
                                            'sourceRange': {
                                                'sources': [{
                                                    'sheetId': worksheet.id,
                                                    'startRowIndex': start_row + 2,
                                                    'endRowIndex': row,
                                                    'startColumnIndex': 1,
                                                    'endColumnIndex': 2
                                                }]
                                            }
                                        },
                                        'targetAxis': 'LEFT_AXIS'
                                    },
                                    {
                                        'series': {
                                            'sourceRange': {
                                                'sources': [{
                                                    'sheetId': worksheet.id,
                                                    'startRowIndex': start_row + 2,
                                                    'endRowIndex': row,
                                                    'startColumnIndex': 2,
                                                    'endColumnIndex': 3
                                                }]
                                            }
                                        },
                                        'targetAxis': 'LEFT_AXIS'
                                    }
                                ]
                            }
                        },
                        'position': {
                            'overlayPosition': {
                                'anchorCell': {
                                    'sheetId': worksheet.id,
                                    'rowIndex': start_row + 1,
                                    'columnIndex': 4
                                }
                            }
                        }
                    }
                }
            }]
            
            self.spreadsheet.batch_update({'requests': requests})
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  Could not create monthly summary chart: {str(e)}")

def main():
    """Main application loop"""
    print(f"{Fore.CYAN}💰 Personal Finance Tracker with Charts")
    print(f"{Fore.CYAN}=" * 45)
    
    # Initialize tracker
    tracker = FinanceTracker()
    
    while True:
        print(f"\n{Fore.YELLOW}Choose an option:")
        print("1. 💸 Add Expense")
        print("2. 💰 Add Income")
        print("3. 📊 View Recent Transactions")
        print("4. 📈 Category Summary")
        print("5. 💳 Check Balance")
        print("6. 📊 Create/Update Charts")
        print("7. 🚪 Exit")
        
        choice = input(f"\n{Fore.WHITE}Enter your choice (1-7): ").strip()
        
        if choice == '1':
            # Add Expense
            print(f"\n{Fore.RED}💸 Adding Expense")
            description = input("Description: ").strip()
            category = input("Category (e.g., Food, Transport, Bills): ").strip()
            try:
                amount = float(input("Amount: $"))
                if amount <= 0:
                    print(f"{Fore.RED}❌ Amount must be positive!")
                    continue
                tracker.add_transaction(description, category, amount, "Expense")
            except ValueError:
                print(f"{Fore.RED}❌ Invalid amount entered!")
                
        elif choice == '2':
            # Add Income
            print(f"\n{Fore.GREEN}💰 Adding Income")
            description = input("Description: ").strip()
            category = input("Category (e.g., Salary, Freelance, Investment): ").strip()
            try:
                amount = float(input("Amount: $"))
                if amount <= 0:
                    print(f"{Fore.RED}❌ Amount must be positive!")
                    continue
                tracker.add_transaction(description, category, amount, "Income")
            except ValueError:
                print(f"{Fore.RED}❌ Invalid amount entered!")
                
        elif choice == '3':
            # View Transactions
            try:
                limit = int(input(f"How many recent transactions to show? (default 10): ") or "10")
                tracker.view_transactions(limit)
            except ValueError:
                tracker.view_transactions(10)
                
        elif choice == '4':
            # Category Summary
            tracker.get_category_summary()
            
        elif choice == '5':
            # Check Balance
            balance = tracker.get_current_balance()
            balance_color = Fore.GREEN if balance >= 0 else Fore.RED
            print(f"\n{Fore.CYAN}💳 Current Balance: {balance_color}${balance:.2f}")
            
        elif choice == '6':
            # Create Charts
            tracker.create_charts()
            
        elif choice == '7':
            # Exit
            print(f"{Fore.GREEN}👋 Thank you for using Finance Tracker!")
            break
            
        else:
            print(f"{Fore.RED}❌ Invalid choice! Please enter 1-7.")

if __name__ == "__main__":
    main() 