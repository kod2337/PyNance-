"""
Setup Check Script for Finance Tracker
This script helps verify that your Google Sheets API setup is working correctly.
"""

import os
import json
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def check_credentials_file():
    """Check if credentials.json exists and is valid"""
    print(f"{Fore.CYAN}🔍 Checking credentials file...")
    
    if not os.path.exists('credentials.json'):
        print(f"{Fore.RED}❌ credentials.json not found!")
        print(f"{Fore.YELLOW}📝 Please follow these steps:")
        print("   1. Go to Google Cloud Console (https://console.cloud.google.com/)")
        print("   2. Create a new project or select existing one")
        print("   3. Enable Google Sheets API and Google Drive API")
        print("   4. Create Service Account credentials")
        print("   5. Download the JSON file and rename it to 'credentials.json'")
        print("   6. Place it in this project directory")
        return False
    
    try:
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
        
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 
                          'client_email', 'client_id', 'auth_uri', 'token_uri']
        
        missing_fields = [field for field in required_fields if field not in creds]
        
        if missing_fields:
            print(f"{Fore.RED}❌ credentials.json is missing required fields: {missing_fields}")
            return False
        
        if creds.get('type') != 'service_account':
            print(f"{Fore.RED}❌ credentials.json should be a service account key")
            return False
        
        print(f"{Fore.GREEN}✅ credentials.json looks good!")
        print(f"   📧 Service Account Email: {creds['client_email']}")
        print(f"   🏗️  Project ID: {creds['project_id']}")
        return True
        
    except json.JSONDecodeError:
        print(f"{Fore.RED}❌ credentials.json is not valid JSON")
        return False
    except Exception as e:
        print(f"{Fore.RED}❌ Error reading credentials.json: {str(e)}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print(f"\n{Fore.CYAN}🔍 Checking Python dependencies...")
    
    required_packages = [
        'gspread', 'google-auth', 'google-auth-oauthlib', 
        'pandas', 'tabulate', 'colorama'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"{Fore.GREEN}✅ {package}")
        except ImportError:
            print(f"{Fore.RED}❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n{Fore.YELLOW}📦 Missing packages detected!")
        print(f"Run this command to install them:")
        print(f"{Fore.WHITE}pip install -r requirements.txt")
        return False
    
    print(f"{Fore.GREEN}✅ All dependencies are installed!")
    return True

def test_google_sheets_connection():
    """Test connection to Google Sheets"""
    print(f"\n{Fore.CYAN}🔍 Testing Google Sheets connection...")
    
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        # Define the scope
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Load credentials
        creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
        client = gspread.authorize(creds)
        
        # Try to access the user's Google Drive
        print(f"{Fore.GREEN}✅ Successfully authenticated with Google Sheets API!")
        
        # Try to create a test spreadsheet
        test_sheet_name = "Finance Tracker Test"
        try:
            # Try to open existing test sheet first
            spreadsheet = client.open(test_sheet_name)
            print(f"{Fore.GREEN}✅ Can access existing test spreadsheet")
        except gspread.SpreadsheetNotFound:
            # Create new test spreadsheet
            spreadsheet = client.create(test_sheet_name)
            print(f"{Fore.GREEN}✅ Successfully created test spreadsheet: {test_sheet_name}")
            
            # Clean up - delete the test spreadsheet
            try:
                client.del_spreadsheet(spreadsheet.id)
                print(f"{Fore.GREEN}✅ Test spreadsheet cleaned up")
            except:
                print(f"{Fore.YELLOW}⚠️  Test spreadsheet created but couldn't delete it")
                print(f"   You can manually delete '{test_sheet_name}' from your Google Drive")
        
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Google Sheets connection failed: {str(e)}")
        print(f"\n{Fore.YELLOW}💡 Common solutions:")
        print("   1. Make sure Google Sheets API is enabled in Google Cloud Console")
        print("   2. Make sure Google Drive API is enabled in Google Cloud Console")
        print("   3. Check that your credentials.json is from a Service Account")
        print("   4. Ensure the service account has necessary permissions")
        return False

def main():
    """Main setup check function"""
    print(f"{Fore.CYAN}🛠️  Finance Tracker Setup Check")
    print(f"{Fore.CYAN}=" * 40)
    
    all_good = True
    
    # Check credentials file
    if not check_credentials_file():
        all_good = False
    
    # Check dependencies
    if not check_dependencies():
        all_good = False
    
    # Test Google Sheets connection (only if credentials are present)
    if os.path.exists('credentials.json'):
        if not test_google_sheets_connection():
            all_good = False
    else:
        all_good = False
    
    print(f"\n{Fore.CYAN}📋 Setup Check Results:")
    print("=" * 30)
    
    if all_good:
        print(f"{Fore.GREEN}🎉 Everything looks great! You're ready to use the Finance Tracker!")
        print(f"\n{Fore.CYAN}🚀 Run the application with:")
        print(f"{Fore.WHITE}python finance_tracker.py")
    else:
        print(f"{Fore.RED}❌ Some issues were found. Please fix them before running the Finance Tracker.")
        print(f"\n{Fore.YELLOW}📖 Check the README.md for detailed setup instructions.")

if __name__ == "__main__":
    main() 