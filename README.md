# 💰 Finance Tracker System

A comprehensive personal finance tracking application with Google Sheets integration, featuring automated categorization, visual charts, and an intuitive command-line interface.

## 🌟 Features

- **Transaction Management**: Add income and expenses with automatic categorization
- **Google Sheets Integration**: Automatic syncing with Google Sheets for data persistence
- **Visual Analytics**: Automated chart generation and financial analysis
- **Category Tracking**: Smart categorization of transactions
- **Balance Monitoring**: Real-time balance tracking and trend analysis
- **User-Friendly Interface**: Clean command-line interface with colored output

## 📋 Prerequisites

Before setting up the Finance Tracker, ensure you have:

- **Python 3.8+** installed on your system
- **Google Account** for Google Sheets integration
- **Internet connection** for Google Sheets API access

## 🚀 Quick Setup Guide

### Step 1: Clone/Download the Project

```bash
# If using Git
git clone <your-repository-url>
cd Financetracker

# Or download and extract the ZIP file
```

### Step 2: Install Python Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

**Required packages:**
- `gspread==5.12.0` - Google Sheets API wrapper
- `google-auth==2.23.4` - Google authentication
- `google-auth-oauthlib==1.1.0` - OAuth for Google APIs
- `pandas==2.1.3` - Data manipulation
- `tabulate==0.9.0` - Table formatting
- `colorama==0.4.6` - Colored terminal output

### Step 3: Set Up Google Sheets API

#### 3.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Create Project"** or select an existing project
3. Name your project (e.g., "Finance Tracker")

#### 3.2 Enable Required APIs

1. In the Google Cloud Console, go to **"APIs & Services" > "Library"**
2. Search for and enable:
   - **Google Sheets API**
   - **Google Drive API**

#### 3.3 Create Service Account

1. Go to **"APIs & Services" > "Credentials"**
2. Click **"+ CREATE CREDENTIALS" > "Service Account"**
3. Fill in the service account details:
   - **Name**: Finance Tracker Service
   - **Description**: Service account for Finance Tracker app
4. Click **"CREATE AND CONTINUE"**
5. Skip the optional steps and click **"DONE"**

#### 3.4 Generate and Download Credentials

1. In the **"Credentials"** page, find your service account
2. Click on the service account email
3. Go to the **"Keys"** tab
4. Click **"ADD KEY" > "Create new key"**
5. Choose **"JSON"** format
6. Click **"CREATE"** - this downloads the JSON file
7. **Rename** the downloaded file to `credentials.json`
8. **Move** `credentials.json` to your project root directory

### Step 4: Verify Setup

Run the setup check script to ensure everything is configured correctly:

```bash
python setup_check.py
```

This script will:
- ✅ Check if `credentials.json` exists and is valid
- ✅ Verify all Python dependencies are installed
- ✅ Test Google Sheets API connection
- ✅ Create a test spreadsheet (and clean it up)

## 🎯 Running the Application

### Option 1: Main Application (Recommended)
```bash
python main.py
```

### Option 2: Direct Run
```bash
python finance_tracker.py
```

### Option 3: GUI Version (If Available)
```bash
python gui_finance_tracker.py
```

### Option 4: Quick Start Demo
```bash
python quick_start.py
```

## 🛠️ Configuration

### Default Settings

The system uses these default settings (configurable in `config/settings.py`):

- **Default Spreadsheet Name**: "Finance Tracker Automated"
- **Default User Email**: kodibompat2@gmail.com
- **Transaction Categories**: Auto-detected based on descriptions
- **Chart Update Frequency**: Manual or on-demand

### Customizing Settings

Edit `config/settings.py` to customize:

```python
# Your settings
DEFAULT_SPREADSHEET_NAME = 'Your Finance Tracker'
DEFAULT_USER_EMAIL = 'your-email@gmail.com'
```

## 📊 How to Use

### 1. First Run
- The app will create a new Google Spreadsheet
- Two worksheets will be created:
  - **"Transactions"**: Stores all your financial data
  - **"Charts & Analysis"**: Contains visual analytics

### 2. Adding Transactions

**Adding Expenses:**
```
Select option 1: Add Expense
Enter amount: 50.00
Enter description: Grocery shopping
Category will be auto-detected (Food/Groceries)
```

**Adding Income:**
```
Select option 2: Add Income
Enter amount: 2500.00
Enter description: Salary payment
Category will be auto-detected (Income)
```

### 3. Viewing Data
- **Option 3**: View recent transactions
- **Option 4**: Category-wise summary
- **Option 5**: Check current balance
- **Option 6**: Generate/update charts

## 🔧 Troubleshooting

### Common Issues and Solutions

#### ❌ "credentials.json not found"
**Solution:** Make sure you've downloaded and renamed your Google service account key file to `credentials.json` and placed it in the project root.

#### ❌ "Permission denied" or "Insufficient permissions"
**Solutions:**
1. Ensure Google Sheets API and Google Drive API are enabled
2. Check that your service account has the correct permissions
3. Try recreating the service account and downloading new credentials

#### ❌ "Module not found" errors
**Solution:** Install dependencies using:
```bash
pip install -r requirements.txt
```

#### ❌ "Spreadsheet not found"
**Solution:** The app will automatically create a new spreadsheet on first run. If issues persist, check your Google Drive permissions.

#### ❌ "SSL Certificate errors"
**Solutions:**
1. Update your Python installation
2. Try: `pip install --upgrade certifi`
3. Check your internet connection and firewall settings

### Getting Help

1. **Run the setup check**: `python setup_check.py`
2. **Check the error logs** in the terminal output
3. **Verify your Google Cloud Console** settings
4. **Ensure all APIs are enabled** and credentials are correct

## 📁 Project Structure

```
Financetracker/
├── main.py                      # Main entry point
├── finance_tracker.py           # Core application logic
├── finance_tracker_modular.py   # Modular version
├── gui_finance_tracker.py       # GUI version
├── quick_start.py               # Quick demo
├── setup_check.py               # Setup verification
├── requirements.txt             # Python dependencies
├── credentials.json             # Google API credentials (you create this)
├── config/
│   ├── settings.py              # Configuration settings
│   └── __init__.py
├── services/
│   ├── chart_service.py         # Chart generation
│   ├── sheets_service.py        # Google Sheets integration
│   └── __init__.py
├── ui/
│   └── menu.py                  # User interface
├── models/
│   └── __init__.py
└── .gitignore                   # Git ignore rules
```

## 🔒 Security Notes

- **Never commit `credentials.json`** to version control
- Your financial data is stored in your personal Google Sheets
- The app only accesses spreadsheets you own or have been granted access to
- All communication with Google APIs is encrypted (HTTPS)

## 🚀 Getting Started Checklist

- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Google Cloud project created
- [ ] Google Sheets API and Google Drive API enabled
- [ ] Service account created and JSON key downloaded
- [ ] `credentials.json` file in project root
- [ ] Setup check passed (`python setup_check.py`)
- [ ] Application runs successfully (`python main.py`)

## 📈 Next Steps

Once your Finance Tracker is set up:

1. **Add your first transactions** to see the system in action
2. **Explore the generated charts** in your Google Sheets
3. **Customize categories** and settings as needed
4. **Set up regular usage** for comprehensive financial tracking

## 🤝 Support

If you encounter any issues:

1. Run `python setup_check.py` to diagnose problems
2. Check this README for common solutions
3. Verify your Google Cloud Console configuration
4. Ensure all required APIs are enabled

---

**Happy tracking! 💰📊** 