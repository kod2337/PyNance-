"""
AI Service for Finance Tracker
Integrates Google Gemini AI for smart transaction processing and financial insights
"""

import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date
import google.generativeai as genai
from colorama import Fore, Style

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass

class AIService:
    """Service for AI-powered financial features using Google Gemini"""
    
    def __init__(self):
        self.model = None
        self.is_initialized = False
        self._initialize_gemini()
        
        # Predefined categories for better consistency
        self.categories = {
            'food': ['Food & Dining', 'Groceries', 'Restaurants', 'Coffee', 'Takeout'],
            'transport': ['Transportation', 'Gas', 'Public Transit', 'Uber/Taxi', 'Parking'],
            'shopping': ['Shopping', 'Clothing', 'Electronics', 'Home & Garden', 'Personal Care'],
            'entertainment': ['Entertainment', 'Movies', 'Gaming', 'Streaming', 'Books'],
            'bills': ['Bills & Utilities', 'Rent', 'Internet', 'Phone', 'Insurance'],
            'health': ['Healthcare', 'Pharmacy', 'Fitness', 'Medical', 'Dental'],
            'income': ['Salary', 'Bonus', 'Freelance', 'Investment', 'Gift'],
            'other': ['Other', 'Miscellaneous', 'Cash', 'Transfer']
        }
    
    def _initialize_gemini(self):
        """Initialize Gemini AI model"""
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                print(f"{Fore.YELLOW}⚠️  GEMINI_API_KEY not found. AI features will be disabled.")
                return
            
            genai.configure(api_key=api_key)
            
            # Use the latest available Gemini model
            # gemini-2.0-flash-thinking-exp is the current available model
            model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-thinking-exp')
            
            try:
                self.model = genai.GenerativeModel(model_name)
                self.is_initialized = True
                print(f"{Fore.GREEN}🤖 Gemini AI initialized successfully with model: {model_name}!")
            except Exception as model_error:
                # Fallback to other available models
                fallback_models = [
                    'gemini-2.0-flash-thinking-exp',
                    'gemini-1.5-flash',
                    'gemini-1.5-pro',
                    'gemini-pro'
                ]
                
                for fallback_model in fallback_models:
                    try:
                        self.model = genai.GenerativeModel(fallback_model)
                        self.is_initialized = True
                        print(f"{Fore.GREEN}🤖 Gemini AI initialized with fallback model: {fallback_model}!")
                        return
                    except:
                        continue
                
                # If all models fail, raise the original error
                raise model_error
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error initializing Gemini AI: {str(e)}")
            print(f"{Fore.YELLOW}💡 Try checking your API key or model availability")
            self.is_initialized = False
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.is_initialized and self.model is not None
    
    def categorize_transaction(self, description: str, amount: float, 
                             user_history: Optional[List[Dict]] = None) -> str:
        """
        Automatically categorize a transaction based on description and context
        
        Args:
            description: Transaction description
            amount: Transaction amount
            user_history: Optional user transaction history for pattern learning
            
        Returns:
            Suggested category
        """
        if not self.is_available():
            return self._fallback_categorization(description, amount)
        
        try:
            # Build context from user history
            context = ""
            if user_history:
                recent_patterns = self._extract_categorization_patterns(user_history)
                context = f"User's recent categorization patterns: {recent_patterns}\n"
            
            # Create prompt for categorization
            prompt = f"""
            {context}
            Based on the transaction description and amount, suggest the most appropriate category.
            
            Transaction: "{description}"
            Amount: ${abs(amount):.2f}
            Type: {"Expense" if amount < 0 else "Income"}
            
            Available categories:
            Food & Dining, Groceries, Transportation, Shopping, Entertainment, Bills & Utilities,
            Healthcare, Salary, Freelance, Investment, Other
            
            Respond with ONLY the category name, nothing else.
            """
            
            response = self.model.generate_content(prompt)
            category = response.text.strip()
            
            # Validate and normalize category
            return self._normalize_category(category)
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  AI categorization failed: {str(e)}")
            return self._fallback_categorization(description, amount)
    
    def parse_natural_language_transaction(self, text: str) -> Dict[str, Any]:
        """
        Parse natural language input into transaction components
        
        Args:
            text: Natural language transaction description
            
        Returns:
            Dictionary with parsed transaction data
        """
        if not self.is_available():
            return self._fallback_parsing(text)
        
        try:
            prompt = f"""
            Parse this natural language transaction into structured data:
            "{text}"
            
            Extract and return ONLY a JSON object with these fields:
            - "description": Clear description of the transaction
            - "amount": Numeric amount (positive for income, negative for expenses)
            - "category": Most appropriate category
            - "date": Date in YYYY-MM-DD format (use today if not specified)
            - "type": Either "Income" or "Expense"
            
            Examples:
            "I spent $25 on groceries at Walmart yesterday" -> 
            {{"description": "Groceries at Walmart", "amount": -25.0, "category": "Groceries", "date": "2024-01-15", "type": "Expense"}}
            
            "Got paid $500 for freelance work" ->
            {{"description": "Freelance work payment", "amount": 500.0, "category": "Freelance", "date": "2024-01-16", "type": "Income"}}
            
            Return ONLY the JSON object, no additional text.
            """
            
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())
            
            # Validate and normalize the result
            return self._validate_parsed_transaction(result)
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  AI parsing failed: {str(e)}")
            return self._fallback_parsing(text)
    
    def generate_financial_insights(self, transactions: List[Dict[str, Any]], 
                                  current_balance: float) -> Dict[str, Any]:
        """
        Generate AI-powered financial insights and recommendations
        
        Args:
            transactions: List of user transactions
            current_balance: Current account balance
            
        Returns:
            Dictionary with insights and recommendations
        """
        if not self.is_available() or not transactions:
            return self._fallback_insights(transactions, current_balance)
        
        try:
            # Prepare transaction summary for AI
            summary = self._prepare_transaction_summary(transactions)
            
            # Create a simpler, more reliable prompt
            prompt = f"""
            Analyze this financial data and provide insights in JSON format:
            
            {summary}
            
            Return a JSON object with exactly these keys:
            - "spending_patterns": brief description of spending patterns
            - "budget_recommendations": one specific budget recommendation  
            - "savings_tips": one practical savings tip
            - "anomalies": any unusual patterns or "None detected"
            - "monthly_trend": spending trend description
            - "top_categories": list of top 3 spending categories
            
            Keep responses brief and actionable. Return only valid JSON.
            """
            
            # Try to get response with retry logic
            for attempt in range(3):
                try:
                    print(f"{Fore.CYAN}🔍 Debug: AI insights attempt {attempt + 1}")
                    response = self.model.generate_content(prompt)
                    
                    if not response or not response.text:
                        print(f"{Fore.YELLOW}⚠️  Empty response from AI (attempt {attempt + 1})")
                        continue
                    
                    response_text = response.text.strip()
                    print(f"{Fore.CYAN}🔍 Debug: AI response length: {len(response_text)}")
                    
                    # Try to extract JSON if response has extra text
                    if response_text.startswith('```'):
                        # Extract JSON from code block
                        json_start = response_text.find('{')
                        json_end = response_text.rfind('}') + 1
                        if json_start != -1 and json_end > json_start:
                            response_text = response_text[json_start:json_end]
                    
                    insights = json.loads(response_text)
                    print(f"{Fore.GREEN}✅ Successfully parsed AI insights")
                    return self._validate_insights(insights)
                    
                except json.JSONDecodeError as e:
                    print(f"{Fore.YELLOW}⚠️  JSON parsing failed (attempt {attempt + 1}): {e}")
                    if attempt == 2:  # Last attempt
                        break
                    continue
                except Exception as e:
                    print(f"{Fore.YELLOW}⚠️  AI request failed (attempt {attempt + 1}): {e}")
                    if attempt == 2:  # Last attempt
                        break
                    continue
            
            # If all attempts failed, return fallback
            print(f"{Fore.YELLOW}⚠️  All AI attempts failed, using fallback insights")
            return self._fallback_insights(transactions, current_balance)
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  AI insights generation failed: {str(e)}")
            return self._fallback_insights(transactions, current_balance)
    
    def generate_expense_report(self, transactions: List[Dict[str, Any]], 
                              period: str = "monthly") -> str:
        """
        Generate AI-powered expense report with summaries
        
        Args:
            transactions: List of transactions
            period: Report period ("monthly", "weekly", "yearly")
            
        Returns:
            Formatted expense report
        """
        if not self.is_available() or not transactions:
            return self._fallback_report(transactions, period)
        
        try:
            # Filter transactions by period
            filtered_transactions = self._filter_by_period(transactions, period)
            
            if not filtered_transactions:
                print(f"{Fore.YELLOW}⚠️  No transactions found for {period} period, using fallback")
                return self._fallback_report(transactions, period)
            
            summary = self._prepare_transaction_summary(filtered_transactions)
            
            # Create a simpler, more reliable prompt
            prompt = f"""
            Create a {period} expense report based on this financial data:
            
            {summary}
            
            Write a professional report with:
            1. Brief executive summary (2-3 sentences)
            2. Income vs expenses totals
            3. Top spending categories 
            4. Key insights
            5. Simple recommendations
            
            Make it clear and concise. Do not use JSON format.
            """
            
            # Try to generate report with retry logic
            for attempt in range(3):
                try:
                    print(f"{Fore.CYAN}🔍 Debug: AI report attempt {attempt + 1}")
                    response = self.model.generate_content(prompt)
                    
                    if not response or not response.text:
                        print(f"{Fore.YELLOW}⚠️  Empty response from AI (attempt {attempt + 1})")
                        continue
                    
                    report_text = response.text.strip()
                    print(f"{Fore.CYAN}🔍 Debug: AI report length: {len(report_text)}")
                    
                    if len(report_text) > 50:  # Basic validation
                        return self._format_report(report_text, period)
                    else:
                        print(f"{Fore.YELLOW}⚠️  Report too short (attempt {attempt + 1})")
                        continue
                        
                except Exception as e:
                    print(f"{Fore.YELLOW}⚠️  AI report request failed (attempt {attempt + 1}): {e}")
                    if attempt == 2:  # Last attempt
                        break
                    continue
            
            # If all attempts failed, return fallback
            print(f"{Fore.YELLOW}⚠️  All AI report attempts failed, using fallback")
            return self._fallback_report(filtered_transactions, period)
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  AI report generation failed: {str(e)}")
            return self._fallback_report(transactions, period)
    
    def list_available_models(self):
        """List available Gemini models for debugging"""
        try:
            if not os.getenv('GEMINI_API_KEY'):
                print(f"{Fore.YELLOW}⚠️  GEMINI_API_KEY not found.")
                return []
            
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            
            print(f"{Fore.CYAN}🔍 Available Gemini models:")
            models = []
            for model in genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    models.append(model.name)
                    print(f"   ✅ {model.name}")
            
            return models
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error listing models: {str(e)}")
            return []
    
    # Helper methods
    def _fallback_categorization(self, description: str, amount: float) -> str:
        """Fallback categorization when AI is unavailable"""
        description_lower = description.lower()
        
        # Simple keyword-based categorization
        if any(word in description_lower for word in ['grocery', 'food', 'restaurant', 'cafe']):
            return "Food & Dining"
        elif any(word in description_lower for word in ['gas', 'uber', 'taxi', 'transport']):
            return "Transportation"
        elif any(word in description_lower for word in ['rent', 'utility', 'bill', 'insurance']):
            return "Bills & Utilities"
        elif amount > 0:
            return "Income"
        else:
            return "Other"
    
    def _fallback_parsing(self, text: str) -> Dict[str, Any]:
        """Fallback parsing when AI is unavailable"""
        # Simple regex-based parsing
        amount_match = re.search(r'\$?(\d+(?:\.\d{2})?)', text)
        amount = float(amount_match.group(1)) if amount_match else 0.0
        
        # Determine if it's an expense or income
        expense_keywords = ['spend', 'spent', 'paid', 'bought', 'cost']
        income_keywords = ['earn', 'earned', 'paid', 'received', 'got']
        
        text_lower = text.lower()
        is_expense = any(word in text_lower for word in expense_keywords)
        is_income = any(word in text_lower for word in income_keywords)
        
        if is_expense:
            amount = -abs(amount)
            transaction_type = "Expense"
        elif is_income:
            amount = abs(amount)
            transaction_type = "Income"
        else:
            transaction_type = "Expense" if amount > 0 else "Income"
        
        return {
            "description": text[:50],
            "amount": amount,
            "category": self._fallback_categorization(text, amount),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": transaction_type
        }
    
    def _normalize_category(self, category: str) -> str:
        """Normalize AI-suggested category to predefined categories"""
        category_lower = category.lower()
        
        for main_cat, sub_cats in self.categories.items():
            if any(sub_cat.lower() in category_lower or category_lower in sub_cat.lower() 
                   for sub_cat in sub_cats):
                return sub_cats[0]  # Return primary category name
        
        return "Other"
    
    def _extract_categorization_patterns(self, history: List[Dict]) -> str:
        """Extract user's categorization patterns from history"""
        patterns = {}
        for transaction in history[-20:]:  # Last 20 transactions
            desc = transaction.get('description', '').lower()
            category = transaction.get('category', '')
            if desc and category:
                patterns[desc] = category
        
        return str(patterns)[:500]  # Limit context size
    
    def _validate_parsed_transaction(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize parsed transaction data"""
        # Ensure required fields exist
        required_fields = ['description', 'amount', 'category', 'date', 'type']
        for field in required_fields:
            if field not in result:
                result[field] = ""
        
        # Normalize amount
        try:
            result['amount'] = float(result['amount'])
        except (ValueError, TypeError):
            result['amount'] = 0.0
        
        # Normalize date
        try:
            parsed_date = parse_date(result['date'])
            result['date'] = parsed_date.strftime("%Y-%m-%d")
        except:
            result['date'] = datetime.now().strftime("%Y-%m-%d")
        
        # Normalize category
        result['category'] = self._normalize_category(result['category'])
        
        return result
    
    def _prepare_transaction_summary(self, transactions: List[Dict[str, Any]]) -> str:
        """Prepare transaction summary for AI analysis"""
        if not transactions:
            return "No transactions available"
        
        print(f"{Fore.CYAN}🔍 Debug: Processing {len(transactions)} transactions...")
        
        # Calculate basic statistics
        total_income = 0.0
        total_expenses = 0.0
        
        for t in transactions:
            try:
                # Handle different possible key names from Google Sheets
                amount_key = 'Amount' if 'Amount' in t else 'amount'
                amount = float(t.get(amount_key, 0))
                
                if amount > 0:
                    total_income += amount
                else:
                    total_expenses += abs(amount)
                    
            except (ValueError, TypeError) as e:
                print(f"{Fore.YELLOW}⚠️  Skipping invalid amount: {t.get('Amount', 'N/A')} - {e}")
                continue
        
        print(f"{Fore.CYAN}🔍 Debug: Income=${total_income:.2f}, Expenses=${total_expenses:.2f}")
        
        # Category breakdown
        category_totals = {}
        for transaction in transactions:
            try:
                category_key = 'Category' if 'Category' in transaction else 'category'
                amount_key = 'Amount' if 'Amount' in transaction else 'amount'
                
                category = transaction.get(category_key, 'Other')
                amount = float(transaction.get(amount_key, 0))
                
                # Only count expenses for category analysis (negative amounts)
                if amount < 0:
                    abs_amount = abs(amount)
                    category_totals[category] = category_totals.get(category, 0) + abs_amount
                    
            except (ValueError, TypeError):
                continue
        
        # Recent transactions (last 10)
        recent = transactions[-10:] if len(transactions) > 10 else transactions
        
        summary = {
            'total_transactions': len(transactions),
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_amount': total_income - total_expenses,
            'top_categories': dict(sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]),
            'recent_transactions': [
                {
                    'description': t.get('Description', t.get('description', '')),
                    'amount': float(t.get('Amount', t.get('amount', 0))),
                    'category': t.get('Category', t.get('category', ''))
                } for t in recent
            ]
        }
        
        print(f"{Fore.CYAN}🔍 Debug: Summary prepared with {summary['total_transactions']} transactions")
        return json.dumps(summary, indent=2)
    
    def _validate_insights(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and ensure insights have required structure"""
        required_keys = [
            'spending_patterns', 'budget_recommendations', 'savings_tips',
            'anomalies', 'monthly_trend', 'top_categories'
        ]
        
        for key in required_keys:
            if key not in insights:
                insights[key] = f"No {key.replace('_', ' ')} analysis available"
        
        return insights
    
    def _filter_by_period(self, transactions: List[Dict[str, Any]], period: str) -> List[Dict[str, Any]]:
        """Filter transactions by time period"""
        if not transactions:
            return []
            
        now = datetime.now()
        
        if period == "weekly":
            cutoff = now - timedelta(days=7)
        elif period == "monthly":
            cutoff = now - timedelta(days=30)
        elif period == "yearly":
            cutoff = now - timedelta(days=365)
        else:
            # If period is invalid, return all transactions
            print(f"{Fore.CYAN}🔍 Debug: Invalid period '{period}', returning all transactions")
            return transactions
        
        print(f"{Fore.CYAN}🔍 Debug: Filtering {len(transactions)} transactions for {period} period (cutoff: {cutoff.strftime('%Y-%m-%d')})")
        
        filtered = []
        for transaction in transactions:
            try:
                # Handle different possible key names from Google Sheets
                date_key = 'Date' if 'Date' in transaction else 'date'
                date_str = transaction.get(date_key, '')
                
                if not date_str:
                    print(f"{Fore.YELLOW}⚠️  Skipping transaction with no date")
                    continue
                
                # Parse date - handle various formats
                if isinstance(date_str, str):
                    # Try to parse the date string
                    trans_date = parse_date(date_str)
                else:
                    # If it's already a datetime object
                    trans_date = date_str
                
                # Compare dates (remove timezone for comparison)
                if hasattr(trans_date, 'replace'):
                    trans_date = trans_date.replace(tzinfo=None)
                
                if trans_date >= cutoff:
                    filtered.append(transaction)
                    
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️  Skipping transaction with invalid date '{transaction.get('Date', 'N/A')}': {e}")
                # For debugging, include recent transactions even with date issues
                if period in ["weekly", "monthly"]:
                    filtered.append(transaction)
                continue
        
        print(f"{Fore.CYAN}🔍 Debug: Filtered to {len(filtered)} transactions for {period} period")
        
        # If no transactions match the period but we have transactions, 
        # return recent ones anyway (they might be recent but date parsing failed)
        if not filtered and transactions and period in ["weekly", "monthly"]:
            print(f"{Fore.YELLOW}⚠️  No transactions matched {period} filter, returning recent transactions anyway")
            filtered = transactions[-10:] if len(transactions) > 10 else transactions
        
        return filtered
    
    def _format_report(self, report: str, period: str) -> str:
        """Format the AI-generated report"""
        header = f"""
{Fore.CYAN}{'='*60}
{f'{period.upper()} FINANCIAL REPORT':^60}
{f'Generated on {datetime.now().strftime("%Y-%m-%d %H:%M")}':^60}
{'='*60}{Style.RESET_ALL}

"""
        return header + report
    
    def _fallback_insights(self, transactions: List[Dict[str, Any]], 
                          current_balance: float) -> Dict[str, Any]:
        """Fallback insights when AI is unavailable"""
        if not transactions:
            return {
                'spending_patterns': "No transaction data available",
                'budget_recommendations': "Add transactions to get recommendations",
                'savings_tips': "Track your expenses to receive personalized tips",
                'anomalies': "No anomalies detected",
                'monthly_trend': "Insufficient data",
                'top_categories': []
            }
        
        # Basic analysis with real data
        total_income = 0.0
        total_expenses = 0.0
        category_totals = {}
        
        for t in transactions:
            try:
                amount_key = 'Amount' if 'Amount' in t else 'amount'
                category_key = 'Category' if 'Category' in t else 'category'
                
                amount = float(t.get(amount_key, 0))
                category = t.get(category_key, 'Other')
                
                if amount > 0:
                    total_income += amount
                else:
                    total_expenses += abs(amount)
                    # Track expense categories
                    category_totals[category] = category_totals.get(category, 0) + abs(amount)
                    
            except (ValueError, TypeError):
                continue
        
        avg_expense = total_expenses / len([t for t in transactions if float(t.get('Amount', t.get('amount', 0))) < 0]) if transactions else 0
        net_amount = total_income - total_expenses
        
        # Get top categories
        top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:3]
        top_cat_list = [f"{cat}: ${amt:.2f}" for cat, amt in top_categories]
        
        return {
            'spending_patterns': f"Total: ${total_expenses:.2f} expenses, ${total_income:.2f} income. Average expense: ${avg_expense:.2f}",
            'budget_recommendations': f"Current net: ${net_amount:.2f}. {'Consider reducing expenses' if net_amount < 0 else 'Good financial position'}",
            'savings_tips': f"You have {len(transactions)} transactions recorded. {'Focus on reducing top spending categories' if category_totals else 'Continue tracking expenses'}",
            'anomalies': "Enable AI features for detailed anomaly detection",
            'monthly_trend': f"{'Positive trend' if net_amount > 0 else 'Negative trend'} - Net amount: ${net_amount:.2f}",
            'top_categories': top_cat_list
        }
    
    def _fallback_report(self, transactions: List[Dict[str, Any]], period: str) -> str:
        """Fallback report when AI is unavailable"""
        if not transactions:
            return f"No transactions available for {period} report."
        
        total_income = sum(float(t.get('amount', 0)) for t in transactions if float(t.get('amount', 0)) > 0)
        total_expenses = sum(abs(float(t.get('amount', 0))) for t in transactions if float(t.get('amount', 0)) < 0)
        
        return f"""
{period.upper()} FINANCIAL REPORT
Generated on {datetime.now().strftime("%Y-%m-%d")}

Summary:
- Total Income: ${total_income:.2f}
- Total Expenses: ${total_expenses:.2f}
- Net Amount: ${total_income - total_expenses:.2f}
- Transactions: {len(transactions)}

Enable AI features for detailed analysis and recommendations.
"""


def get_ai_service() -> AIService:
    """Get singleton AI service instance"""
    if not hasattr(get_ai_service, '_instance'):
        get_ai_service._instance = AIService()
    return get_ai_service._instance 