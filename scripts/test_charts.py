#!/usr/bin/env python3
"""
Test chart creation after balance fix
"""

from finance_tracker_modular import FinanceTracker

def test_charts():
    print("🧪 Testing chart creation...")
    
    try:
        tracker = FinanceTracker()
        success = tracker.create_charts()
        
        if success:
            print("✅ Charts created successfully!")
        else:
            print("❌ Chart creation failed")
            
        return success
        
    except Exception as e:
        print(f"❌ Error testing charts: {e}")
        return False

if __name__ == "__main__":
    test_charts() 