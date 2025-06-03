#!/usr/bin/env python3
"""
Script to fix corrupted balance data in Google Sheets
"""

from finance_tracker_modular import FinanceTracker

def fix_balance_data():
    """Fix corrupted balance data by recalculating balances"""
    print("🔧 Fixing balance data in Google Sheets...")
    
    try:
        tracker = FinanceTracker()
        
        # Get all records
        records = tracker.sheets_service.get_all_records()
        print(f"Found {len(records)} records to check")
        
        if not records:
            print("No records found!")
            return
        
        # Calculate correct balances
        running_balance = 0.0
        fixed_records = []
        
        for i, record in enumerate(records):
            # Get amount
            amount = float(record['Amount'])
            running_balance += amount
            
            # Create corrected record data
            fixed_record = {
                'Date': record['Date'],
                'Description': record['Description'], 
                'Category': record['Category'],
                'Amount': amount,
                'Type': record['Type'],
                'Balance': running_balance
            }
            
            fixed_records.append(fixed_record)
            print(f"Record {i+1}: Amount={amount}, New Balance={running_balance}")
        
        # Clear the worksheet and rewrite with corrected data
        worksheet = tracker.sheets_service.transactions_worksheet
        
        # Clear all data except headers
        worksheet.clear()
        
        # Add headers
        headers = ["Date", "Description", "Category", "Amount", "Type", "Balance"]
        worksheet.append_row(headers)
        
        # Add corrected records
        for record in fixed_records:
            row = [
                record['Date'],
                record['Description'],
                record['Category'],
                record['Amount'],
                record['Type'],
                record['Balance']
            ]
            worksheet.append_row(row)
        
        print(f"✅ Fixed {len(fixed_records)} records!")
        print(f"💰 Final balance: ${running_balance:.2f}")
        
        # Verify the fix
        print("\n🔍 Verifying fix...")
        new_records = tracker.sheets_service.get_all_records()
        
        for i, record in enumerate(new_records[:3]):
            print(f"Verified Record {i+1}: Balance = {record['Balance']}")
        
        print("✅ Balance data fix completed!")
        
    except Exception as e:
        print(f"❌ Error fixing balance data: {e}")

if __name__ == "__main__":
    fix_balance_data() 