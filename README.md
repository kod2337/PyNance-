# 🤖 AI-Powered Finance Tracker 💰

A comprehensive personal finance tracker enhanced with Google Gemini AI for smart transaction management, automated categorization, and intelligent financial insights.

## ✨ Features

### 📊 Core Features
- **Transaction Management**: Add, view, and categorize financial transactions
- **Google Sheets Integration**: Automatic synchronization with Google Sheets
- **Interactive Charts**: Visual spending analysis and balance trends
- **Multi-Currency Support**: Track finances in different currencies
- **Category Analytics**: Detailed spending breakdown by category

### 🤖 AI-Powered Features
- **Smart Transaction Categorization**: AI automatically suggests categories based on transaction descriptions
- **Natural Language Processing**: Add transactions using plain English
- **Financial Insights**: AI-generated personalized spending analysis and recommendations
- **Intelligent Reporting**: AI-powered expense reports with actionable insights
- **Pattern Recognition**: Learn from your spending habits for better categorization

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google account for Sheets integration
- Google Gemini API key (for AI features)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd PythonProj/Financetracker
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
# Copy the example environment file
cp env.example .env

# Edit .env with your configuration
# Add your GEMINI_API_KEY for AI features
```

4. **Set up Google Sheets API** (See detailed setup below)

5. **Run the application**
```bash
python main.py
```

## 🔐 Setup Instructions

### Google Sheets API Setup

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select existing one

2. **Enable APIs**
   - Enable Google Sheets API
   - Enable Google Drive API

3. **Create Service Account**
   - Go to "Credentials" → "Create Credentials" → "Service Account"
   - Download the JSON credentials file
   - Rename it to `credentials.json` and place in project root

4. **Share Spreadsheet**
   - Create or open your Google Sheet
   - Share it with the service account email (found in credentials.json)
   - Give "Editor" permissions

### 🤖 AI Features Setup

1. **Get Gemini API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key

2. **Set Environment Variable**
```bash
# Windows (PowerShell)
$env:GEMINI_API_KEY = "your_api_key_here"

# Windows (CMD)
set GEMINI_API_KEY=your_api_key_here

# Linux/Mac
export GEMINI_API_KEY="your_api_key_here"

# Or add to .env file
echo "GEMINI_API_KEY=your_api_key_here" >> .env
```

3. **Restart the application** to enable AI features

## 🎯 Usage Guide

### Basic Transaction Management

```
📊 MAIN MENU
1. Add Transaction (Manual)     - Traditional transaction entry
2. View Recent Transactions     - Display recent activity
3. Category Summary            - Spending breakdown by category
4. Create Charts              - Generate visual analytics
```

### 🤖 AI-Powered Features

#### Smart Categorization
```
5. Add Transaction (AI Categories)
```
- Enter transaction description and amount
- AI automatically suggests the most appropriate category
- Based on description analysis and your spending patterns

#### Natural Language Transactions
```
6. Natural Language Transaction
```
**Examples:**
- "I spent $25 on groceries at Walmart yesterday"
- "Got paid $500 for freelance work"
- "Bought coffee for $4.50 this morning"
- "Received $1000 salary today"

#### Financial Insights
```
7. Generate AI Insights
```
Get personalized analysis including:
- **Spending Patterns**: Key trends in your expenses
- **Budget Recommendations**: AI-suggested spending limits
- **Savings Tips**: Personalized advice for reducing expenses
- **Anomaly Detection**: Unusual spending patterns
- **Trend Analysis**: Monthly spending trajectory

#### Intelligent Reports
```
8. AI Financial Report
```
Choose from:
- **Weekly Report**: Last 7 days analysis
- **Monthly Report**: Last 30 days comprehensive review
- **Yearly Report**: Annual financial summary

### Example AI Interactions

#### Natural Language Examples
```
Input: "Spent 45 dollars on gas at Shell station"
AI Output:
✅ Parsed transaction:
   📝 Description: Gas at Shell station
   💵 Amount: $45.00
   📂 Category: Transportation
   📅 Date: 2024-01-16
   🏷️  Type: Expense
```

#### AI Insights Example
```
🤖 AI FINANCIAL INSIGHTS

📊 SPENDING PATTERNS:
You tend to spend more on weekends, with dining out being your highest weekend expense category.

💡 BUDGET RECOMMENDATIONS:
Consider setting a $300 monthly limit for dining out. You've exceeded this by $75 in the past month.

💰 SAVINGS TIPS:
You could save approximately $50/month by meal prepping instead of ordering takeout 3x per week.

🚨 ANOMALIES DETECTED:
Unusual entertainment spending spike (+150%) in the last week. Review streaming subscriptions.

