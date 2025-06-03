#!/usr/bin/env python3
"""
Finance Tracker - Main Entry Point
Clean, modular personal finance tracker with Google Sheets integration
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from finance_tracker_modular import FinanceTracker
from ui.menu import FinanceTrackerUI


def main():
    """Main application entry point"""
    try:
        # Initialize the Finance Tracker
        tracker = FinanceTracker()
        
        # Initialize and run the UI
        ui = FinanceTrackerUI(tracker)
        ui.run()
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Thanks for using Finance Tracker!")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {str(e)}")
        print("Please check your setup and try again.")


if __name__ == "__main__":
    main() 