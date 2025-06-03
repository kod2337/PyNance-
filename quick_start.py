"""
Quick Start Script for Finance Tracker
This script will install dependencies and check your setup automatically.
"""

import subprocess
import sys
import os
from colorama import Fore, Style, init

try:
    # Initialize colorama
    init(autoreset=True)
except ImportError:
    # If colorama isn't installed yet, we'll install it first
    pass

def install_dependencies():
    """Install required dependencies"""
    print("🔧 Installing dependencies...")
    
    try:
        # Install dependencies
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True, check=True)
        
        print(f"{Fore.GREEN}✅ Dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}❌ Error installing dependencies:")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print(f"{Fore.RED}❌ requirements.txt not found!")
        return False

def run_setup_check():
    """Run the setup check script"""
    print(f"\n{Fore.CYAN}🔍 Running setup check...")
    
    try:
        # Run setup check
        result = subprocess.run([sys.executable, "setup_check.py"], check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"{Fore.RED}❌ Setup check failed")
        return False
    except FileNotFoundError:
        print(f"{Fore.RED}❌ setup_check.py not found!")
        return False

def main():
    """Main quick start function"""
    print(f"🚀 Finance Tracker Quick Start")
    print("=" * 40)
    
    # Check if requirements.txt exists
    if not os.path.exists('requirements.txt'):
        print(f"❌ requirements.txt not found!")
        print("Please make sure you're in the correct directory.")
        return
    
    # Install dependencies first
    print("Step 1: Installing Python dependencies...")
    if not install_dependencies():
        print(f"\n❌ Failed to install dependencies. Please check the error above.")
        return
    
    # Now we can import colorama since it should be installed
    try:
        from colorama import Fore, Style, init
        init(autoreset=True)
    except ImportError:
        pass
    
    print(f"\n{Fore.CYAN}Step 2: Checking setup...")
    
    # Run setup check
    if run_setup_check():
        print(f"\n{Fore.GREEN}🎉 Quick start completed!")
    else:
        print(f"\n{Fore.YELLOW}⚠️  Setup check found some issues.")
        print("Please review the output above and fix any problems.")
    
    print(f"\n{Fore.CYAN}📖 Next Steps:")
    print("1. If you haven't already, create your Google Sheets API credentials")
    print("2. Save the credentials as 'credentials.json' in this directory")
    print("3. Run 'python setup_check.py' to verify everything is working")
    print("4. Run 'python finance_tracker.py' to start using the app!")

if __name__ == "__main__":
    main() 