📈 MONTHLY TREND:
Spending has increased by 12% compared to last month, primarily in the shopping category.
```

## 📁 Project Structure

```
Finance-Tracker/
├── main.py                     # Main CLI application
├── gui_finance_tracker.py      # GUI application
├── requirements.txt            # Project dependencies
├── README.md                   # Documentation
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
│
├── core/                      # Core business logic
│   └── finance_tracker_modular.py
│
├── models/                    # Data models
│   └── transaction.py
│
├── services/                  # Service layer
│   ├── sheets_service.py      # Google Sheets integration
│   ├── chart_service.py       # Chart creation
│   ├── currency_service.py    # Currency handling
│   ├── settings_service.py    # Settings management
│   └── ai_service.py          # AI features (Gemini)
│
├── config/                    # Configuration
│   └── settings.py
│
├── ui/                        # UI components
│   └── components.py
│
├── scripts/                   # Utility scripts
│   ├── setup_check.py         # Environment setup check
│   ├── fix_balance_data.py    # Data repair utilities
│   └── quick_start.py         # Quick setup script
│
├── tests/                     # Test scripts
│   ├── test_gemini_models.py  # AI/Gemini testing
│   └── test_sheets_data.py    # Data integration testing
│
├── examples/                  # Example scripts
│   └── demo_ai_features.py    # AI features demonstration
│
├── docs/                      # Documentation
├── logs/                      # Application logs
└── data/                      # Local data storage
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `GEMINI_API_KEY` | Google Gemini AI API key | For AI features | `AIzaSy...` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to Google credentials | Yes | `credentials.json` |
| `SPREADSHEET_NAME` | Google Sheets name | No | `Finance Tracker` |
| `USER_EMAIL` | Your email for sharing | No | `user@gmail.com` |

### AI Service Configuration

The AI service automatically handles:
- **Fallback Behavior**: Works without AI when API key is missing
- **Error Handling**: Graceful degradation when AI services fail
- **Rate Limiting**: Respects API usage limits
- **Caching**: Reduces redundant API calls

## 🎨 AI Features Deep Dive

### Smart Categorization Algorithm

1. **Context Analysis**: Analyzes transaction description for keywords
2. **Pattern Learning**: Uses historical user categorization patterns
3. **Semantic Understanding**: Leverages Gemini's natural language processing
4. **Category Mapping**: Maps AI suggestions to predefined categories
5. **Fallback Logic**: Uses rule-based categorization when AI is unavailable

### Natural Language Processing

The system can parse complex transaction descriptions:
```
"I spent twenty-five dollars on groceries at Walmart yesterday"
↓
{
  "description": "Groceries at Walmart",
  "amount": -25.0,
  "category": "Groceries",
  "date": "2024-01-15",
  "type": "Expense"
}
```

### Financial Insights Engine

AI analyzes your data to provide:
- **Spending Pattern Recognition**: Identifies trends and habits
- **Anomaly Detection**: Flags unusual transactions
- **Predictive Budgeting**: Suggests realistic budget limits
- **Personalized Recommendations**: Tailored advice based on your data
- **Goal-Oriented Insights**: Helps achieve financial objectives

## 🚀 Advanced Usage

### Batch Processing

For bulk transaction import, you can extend the AI service:
```python
from services.ai_service import get_ai_service

ai_service = get_ai_service()
transactions = [
    "Spent $50 on groceries",
    "Got paid $1000 salary",
    "Coffee $4.50"
]

for transaction in transactions:
    parsed = ai_service.parse_natural_language_transaction(transaction)
    # Process parsed transaction
```

### Custom Categories

Modify the AI service categories in `services/ai_service.py`:
```python
self.categories = {
    'custom_category': ['Custom Category', 'Sub Category'],
    # Add your custom categories
}
```

## 🔍 Troubleshooting

### Common Issues

**AI Features Not Working**
- Check if `GEMINI_API_KEY` is set correctly
- Verify API key has proper permissions
- Check internet connection

**Google Sheets Connection Failed**
- Ensure `credentials.json` is in the project root
- Verify service account has access to your spreadsheet
- Check if APIs are enabled in Google Cloud Console

**Import Errors**
- Run `pip install -r requirements.txt`
- Check Python version (3.8+ required)
- Verify virtual environment is activated

### Debug Mode

Enable debug logging by setting:
```bash
export LOG_LEVEL=DEBUG
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure AI features have fallback behavior
5. Submit a pull request

### Adding New AI Features

When adding AI features:
1. Always implement fallback behavior
2. Add proper error handling
3. Include user feedback for AI actions
4. Test with and without API access
5. Document the feature in README

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google Gemini AI**: For powerful natural language processing
- **Google Sheets API**: For seamless data synchronization
- **Colorama**: For beautiful terminal output
- **Tabulate**: For formatted table display

## 🔮 Future Enhancements

- **Receipt OCR**: AI-powered receipt scanning
- **Investment Tracking**: Portfolio management with AI insights
- **Bill Prediction**: AI-powered expense forecasting
- **Voice Commands**: Speech-to-transaction conversion
- **Smart Alerts**: AI-driven spending notifications
- **Financial Goals**: AI-assisted goal setting and tracking

## 🧪 Testing

### Test AI Features
```bash
# Test Gemini API and model availability
python tests/test_gemini_models.py

# Test Google Sheets data integration
python tests/test_sheets_data.py

# Demo all AI features
python examples/demo_ai_features.py
```

### Test Basic Features
```bash
# Check environment setup
python scripts/setup_check.py

# Quick start with sample data
python scripts/quick_start.py
```

---

**Happy Financial Tracking! 🎉**

For support, please open an issue on GitHub or contact the development team. 